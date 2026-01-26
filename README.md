# FieldBot: Autonomous Farm Navigation Stack
in ROS 2 Jazzy

Welcome to the **FieldBot Robot** project. This repository contains the complete software stack for a differential drive robot utilizing **Nav2**, **SLAM Toolbox**, and **Gazebo Harmonic**.

The project is designed with a professional, modular architecture, adhering to Senior-level ROS 2 development standards including event-driven launch sequences and safety-critical monitoring loops.

---

## 🚀 Features

-   **Autonomous Navigation**: Full Nav2 stack integration using the Regulated Pure Pursuit (RPP) controller.
-   **Dynamic Mapping**: Synchronous SLAM utilizing `slam_toolbox` for real-time environment discovery.
-   **Simulation Ready**: High-fidelity simulation in **Gazebo Harmonic** with GPU-accelerated Lidar (optimized at 30Hz).
-   **Safety First**: Dedicated `collision_monitor` node acting as a low-latency safety reflex layer.
-   **Deterministic Launch**: Event-driven node initialization (using `RegisterEventHandler`) to ensure reliable synchronization between Gazebo and ROS 2.

---

## 🛠️ Tech Stack

-   **OS**: Ubuntu 24.04 (Noble)
-   **ROS 2**: Jazzy Jalisco
-   **Simulator**: Gazebo Harmonic
-   **Hardware Control**: `ros2_control` via `gz_ros2_control` plugin.

---

## 📂 Project Structure

```text
fieldbot_ws/
├── src/
│   └── fieldbot/
│       ├── docs/        # Formal technical documentation
│       ├── launch/      # Deterministic launch sequences
│       ├── params/      # Nav2 and SLAM configurations
│       ├── urdf/        # Robot modeling and physical links
│       └── worlds/      # Simulation environments
└── README.md
```

---

## ⚡ Quick Start

### 1. Requirements
Ensure you have ROS 2 Jazzy and Gazebo Harmonic installed.

### 2. Build the Workspace
```bash
cd fieldbot_ws
colcon build --symlink-install
source install/setup.bash
```

### 3. Launch Simulation & Navigation
```bash
ros2 launch fieldbot fieldbot_launch.py
```

---

## 📖 Documentation
Detailed technical specifications are available in the [docs](./src/fieldbot/docs/) directory:
- [System Topology](./src/fieldbot/docs/topology.md)
- [Data Pipeline](./src/fieldbot/docs/data_flow.md)
- [Navigation Tuning](./src/fieldbot/docs/tuning_guide.md)
- [Launch Architecture](./src/fieldbot/docs/launch_architecture.md)

---

## 🛡️ License
This project is licensed under the Apache 2.0 License.

---
**🔗 Repository**: [https://github.com/ilyessaadna10/FieldBot.git](https://github.com/ilyessaadna10/FieldBot.git)
