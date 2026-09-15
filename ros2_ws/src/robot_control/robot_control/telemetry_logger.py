#!/usr/bin/env python3
"""Append /telemetry strings to a timestamped log file."""

from datetime import datetime
import os

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TelemetryLogger(Node):
    def __init__(self):
        super().__init__('telemetry_logger')
        self.declare_parameter('log_dir', os.path.expanduser('~/ros_logs'))
        log_dir = self.get_parameter('log_dir').get_parameter_value().string_value
        self.log_file = None

        try:
            os.makedirs(log_dir, exist_ok=True)
            stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            path = os.path.join(log_dir, f'log_{stamp}.txt')
            self.log_file = open(path, 'a', buffering=1)  # line-buffered, flush po każdej ramce
            self.get_logger().info(f'Logging telemetry to {path}')
        except OSError as exc:
            self.get_logger().error(f'Cannot open log file: {exc}')

        self.create_subscription(String, '/telemetry', self.on_telemetry, 10)

    def on_telemetry(self, msg):
        if not self.log_file:
            return
        try:
            now = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            self.log_file.write(f'[{now}] {msg.data}\n')
        except OSError as exc:
            self.get_logger().error(f'Log write failed: {exc}')

    def destroy_node(self):
        if self.log_file:
            self.log_file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = TelemetryLogger()
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
