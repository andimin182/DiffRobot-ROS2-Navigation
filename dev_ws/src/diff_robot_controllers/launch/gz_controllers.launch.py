from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition



import os


def generate_launch_description():
    rviz_config_default = os.path.join(get_package_share_directory("diff_robot_controllers"), "config", "display.rviz")
    robot_controllers = os.path.join(get_package_share_directory("diff_robot_controllers"), "config", "robot_controllers.yaml")                                                                             
    
    # Define terminal argument to launch rviz
    launch_rviz_arg = DeclareLaunchArgument(
        name="launch_rviz",
        default_value="true",
        description= "Launch RViz application"
    )

    use_sim_time_arg = DeclareLaunchArgument(
        name="use_sim_time",
        default_value="false",
        description= "Use simulation (Gazebo) clock"
    )

    rviz_config_arg = DeclareLaunchArgument(
        name="rviz_config",
        default_value=rviz_config_default,
        description= "Path to Rviz config file"
    )

    launch_rviz = LaunchConfiguration("launch_rviz")
    use_sim_time = LaunchConfiguration("use_sim_time")
    rviz_config = LaunchConfiguration("rviz_config")

    # Spawn the controllers
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
            "--param-file", robot_controllers
        ],
        output="screen",
    )

    diff_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_controller",
            "--controller-manager",
            "/controller_manager",
            "--param-file", robot_controllers
        ]
    )

    # RViz
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
            "-d", rviz_config
        ],
        condition = IfCondition(launch_rviz)
    )
    return LaunchDescription([
        launch_rviz_arg,
        use_sim_time_arg,
        rviz_config_arg,
        joint_state_broadcaster_spawner,
        diff_controller_spawner,
        rviz_node,
    ])