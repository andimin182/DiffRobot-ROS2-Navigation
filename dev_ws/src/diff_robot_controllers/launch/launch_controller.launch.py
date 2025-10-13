from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    robot_description = ParameterValue(Command(
        [
            "xacro ", 
            os.path.join(get_package_share_directory("diff_robot_description"), "urdf", "robot", "my_robot.urdf.xacro")
        ]
    ),
        value_type=str,
        )

    # Robot state publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}]
    )

    # Ros2 control node
    robot_controllers = os.path.join(get_package_share_directory("diff_robot_controllers"), "config", "robot_controllers.yaml")

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        output="screen",
        parameters=[
            {"robot_description": robot_description},
            robot_controllers
        ]
    )

    # Spawn the controllers
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
            "--param-file", robot_controllers
        ]
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
    rviz_config = os.path.join(get_package_share_directory("diff_robot_controllers"), "config", "display.rviz")

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=[
            "-d", rviz_config
        ]
    )
    return LaunchDescription([
        robot_state_publisher_node,
        ros2_control_node,
        joint_state_broadcaster_spawner,
        diff_controller_spawner,
        rviz_node,
    ])