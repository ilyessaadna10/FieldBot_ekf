# FieldBot: Autonomous Agricultural Navigation Stack

**Professional-grade ROS 2 Jazzy implementation for outdoor autonomous mobile robots, featuring GPS/IMU/EKF sensor fusion and agricultural field navigation.**

FieldBot is designed for real-world agricultural environments with GPS-based global localization, 3D perception, and deterministic event-driven architecture. This project demonstrates senior-level ROS 2 development practices including sensor fusion, hardware abstraction, and outdoor navigation.

---

## 🌟 Key Features

### 🛰️ GPS/IMU/EKF Sensor Fusion
- **Dual-EKF Localization**: Separate local and global EKF filters for smooth navigation
- **Global Positioning**: GPS-based absolute positioning for outdoor agricultural environments
- **Multi-Sensor Fusion**: Combines wheel odometry, IMU orientation, and GPS coordinates
- **No Drift Navigation**: Eliminates long-term position drift common in wheel-only odometry
- **Frame Architecture**: `map → utm → odom → base_footprint` transform tree

> [!NOTE]
> This project uses **GPS/IMU/EKF sensor fusion** for localization, **NOT SLAM or AMCL**. It provides absolute global outdoor positioning suitable for agricultural field operations.

### 📷 RGB-D 3D Perception
- **Depth Sensing**: Simulated RGB-D camera with point cloud generation
- **Corrected Optical Frames**: Proper REP-103 coordinate system compliance
- **Multiple Data Streams**:
  - `/camera/image_raw` - RGB images (rgb8 encoding)
  - `/camera/depth` - Depth maps (32FC1)
  - `/camera/points` - 3D point clouds (PointCloud2)
- **Memory-Aligned Encoding**: Fixed byte alignment for clean visual data

### 🧭 Autonomous Navigation
- **Nav2 Integration**: Full path planning and navigation stack
- **Path Planning Algorithms**: Dijkstra/A* for global planning
- **Controller**: Regulated Pure Pursuit (RPP) for trajectory following
- **Safety**: Dedicated collision monitor node for real-time obstacle avoidance
- **Differential Drive**: Professional `ros2_control` integration

### 🚜 Agricultural Intelligence
- **Vineyard Surveyor GUI**: A professional Tkinter interface for field mapping and mission control.
- **Hierarchical Mapping**: GPS waypoint recording with row semantic structure.
  - Services: `/start_row`, `/end_row`, `/mark_tree_left`, `/mark_tree_right`, `/mark_fence`
  - Records semantic field positions to YAML.
  - Supports **Multi-Map Management** (append/create/load specific files).
- **Hugging Navigation Pattern**: Deterministic traversal that "hugs" tree lines with perspective awareness.
- **Virtual Bumper**: LiDAR-based safety system enforcing a strict **20cm safety margin**.

### ⚙️ Professional Architecture
- **Event-Driven Launch**: `RegisterEventHandler` for deterministic node startup
- **Hardware Abstraction**: `ros2_control` enables seamless sim-to-real transfer
- **Simulation Ready**: High-fidelity Gazebo Harmonic with GPU-accelerated sensors
- **DDS Middleware**: Fast-DDS for peer-to-peer communication
- **Dual Simulation Worlds**: Navigation test environment and agricultural vineyard

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **OS** | Ubuntu 24.04 (Noble) |
| **ROS** | ROS 2 Jazzy Jalisco |
| **Simulator** | Gazebo Harmonic |
| **Navigation** | Nav2 (Regulated Pure Pursuit) |
| **Localization** | `robot_localization` (Dual-EKF) |
| **Control** | `ros2_control` + `gz_ros2_control` |
| **Middleware** | Fast-DDS |
| **Sensors** | LiDAR (30Hz), RGB-D Camera, GPS, IMU |

---

## 📂 Project Structure

