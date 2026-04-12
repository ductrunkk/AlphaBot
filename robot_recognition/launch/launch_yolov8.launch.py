from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Create a reference to the Argument
    use_sim_time_arg = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        # 2. Declare Argument, set default_value to 'false' for Real Robot
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use real time (false) for physical robot, simulated time (true) for Gazebo'
        ),

        # 3. Launch YOLO Node
        Node(
            package='robot_recognition',
            executable='yolov8_ros2_pt.py',
            name='yolo_detector_node',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time_arg}, # Pass time config to Node
                {'model': 'yolo8nfinetune.pt'}             # Declare model
            ]
        ),
        
        Node(
            package='robot_recognition',
            executable='yolo_to_scan.py', 
            name='yolo_to_laser_scan_node',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time_arg} 
            ]
        ),
    ])