from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import  PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import os
from pathlib import Path
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    robot_simulation_dir = get_package_share_directory("diff_robot_description")
    world_default = "~/ros_ws/src/diff_robot_simulation/worlds/maze.sdf"
    # Define launch arguments
    model_arg = DeclareLaunchArgument(
        name="model", 
        default_value = os.path.join(get_package_share_directory("diff_robot_description"), "urdf","robot", "my_robot.urdf.xacro"),
        description=" Absolute path to URDF model file"
        )
    
    sim_arg = DeclareLaunchArgument(
        name="use_sim_time",
        default_value="true",
        description= "Use Gazebo simulation time"
    )

    collision_arg = DeclareLaunchArgument(
        name="enable_collision",
        default_value="true",
        description= "Enable collision tag in the URDF model"
    )

    enable_gz_control_arg = DeclareLaunchArgument(
        name="enable_gz_control",
        default_value="true",
        description= "Enable ros2 control in URDF model for Gazebo simulation"
    )

    gz_world_arg = DeclareLaunchArgument(
        name="gz_world",
        default_value=world_default,
        description= "The path to world to be used in simulation (Gazebo)"
    )


    # Retrieve the arguments from terminal
    use_sim = LaunchConfiguration("use_sim_time")
    robot_model = LaunchConfiguration("model")
    enable_collision = LaunchConfiguration("enable_collision")
    enable_gz_control = LaunchConfiguration("enable_gz_control")
    gz_world = LaunchConfiguration("gz_world")
    
    # Set the Gz ENV VAR
    gazebo_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=[
            str(Path(robot_simulation_dir).parent.resolve())
        ]
    )
    
    # Full plain URDF robot model (converted from xacro)
    robot_description = ParameterValue(Command([
        "xacro ", 
        robot_model,
        " enable_collision:=", enable_collision,
        " enable_gz_control:=", enable_gz_control]),

        value_type=str
    )

    # Launch the node robot state pub to publish the robot states thanks to the URDF model
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description,
                    "use_sim_time": use_sim}]
    )

    # Launch the Gazebo Sim
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory("ros_gz_sim"), "launch"),
            "/gz_sim.launch.py"]
        ),
        launch_arguments=[("gz_args", [" -r -v 4 -r ", gz_world])]

    )

    # Spawn the robot from the URDF model
    gz_spawn = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=["-topic", "robot_description",
                   "-name", "my_diff_robot"]
    )

    # Launch the bridge between Ros2 & Gz to synchronize the clock and bridge all the necessary topics
    # gz_ros2_bridge = Node(
    #     package="ros_gz_bridge",
    #     executable="parameter_bridge",
    #     arguments=[
    #         "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
    #         "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan"]
    # )

    ros_gz_bridge_config_file_path = os.path.join(get_package_share_directory("diff_robot_simulation"), "config", "gz_bridge_params.yaml")
    gz_ros2_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': ros_gz_bridge_config_file_path,
        }],
        output='screen')

    return LaunchDescription([
        model_arg,
        sim_arg,
        collision_arg,
        enable_gz_control_arg,
        gz_world_arg,
        gazebo_resource_path,
        robot_state_publisher,
        gazebo,
        gz_spawn,
        gz_ros2_bridge
    ])