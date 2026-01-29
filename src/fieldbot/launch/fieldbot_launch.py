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
        default_value=os.path.join(pkg_fieldbot, 'worlds', 'vineyard_variable.sdf'),
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
            '/camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/camera/depth_image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/camera/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/gps/fix@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat',
        ],
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        remappings=[
            ('/model/field_robot/pose', '/gazebo_pose'),
            ('/camera/image', '/camera/image_raw'),
            ('/camera/depth_image', '/camera/depth'),
            ('/camera/camera_info', '/camera/camera_info'),
            ('/camera/points', '/camera/points'),
        ]
    )

    # 6. LOCALIZATION (EKF)
    ekf_local = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node_odom',
        output='screen',
        parameters=[os.path.join(pkg_fieldbot, 'params', 'ekf.yaml'), {'use_sim_time': use_sim_time}]
    )

    ekf_global = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node_map',
        output='screen',
        parameters=[os.path.join(pkg_fieldbot, 'params', 'ekf.yaml'), {'use_sim_time': use_sim_time}],
        remappings=[('/odometry/filtered', '/odometry/global')]
    )

    navsat_transform = Node(
        package='robot_localization',
        executable='navsat_transform_node',
        name='navsat_transform',
        output='screen',
        parameters=[os.path.join(pkg_fieldbot, 'params', 'ekf.yaml'), {'use_sim_time': use_sim_time}],
        remappings=[('/gps/fix', '/gps/fix'),
                    ('/imu', '/imu'),
                    ('/odometry/filtered', '/odometry/filtered')]
    )

    # 7. SPAWN CONTROLLERS
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
            os.path.join(pkg_nav2, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'params_file': params_file,
            'use_sim_time': use_sim_time,
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

    # Nav2 will start after global localization is ready
    load_nav2 = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=ekf_global,
            on_start=[nav2_bringup],
        )
    )

    # Start RViz after bridge is ready
    load_rviz = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=bridge,
            on_start=[TimerAction(period=5.0, actions=[rviz])],
        )
    )

    # Static transform: map -> utm (identity)
    # navsat_transform publishes utm->odom, but Nav2 expects map frame
    map_to_utm_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'utm'],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_world,

        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge,
        
        ekf_local,
        ekf_global,
        navsat_transform,
        map_to_utm_tf,

        load_joint_state,
        load_diff_drive,
        load_nav2,
        load_rviz,
    ])

