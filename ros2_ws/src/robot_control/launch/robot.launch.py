from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='robot_control',
            executable='joy_publisher',
            name='joy_publisher',
            output='screen',
        ),
        Node(
            package='robot_control',
            executable='stm_bridge',
            name='stm_bridge',
            output='screen',
            parameters=[{
                'port': '/dev/ttyACM0',
                'baudrate': 115200,
            }],
        ),
        Node(
            package='robot_control',
            executable='telemetry_logger',
            name='telemetry_logger',
            output='screen',
        ),
    ])
