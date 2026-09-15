#!/usr/bin/env python3
"""Bridge /joy commands to the STM32 UART protocol and republish telemetry."""

import time

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Joy
from std_msgs.msg import String
import serial


class StmBridge(Node):
    def __init__(self):
        super().__init__('stm_bridge')
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)

        self.port_name = self.get_parameter('port').get_parameter_value().string_value
        self.baud_rate = self.get_parameter('baudrate').get_parameter_value().integer_value
        self.ser = None

        self.telemetry_pub = self.create_publisher(String, '/telemetry', 10)
        # Pad publikuje Best Effort — mostek musi mieć ten sam QoS, inaczej nie złapie /joy.
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self.create_subscription(Joy, 'joy', self.joy_callback, qos)
        self.create_timer(1.0, self.ensure_connection)  # ponowne otwarcie USB po resecie Nucleo
        self.create_timer(0.01, self.read_uart)         # odczyt telemetrii ze STM32


        self.prev_lspeed = 0
        self.prev_rspeed = 0
        self.prev_hat_y = 0.0
        self.prev_btn_x = 0
        self.prev_btn_circle = 0
        self.prev_btn_triangle = 0
        self.prev_btn_square = 0

        self.get_logger().info(f'STM bridge starting on {self.port_name} @ {self.baud_rate}')
        self.connect()

    def connect(self):
        if self.ser and self.ser.is_open:
            return True
        try:
            self.ser = serial.Serial(self.port_name, self.baud_rate, timeout=0.1)
            self.get_logger().info(f'Opened {self.port_name}')
            # DTR przy otwarciu portu resetuje STM32 — czekamy, aż wróci boot.
            time.sleep(1.0)
            for _ in range(3):
                self.send_command('ready')
                time.sleep(0.5)
            return True
        except Exception as exc:
            self.get_logger().error(f'UART open failed: {exc}')
            return False

    def ensure_connection(self):
        if self.ser is None or not self.ser.is_open:
            self.connect()

    def read_uart(self):
        if not (self.ser and self.ser.is_open):
            return
        try:
            if self.ser.in_waiting <= 0:
                return
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                return
            msg = String()
            # Dopinamy aktualne zadanie z pada, bo telemetria STM ma tylko RPM kół.
            msg.data = f'{line}, {self.prev_lspeed}, {self.prev_rspeed}'
            self.telemetry_pub.publish(msg)
        except Exception:
            pass

    @staticmethod
    def map_analog_to_speed(raw_value):
        try:
            val = int(float(raw_value))
        except (TypeError, ValueError):
            return 0
        if 115 <= val <= 140:
            return 0  # martwa strefa środka gałki (osie przychodzą jako 0…255)
        speed = int((val - 127) * 0.78)  # 0…255 → ok. −100…100
        return max(-100, min(100, speed))

    def joy_callback(self, msg):
        try:
            if len(msg.axes) > 5:
                # axes[1] / axes[5] = lewy i prawy analog; * -1 bo gałka do przodu
                # dawała ujemną prędkość względem kierunku jazdy robota.
                left = self.map_analog_to_speed(msg.axes[1]) * -1
                right = self.map_analog_to_speed(msg.axes[5]) * -1
                if left != self.prev_lspeed:
                    self.send_command(f'lspeed={left}')
                    self.prev_lspeed = left
                if right != self.prev_rspeed:
                    self.send_command(f'rspeed={right}')
                    self.prev_rspeed = right

            if len(msg.buttons) >= 4:
                # Zbocze 0→1, żeby jedno wciśnięcie przełączało silnik krokowy.
                if msg.buttons[0] == 1 and self.prev_btn_x == 0:
                    self.send_command('bleft_step')
                self.prev_btn_x = msg.buttons[0]
                if msg.buttons[3] == 1 and self.prev_btn_square == 0:
                    self.send_command('bright_step')
                self.prev_btn_square = msg.buttons[3]
                if msg.buttons[2] == 1 and self.prev_btn_triangle == 0:
                    self.send_command('fleft_step')
                self.prev_btn_triangle = msg.buttons[2]
                if msg.buttons[1] == 1 and self.prev_btn_circle == 0:
                    self.send_command('fright_step')
                self.prev_btn_circle = msg.buttons[1]

            if len(msg.axes) > 7:
                hat = msg.axes[7]  # D-pad góra/dół
                if hat != self.prev_hat_y:
                    if hat == 1.0:
                        self.send_command('forward')
                    elif hat == -1.0:
                        self.send_command('backward')
                    elif hat == 0.0:
                        self.send_command('stop')
                    self.prev_hat_y = hat
        except Exception as exc:
            self.get_logger().error(f'Joy callback failed: {exc}')

    def send_command(self, command):
        if not (self.ser and self.ser.is_open):
            return
        try:
            self.ser.write((command + '\n').encode('utf-8'))
        except Exception as exc:
            self.get_logger().error(f'UART write failed: {exc}')

    def destroy_node(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = StmBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
