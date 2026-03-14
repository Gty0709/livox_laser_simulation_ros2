import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    # Get package paths
    pkg_share = get_package_share_directory('ros2_livox_simulation')
    
    # Process xacro file
    robot_model_path = os.path.join(pkg_share, 'urdf', 'robot_with_mid360.urdf.xacro')
    doc = xacro.process_file(robot_model_path)
    robot_desc = doc.toxml()
    
    # Save processed urdf
    robot_urdf_path = '/tmp/robot_with_mid360.urdf'
    with open(robot_urdf_path, 'w') as f:
        f.write(robot_desc)
    
    # Gazebo server
    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': ''}.items()  # Empty world
    )
    
    # Gazebo client
    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gzclient.launch.py')
        )
    )
    
    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )
    
    # Spawn robot in Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'robot_with_mid360',
            '-file', robot_urdf_path,
            '-x', '0', '-y', '0', '-z', '0'
        ],
        output='screen'
    )
    
    return LaunchDescription([
        gazebo_server,
        gazebo_client,
        robot_state_publisher,
        spawn_robot
    ])
