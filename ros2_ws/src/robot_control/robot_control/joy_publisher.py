#!/usr/bin/env python3
"""Publish a DualShock-style gamepad as sensor_msgs/Joy."""

from inputs import get_gamepad
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy

CONTROLLER_INPUT_MAP = {
    'ABS_X': 0, 'ABS_Y': 0, 'ABS_Z': 0, 'ABS_RX': 0, 'ABS_RY': 0, 'ABS_RZ': 0,
    'ABS_HAT0X': 0, 'ABS_HAT0Y': 0,
    'BTN_SOUTH': 0, 'BTN_WEST': 0, 'BTN_EAST': 0, 'BTN_NORTH': 0,
    'BTN_TL': 0, 'BTN_TR': 0,
    'BTN_THUMBL': 0, 'BTN_THUMBR': 0,
    'BTN_START': 0, 'BTN_SELECT': 0,
}


class JoyPublisher(Node):
    def __init__(self):
        super().__init__('joy_publisher')
        self.publisher = self.create_publisher(Joy, 'joy', 10)
        self.controller_input = CONTROLLER_INPUT_MAP.copy()
        self.joy_msg = Joy()
        self.joy_msg.header.frame_id = 'joy_link'
        self.joy_msg.axes = [0.0] * 8
        self.joy_msg.buttons = [0] * 10
        self.create_timer(0.01, self.read_and_publish)
        # get_gamepad() jest blokujące — timer tylko utrzymuje spin ROS.

        self.get_logger().info('Publishing gamepad on /joy')

    def gamepad_update(self):
        for event in get_gamepad():
            if event.code in self.controller_input:
                self.controller_input[event.code] = event.state

    def map_and_publish(self):
        self.joy_msg.header.stamp = self.get_clock().now().to_msg()
        inp = self.controller_input
        self.joy_msg.axes[0] = inp['ABS_X']
        self.joy_msg.axes[1] = inp['ABS_Y']
        self.joy_msg.axes[2] = inp['ABS_Z']
        self.joy_msg.axes[3] = inp['ABS_RX']
        self.joy_msg.axes[4] = inp['ABS_RY']
        self.joy_msg.axes[5] = inp['ABS_RZ']
        self.joy_msg.axes[6] = float(inp['ABS_HAT0X'])
        self.joy_msg.axes[7] = float(inp['ABS_HAT0Y']) * -1.0  # góra pada = +1
        # Przyciski: 0=X/A, 1=O/B, 2=trójkąt/X, 3=kwadrat/Y (mapowanie DualShock).
        self.joy_msg.buttons[0] = inp['BTN_SOUTH']
        self.joy_msg.buttons[1] = inp['BTN_WEST']
        self.joy_msg.buttons[2] = inp['BTN_NORTH']
        self.joy_msg.buttons[3] = inp['BTN_EAST']
        self.joy_msg.buttons[4] = inp['BTN_TL']
        self.joy_msg.buttons[5] = inp['BTN_TR']
        self.joy_msg.buttons[6] = inp['BTN_THUMBL']
        self.joy_msg.buttons[7] = inp['BTN_THUMBR']
        self.joy_msg.buttons[8] = inp['BTN_START']
        self.joy_msg.buttons[9] = inp['BTN_SELECT']
        self.publisher.publish(self.joy_msg)

    def read_and_publish(self):
        try:
            self.gamepad_update()
            self.map_and_publish()
        except Exception as exc:
            self.get_logger().error(f'Gamepad read failed: {exc}')
            self.destroy_node()
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = JoyPublisher()
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
