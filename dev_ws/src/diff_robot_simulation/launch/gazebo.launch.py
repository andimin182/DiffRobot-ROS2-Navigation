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
    # Define some arg
    model_arg = DeclareLaunchArgument(
        name="model", 
        default_value = os.path.join(get_package_share_directory("diff_robot_description"), "urdf","robot", "my_robot.urdf.xacro"),
        description=" Absolute path to URDF model file"
        )
    
    sim_arg = DeclareLaunchArgument(
        name="use_sim",
        default_value="true",
        description= "Use simulation time flag"
    )

    collision_arg = DeclareLaunchArgument(
        name="enable_collision",
        default_value="true",
        description= "Enable collision tag"
    )

    use_sim = LaunchConfiguration("use_sim")
    enable_collision = LaunchConfiguration("enable_collision")
    
    gazebo_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=[
            str(Path(robot_simulation_dir).parent.resolve())
        ]
    )
    
    # Full plain URDF robot model (converted from xacro)
    robot_description = ParameterValue(Command([
        "xacro ", 
        LaunchConfiguration("model"),
        " enable_collision:=", enable_collision]),

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
        launch_arguments=[("gz_args", [" -r -v 4 -r ~/ros_ws/src/diff_robot_simulation/worlds/maze.sdf"])]

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
    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan"]
    )

    return LaunchDescription([
        model_arg,
        sim_arg,
        collision_arg,
        gazebo_resource_path,
        robot_state_publisher,
        gazebo,
        gz_spawn,
        gz_ros2_bridge
    ])