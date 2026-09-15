from glob import glob
import os

from setuptools import setup

package_name = 'robot_control'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools', 'pyserial', 'inputs'],
    zip_safe=True,
    maintainer='Błażej Kruszka',
    maintainer_email='b.kruszka02@gmail.com',
    description='Gamepad, UART bridge and telemetry logger for the tracked mobile robot.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'joy_publisher = robot_control.joy_publisher:main',
            'stm_bridge = robot_control.stm_bridge:main',
            'telemetry_logger = robot_control.telemetry_logger:main',
        ],
    },
)
