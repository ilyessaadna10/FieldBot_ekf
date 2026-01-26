# FieldBot Bot Package

This package contains the core ROS 2 Jazzy implementation for the FieldBot Farm Robot simulation.

## Overview
`fieldbot` integrates Gazebo Harmonic with the Nav2 stack to provide a robust navigation and SLAM simulation environment.

## 📂 Subdirectories
-   **`config/`**: ROS 2 controller configurations.
-   **`docs/`**: Technical architecture and tuning guides.
-   **`include/`**: C++ headers (if applicable).
-   **`launch/`**: Event-driven Python launch files.
-   **`maps/`**: Saved SLAM maps.
-   **`params/`**: Nav2, SLAM, and node-specific YAML parameters.
-   **`rviz/`**: Custom RViz visualization profiles.
-   **`urdf/`**: Robot physical description and sensor plugins.
-   **`worlds/`**: Gazebo world definitions.

## 🛠 Building & Running
From your workspace root:
```bash
colcon build --packages-select fieldbot
source install/setup.bash
ros2 launch fieldbot fieldbot_launch.py
```

## 🚀 Key Features
- **30Hz GPU Lidar**: Optimized for High-fidelity navigation.
- **Event-Driven Startup**: Robust node synchronization using `RegisterEventHandler`.
- **Advanced Control**: `ros2_control` integration for differential drive base.
