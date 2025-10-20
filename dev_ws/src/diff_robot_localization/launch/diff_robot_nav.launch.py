#!/usr/bin/env python3
"""
Launch Nav2 for the diff drive robot in Gazebo.
 
This launch file sets up a complete ROS 2 navigation environment.
 
:author: Andi Mindru
:date: October 16, 2025
"""
 
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition

 
def generate_launch_description():
    """
    Generate a launch description.
 
    Returns:
        LaunchDescription: A complete launch description for the robot.
    """
    # Constants for paths to different packages
    package_name_gazebo = 'diff_robot_simulation'
    package_name_localization = 'diff_robot_localization'
    package_name_control = 'diff_robot_controllers'
    package_name_nav = 'diff_robot_nav'
 
    # Launch and config file paths
    gazebo_launch_file_path = 'launch/gazebo.launch.py'
    ekf_launch_file_path = 'launch/ekf_gz.launch.py'
    ekf_config_file_path = 'config/ekf.yaml'
    controllers_launch_file = 'launch/gz_controllers.launch.py'
    nav_params_file = 'config/diff_robot_default_params.yaml'
    map_name = 'maps/maze.yaml'
 
    # Set the path to different packages
    pkg_share_gazebo = FindPackageShare(package=package_name_gazebo).find(package_name_gazebo)
    pkg_share_localization = FindPackageShare(
        package=package_name_localization).find(package_name_localization)
    pkg_share_control =FindPackageShare(package=package_name_control).find(package_name_control)
    pkg_share_nav =FindPackageShare(package=package_name_nav).find(package_name_nav)
    nav2_dir = FindPackageShare(package='nav2_bringup').find('nav2_bringup')
 
    # Set default paths
    default_ekf_launch_path = os.path.join(pkg_share_localization, ekf_launch_file_path)
    default_ekf_config_path = os.path.join(pkg_share_localization, ekf_config_file_path)
    default_gazebo_launch_path = os.path.join(pkg_share_gazebo, gazebo_launch_file_path)
    controllers_launch_path = os.path.join(pkg_share_control, controllers_launch_file)
    nav2_params_path = os.path.join(pkg_share_nav, nav_params_file)
    static_map_path = os.path.join(pkg_share_nav, map_name)
    nav2_launch_dir = os.path.join(nav2_dir, 'launch')
 
    # Declare all launch arguments
    # Config and launch files
    model_cmd = DeclareLaunchArgument(
        name="model", 
        default_value = os.path.join(get_package_share_directory("diff_robot_description"), "urdf","robot", "my_robot.urdf.xacro"),
        description=" Absolute path to URDF model file"
        )
    
    sim_cmd = DeclareLaunchArgument(
        name="use_sim_time",
        default_value="true",
        description= "Use Gazebo simulation time"
    )

    collision_cmd = DeclareLaunchArgument(
        name="enable_collision",
        default_value="true",
        description= "Enable collision tag in the URDF model"
    )

    enable_gz_control_cmd = DeclareLaunchArgument(
        name="enable_gz_control",
        default_value="true",
        description= "Enable ros2 control in URDF model for Gazebo simulation"
    )

    start_ros2_controllers_cmd = DeclareLaunchArgument(
        name="start_controllers",
        default_value="true",
        description= "Enable ros2 controllers in Gazebo"
    )

    start_rviz_cmd = DeclareLaunchArgument(
        name="start_rviz",
        default_value="true",
        description= "Start RVIZ with Nav2 plugin GUI"
    )

    declare_ekf_config_file_cmd = DeclareLaunchArgument(
        name='ekf_config_file',
        default_value=default_ekf_config_path,
        description='Full path to the EKF configuration YAML file')
 
    declare_ekf_launch_file_cmd = DeclareLaunchArgument(
        name='ekf_launch_file',
        default_value=default_ekf_launch_path,
        description='Full path to the EKF launch file to use')
    
    declare_gazebo_launch_file_cmd = DeclareLaunchArgument(
        name='gazebo_launch_file',
        default_value=default_gazebo_launch_path,
        description='Full path to the Gazebo launch file to use')
 
    declare_slam_cmd = DeclareLaunchArgument(
        name='slam',
        default_value='False',
        description='Whether to run SLAM')
    
    declare_map_yaml_cmd = DeclareLaunchArgument(
        name='map',
        default_value=static_map_path,
        description='Full path to map file to load')
    
    declare_nav2_params_file_cmd = DeclareLaunchArgument(
        name='nav2_params_file',
        default_value=nav2_params_path,
        description='Full path to the ROS2 parameters file to use for navigation nodes')
 

    # Retrieve the arguments from terminal
    use_sim_time = LaunchConfiguration("use_sim_time")
    model = LaunchConfiguration("model")
    enable_collision = LaunchConfiguration("enable_collision")
    enable_gz_control = LaunchConfiguration("enable_gz_control")
    ekf_config_file = LaunchConfiguration('ekf_config_file')
    ekf_launch_file = LaunchConfiguration('ekf_launch_file')
    gazebo_launch_file = LaunchConfiguration('gazebo_launch_file')
    start_rviz = LaunchConfiguration('start_rviz')
    start_controllers = LaunchConfiguration('start_controllers')
    slam = LaunchConfiguration('slam')
    map_file = LaunchConfiguration('map')
    nav2_params_file = LaunchConfiguration('nav2_params_file')
    
    # Specify the actions
    # Start Gazebo
    start_gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([gazebo_launch_file]),
        launch_arguments={
            'model':model,
            'use_sim_time': use_sim_time,
            'enable_collision': enable_collision,
            'enable_gz_control': enable_gz_control
        }.items()
    )

    # Start Ros2 controllers
    start_controllers_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([controllers_launch_path]),
        condition=IfCondition(start_controllers),
        launch_arguments={
            'launch_rviz': start_rviz,
            'use_sim_time': use_sim_time,
        }.items()
    )
 
    # Start EKF
    start_ekf_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([ekf_launch_file]),
        launch_arguments={
            'ekf_config_file': ekf_config_file,
            'use_sim_time': use_sim_time
        }.items()
    )

    # Start the Nav2 pkg
    start_ros2_navigation_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'bringup_launch.py')),
        launch_arguments={
            'slam': slam,
            'map': map_file,
            'use_sim_time': use_sim_time,
            'params_file': nav2_params_file,
            'autostart':'true'
        }.items()
    )

    # Start the RVIZ with NAV2 plugin GUI
    # TODO: it opens rviz but it cannot be seens. Must be launched on another terminal
    # start_rviz_nav2_cmd = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'rviz_launch.py')),
    #     condition=IfCondition(start_rviz)
    # )
    # Create the launch description and populate
    ld = LaunchDescription()
 
    # Add all launch arguments
    # Config and launch files
    ld.add_action(declare_ekf_config_file_cmd)
    ld.add_action(declare_ekf_launch_file_cmd)
    ld.add_action(declare_gazebo_launch_file_cmd)
    ld.add_action(model_cmd)
    ld.add_action(sim_cmd)
    ld.add_action(collision_cmd)
    ld.add_action(enable_gz_control_cmd)
    ld.add_action(start_ros2_controllers_cmd)
    ld.add_action(start_rviz_cmd)
    ld.add_action(declare_slam_cmd)
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(declare_nav2_params_file_cmd)

    # Add any actions
    ld.add_action(start_gazebo_cmd)
    ld.add_action(start_controllers_cmd)
    ld.add_action(start_ekf_cmd)
    ld.add_action(start_ros2_navigation_cmd)
    # ld.add_action(start_rviz_nav2_cmd)

    return ld