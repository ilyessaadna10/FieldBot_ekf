import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_fieldbot = get_package_share_directory('fieldbot')
    
    # Default map file location (workspace root)
    map_file_path = os.path.join(os.getcwd(), 'field_map.yaml')

    row_surveyor = Node(
        package='fieldbot',
        executable='row_surveyor.py',
        name='row_surveyor',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'map_file': map_file_path
        }]
    )

    tree_navigator = Node(
        package='fieldbot',
        executable='tree_navigator.py',
        name='tree_navigator',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'map_file': map_file_path
        }]
    )

    survey_gui = Node(
        package='fieldbot',
        executable='survey_gui.py',
        name='survey_gui',
        output='screen'
    )

    return LaunchDescription([
        row_surveyor,
        tree_navigator,
        survey_gui
    ])
