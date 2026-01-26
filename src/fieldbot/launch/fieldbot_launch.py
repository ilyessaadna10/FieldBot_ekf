import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            RegisterEventHandler, TimerAction)
from launch.event_handlers import OnProcessExit, OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

import xacro


def generate_launch_description():
    pkg_fieldbot = get_package_share_directory('fieldbot')
    pkg_nav2 = get_package_share_directory('nav2_bringup')
    pkg_ros_gz = get_package_share_directory('ros_gz_sim')

    # Launch Configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    world = LaunchConfiguration('world')

    urdf_file = os.path.join(pkg_fieldbot, 'urdf', 'fieldbot.urdf')
    params_file = os.path.join(pkg_fieldbot, 'params', 'fieldbot_params.yaml')
    rviz_config = os.path.join(pkg_fieldbot, 'rviz', 'fieldbot.rviz')

    # 1. PROCESS URDF
    doc = xacro.process_file(urdf_file)
    robot_desc = doc.toxml()

    # Declare Launch Arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_world = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_fieldbot, 'worlds', 'navigation_world.sdf'),
        description='Full path to Gazebo world file to load')

    # 2. START GAZEBO
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ['-r ', world]}.items(),
    )

    # 3. SPAWN ROBOT
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'field_robot', '-z', '0.5'],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # 4. ROBOT STATE PUBLISHER
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': use_sim_time}]
    )

    # 5. Simulation Interface Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/model/field_robot/pose@geometry_msgs/msg/PoseArray[gz.msgs.Pose_V',
        ],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        remappings=[
            ('/model/field_robot/pose', '/gazebo_pose'),
        ]
    )

    # 6. SPAWN CONTROLLERS
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_base_controller', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    # 7. Navigation Stack (Nav2)
    # Triggered after the diff_drive controller process starts
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'params_file': params_file,
            'use_sim_time': use_sim_time,
            'slam': 'True',
            'use_composition': 'False',
            'use_respawn': 'False',
            'autostart': 'True',
        }.items(),
    )

    # 8. Visualization (RViz)
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # Event handlers for deterministic startup logic

    # Start controllers after Gazebo/Spawn is ready
    load_joint_state = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=spawn_entity,
            on_start=[joint_state_broadcaster],
        )
    )

    load_diff_drive = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster,
            on_exit=[diff_drive_spawner],
        )
    )

    # Start Nav2 only after the base controller is ready
    load_nav2 = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=diff_drive_spawner,
            on_exit=[nav2_bringup],
        )
    )

    # Start RViz after bridge is ready
    load_rviz = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=bridge,
            on_start=[TimerAction(period=5.0, actions=[rviz])],
        )
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_world,

        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge,

        load_joint_state,
        load_diff_drive,
        load_nav2,
        load_rviz,
    ])