```
bakus_ws/
├── src/
│   └── fieldbot/
│       ├── config/          # ros2_control configuration
│       ├── docs/            # Technical deep-dive documentation
│       ├── launch/          # Event-driven launch sequences
│       ├── params/          # Nav2, EKF, and sensor parameters
│       ├── rviz/            # Visualization configurations
│       ├── scripts/         # Agricultural utilities (row_surveyor)
│       ├── urdf/            # Robot description with sensors
│       └── worlds/          # Gazebo simulation environments
├── build/
├── install/
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites

Ensure you have the following installed:
- **Ubuntu 24.04** (Noble Numbat)
- **ROS 2 Jazzy Jalisco**
- **Gazebo Harmonic**

### Installation

```bash
# Clone the repository
cd ~/ros2_ws/src
git clone https://github.com/ilyessaadna10/FieldBot.git fieldbot

# Install dependencies
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y

# Build the workspace
colcon build --symlink-install --packages-select fieldbot
source install/setup.bash
```

### Step 3: Run the Mission Stack
In a second terminal, launch the agricultural mission services and the GUI:

```bash
ros2 launch fieldbot mission.launch.py
```

This command starts:
- ✅ **Row Surveyor**: Service-based mapping logic.
- ✅ **Tree Navigator**: Autonomous GPS waypoint follower.
- ✅ **Surveyor GUI**: Graphical interface for mapping and control.

### Step 4: Map & Navigate
1. Use the **Surveying GUI** to start a new row.
2. Mark trees as you pass them.
3. Click **"End Row & Save"** to write to YAML.
4. Click **"START AUTONOMOUS MISSION"** to begin the "hugging" traversal.

---

## 🗺️ Agricultural Field Mapping

Use the **Row Surveyor** to record GPS waypoints while manually driving through your field:

```bash
# Start the system with GPS localization active
ros2 launch fieldbot fieldbot_launch.py

# In separate terminals, mark waypoints:
ros2 service call /mark_start std_srvs/srv/Trigger  # Start of row
ros2 service call /mark_end std_srvs/srv/Trigger    # End of row
ros2 service call /mark_fence std_srvs/srv/Trigger  # Field boundary

# Waypoints are saved to: field_map.yaml
```

---

## 📖 Documentation

Comprehensive technical documentation is available in [`src/fieldbot/docs/`](./src/fieldbot/docs/):

| Document | Description |
|----------|-------------|
| [Detailed System Architecture](./src/fieldbot/docs/system_architecture_detailed.md) | **Exhaustive guide to the current GPS/GUI mission system** |
| [GPS/IMU/EKF Integration](./src/fieldbot/docs/gps_imu_ekf_integration.md) | Guide to dual-EKF sensor fusion core |
| [Perception & Mechanics](./src/fieldbot/docs/perception_and_mechanics.md) | RGB-D camera integration and URDF specifications |
| [Launch Architecture](./src/fieldbot/docs/launch_architecture.md) | Event-driven deterministic startup system |

---

## 🧪 Coordinate Systems (REP-103)

The system follows ROS 2 spatial standards:

- **Base Frame** (`base_link`): Forward: +X, Left: +Y, Up: +Z
- **Optical Frame** (`camera_link`): Into Lens: +Z, Right: +X, Down: +Y
- **Global Frame** (`map`): ENU (East-North-Up) aligned with GPS coordinates

---

## 🔧 Configuration

Key configuration files:

- **Navigation**: [`params/fieldbot_params.yaml`](./src/fieldbot/params/fieldbot_params.yaml)
- **Localization**: [`params/ekf.yaml`](./src/fieldbot/params/ekf.yaml)
- **Control**: [`config/ros2_controllers.yaml`](./src/fieldbot/config/ros2_controllers.yaml)
- **Visualization**: [`rviz/fieldbot.rviz`](./src/fieldbot/rviz/fieldbot.rviz)

---

## 🚧 Status & Future Roadmap

**Current Status**: ✅ Fully functional GPS-based outdoor navigation system

**Planned Enhancements**:
- 🔮 AI-powered weed detection with YOLO
- 🔮 Coverage path planning for field operations
- 🔮 Real hardware deployment on physical robot
- 🔮 Multi-robot coordination for large fields

---

## 🛡️ License

This project is licensed under the **Apache 2.0 License**.

---

## 🔗 Links

- **Repository**: [https://github.com/ilyessaadna10/FieldBot.git](https://github.com/ilyessaadna10/FieldBot.git)
- **Maintainer**: ilyaes (saadna.ilyes.dev@gmail.com)

---

*Developed as a professional demonstration of Advanced ROS 2 Robotics for agricultural applications.*
