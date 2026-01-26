# FieldBot: Advanced Autonomous Navigation Stack

FieldBot is a professional-grade ROS 2 Jazzy implementation for autonomous mobile robots, featuring a high-fidelity digital twin in Gazebo Harmonic. This project focuses on deterministic system startup, real-time safety monitoring, and 3D perception-based navigation.

---

## � Key Features

- **ROS 2 Jazzy & Gazebo Harmonic**: Built on the latest LTS release with support for modern SDF/URDF standards.
- **RGB-D Perception**: Clean 3D data stream integration with corrected optical frame alignments and memory-aligned `rgb8` encoding.
- **Event-Driven Launch**: Zero-latency deterministic node startup using ROS 2 event handlers instead of brittle timers.
- **Real-time Safety**: Dedicated `collision_monitor` reflex layer providing a polygon-based lookout for immediate obstacle avoidance.
- **Autonomous SLAM**: Synchronous mapping and localization using the `slam_toolbox` and `Nav2` stack with Dijkstra/A* path discovery.

---

## 🛠 Tech Stack

- **Middleware**: Fast-DDS
- **Navigation**: Nav2 (Regulated Pure Pursuit)
- **Mapping**: Synchronous slam_toolbox
- **Simulation**: Gazebo Harmonic (Harmonic Transport Layer)
- **Robotics Core**: URDF/Xacro, ros2_control, ros_gz_bridge

---

## 📦 Installation & Setup

### Prerequisites
- Ubuntu 24.04 (Noble Numbat)
- ROS 2 Jazzy Jalisco
- Gazebo Harmonic

### Build
```bash
# Clone the repository into into your workspace
cd ~/ros2_ws/src
git clone https://github.com/your-username/FieldBot.git fieldbot

# Build the package
cd ~/ros2_ws
colcon build --symlink-install --packages-select fieldbot
source install/setup.bash
```

---

## 🛰 Usage

### Launch Simulation & Navigation
The primary launch file initializes the physics engine, robot state, sensor bridges, and the Nav2 lifecycle manager in a single command:

```bash
ros2 launch fieldbot fieldbot_launch.py
```

### Manual Goal Setting
1.  RViz will open automatically with a pre-configured profile.
2.  Use the **"2D Goal Pose"** button in the top toolbar.
3.  Click and drag on the map to set a target coordinates and heading.

---

## 📐 Coordinate Systems (REP-103)
The system strictly follows ROS 2 spatial standards:
- **Base Frame**: `base_link` (Forward: +X, Left: +Y, Up: +Z)
- **Optical Frame**: `camera_link` (Into Lens: +Z, Right: +X, Down: +Y)

---

## 📖 Documentation
Detailed technical deep-dives are available in the `docs` folder:
- [System Topology](./docs/topology.md)
- [Launch Architecture](./docs/launch_architecture.md)
- [Perception & Mechanics](./docs/perception_and_mechanics.md)
- [Tuning Guide](./docs/tuning_guide.md)

---

## 🚧 Status
FieldBot is actively being expanded. Current work focuses on **Mission Intelligence** and **Vision-based Object Tracking**.

*Developed as a learning-in-public milestone for Advanced ROS 2 Robotics.*
