# Copyright (c) 2024-2025 Ziqi Fan
# SPDX-License-Identifier: Apache-2.0

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, TextSubstitution, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution

def generate_launch_description():
    rname = LaunchConfiguration("rname")

    wname = "stairs"
    robot_name = ParameterValue(Command(["echo -n ", rname]), value_type=str)
    ros_namespace = ParameterValue(Command(["echo -n ", "/", rname, "_gazebo"]), value_type=str)
    gazebo_model_name = ParameterValue(Command(["echo -n ", rname, "_gazebo"]), value_type=str)

    robot_description = ParameterValue(
        Command([
            "xacro ",
            Command(["echo -n ", Command(["ros2 pkg prefix ", rname, "_description"])]),
            "/share/", rname, "_description/xacro/robot.xacro"
        ]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description}],
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("gazebo_ros"), "launch", "gazebo.launch.py")
        ),
        launch_arguments={
            # "verbose": "true",
            # "pause": "true",  # Not Available
            "world": '/home/zetans/IsaacLab/rl_sar/gazebo_models_worlds_collection/worlds/test_zone.world',#os.path.join(get_package_share_directory("rl_sar"), "worlds", wname + ".world"),
        }.items(),
        
        # PythonLaunchDescriptionSource(
        #     PathJoinSubstitution([
        #         FindPackageShare("ros_gz_sim"),
        #         "launch",
        #         "gz_sim.launch.py"
        #     ])
        # ),
        
        # launch_arguments={
        #     "gz_args": '/home/zetans/Downloads/Warehouse/tugbot_warehouse.sdf',
        # }.items(),
    )

    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-topic", "/robot_description",
            "-entity", "robot_model",
            "-z", "1.0",
        ],
        output="screen",
    )
    # spawn_entity = Node(
    #     package="ros_gz_sim",
    #     executable="create",
    #     arguments=[
    #         "-name", "robot_model",
    #         "-topic", "/robot_description",
    #         "-z", "1.0",
    #     ],
    #     output="screen",
    # )
    joint_state_broadcaster_node = Node(
        package="controller_manager",
        executable='spawner.py' if os.environ.get('ROS_DISTRO', '') == 'foxy' else 'spawner',
        arguments=["joint_state_broadcaster"],
        output="screen",
    )

    robot_joint_controller_node = Node(
        package="controller_manager",
        executable='spawner.py' if os.environ.get('ROS_DISTRO', '') == 'foxy' else 'spawner',
        arguments=["robot_joint_controller"],
        output="screen",
    )

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen',
        parameters=[{
            'deadzone': 0.1,
            'autorepeat_rate': 0.0,
        }],
    )

    param_node = Node(
        package="demo_nodes_cpp",
        executable="parameter_blackboard",
        name="param_node",
        parameters=[{
            "robot_name": robot_name,
            "gazebo_model_name": gazebo_model_name,
        }],
    )

    rviz_config = PathJoinSubstitution([
        FindPackageShare("rl_sar"),
        "rviz",
        "go2w.rviz"
    ])

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config],
        parameters=[{"use_sim_time": True}],
        # If you want RViz under the robot namespace, uncomment:
        # namespace=ros_namespace,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "rname",
            description="Robot name (e.g., a1, go2)",
            default_value=TextSubstitution(text=""),
        ),
        robot_state_publisher_node,
        gazebo,
        spawn_entity,
        joint_state_broadcaster_node,
        # robot_joint_controller_node,  # Spawn in rl_sim.cpp
        joy_node,
        param_node,
        rviz_node,
    ])
