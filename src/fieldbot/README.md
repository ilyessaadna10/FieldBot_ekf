# FieldBot Package

**Advanced Autonomous Navigation Stack for Agricultural Robotics**

FieldBot is a professional-grade ROS 2 Jazzy package featuring GPS/IMU/EKF sensor fusion for outdoor localization, 3D RGB-D perception, and Nav2-based autonomous navigation. Designed for agricultural environments with deterministic event-driven architecture.

---

## 🚀 Key Features

### 🛰️ GPS/IMU/EKF Sensor Fusion System
FieldBot uses a **Dual-EKF configuration** for robust outdoor localization, eliminating wheel slip drift common in agricultural terrain.

**System Architecture:**
- **Local EKF**: Provides smooth `odom → base_footprint` transform for high-frequency control
- **Global EKF**: Fuses GPS data for drift-free global positioning
- **NavSat Transform**: Converts GPS lat/lon to Cartesian coordinates

**Sensor Inputs:**
- Wheel Odometry (linear velocity)
- IMU (angular velocity + orientation)
- GPS (absolute position)

**Frame Hierarchy:**
```
map (global reference)
 └─ utm (GPS coordinate system)
     └─ odom (local navigation origin)
         └─ base_footprint (robot pose)
             └─ base_link (chassis)
                 └─ [sensors: gps_link, imu_link, laser_frame, camera_link]
```

> [!IMPORTANT]
> This package uses **GPS/IMU/EKF sensor fusion**, **NOT SLAM or AMCL**. It provides absolute global positioning suitable for outdoor agricultural environments where traditional map-based localization fails.

**Key Benefits:**
- ✅ No long-term drift (GPS correction)
- ✅ Smooth local control (continuous odometry)
- ✅ Return to exact GPS waypoints daily
- ✅ Works in dynamic outdoor environments

---

### 📷 RGB-D 3D Perception

High-fidelity RGB-D camera simulation with proper optical frame alignment.

**Data Streams:**
| Topic | Message Type | Encoding | Description |
|-------|-------------|----------|-------------|
| `/camera/image_raw` | `sensor_msgs/Image` | `rgb8` | Color images |
| `/camera/depth` | `sensor_msgs/Image` | `32FC1` | Depth maps |
| `/camera/points` | `sensor_msgs/PointCloud2` | - | 3D point clouds |

**Technical Highlights:**
- ✅ REP-103 compliant optical frames
- ✅ Memory-aligned RGB8 encoding (no stripe artifacts)
- ✅ Synchronized depth and color streams
- ✅ GPU-accelerated rendering (OGRE 2)

---

### 🧭 Nav2 Path Planning & Navigation

Full autonomous navigation stack with professional safety features.

**Navigation Components:**
- **Global Planner**: Dijkstra/A* for optimal path finding
- **Local Planner**: Regulated Pure Pursuit (RPP) controller
- **Collision Monitor**: Real-time safety reflex layer
- **Velocity Smoother**: Smooth acceleration/deceleration

**Control System:**
- `ros2_control` framework for hardware abstraction
- Differential drive controller
- Joint state broadcasting
- Gazebo Sim integration via `gz_ros2_control`

---

### 🚜 Agricultural Intelligence

**Row Surveyor Tool** (`scripts/row_surveyor.py`)

Record GPS waypoints while manually surveying agricultural fields.

**Services:**
```bash
# Mark row boundaries
ros2 service call /mark_start std_srvs/srv/Trigger
ros2 service call /mark_end std_srvs/srv/Trigger

# Mark field perimeter
ros2 service call /mark_fence std_srvs/srv/Trigger
```

**Output:** Generates `field_map.yaml` with semantic waypoints:
```yaml
waypoints:
  - {x: 570747.95, y: 4829016.65, type: 'row_start'}
  - {x: 570771.23, y: 4829018.42, type: 'row_end'}
  - {x: 570750.11, y: 4829025.88, type: 'fence'}
```

---

## 🛠 Tech Stack

- **ROS 2**: Jazzy Jalisco
- **Simulator**: Gazebo Harmonic
- **Localization**: `robot_localization` (dual-EKF)
- **Navigation**: `nav2_bringup`
- **Control**: `ros2_control` + `gz_ros2_control`
- **Sensors**: GPU LiDAR (30Hz), RGB-D Camera, GPS, IMU

---

## 📦 Installation & Setup

### Prerequisites
- Ubuntu 24.04 (Noble Numbat)
- ROS 2 Jazzy Jalisco
- Gazebo Harmonic

### Build Instructions

```bash
# Clone into your ROS 2 workspace
cd ~/ros2_ws/src
git clone https://github.com/ilyessaadna10/FieldBot.git fieldbot

# Install dependencies
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y

# Build the package
colcon build --symlink-install --packages-select fieldbot
source install/setup.bash
```

---

## 🛰 Usage

### Launch Full Stack

Start everything (simulator, sensors, localization, navigation):

```bash
ros2 launch fieldbot fieldbot_launch.py
```

**What Launches:**
1. Gazebo Harmonic with agricultural vineyard world
2. Robot spawning and state publisher
3. Sensor bridges (LiDAR, Camera, GPS, IMU)
4. Dual-EKF localization nodes
5. Nav2 navigation stack
6. RViz visualization (auto-opens after 5 seconds)

### Set Navigation Goals

1. **Wait for RViz** to open automatically
2. **Click "2D Goal Pose"** button in toolbar
3. **Click and drag** on the map to set target pose
4. Robot navigates autonomously using Nav2!

### Optional: Change World

```bash
# Navigation test world (obstacles and pillars)
ros2 launch fieldbot fieldbot_launch.py \
  world:=$(ros2 pkg prefix fieldbot)/share/fieldbot/worlds/navigation_world.sdf

# Agricultural vineyard (default)
ros2 launch fieldbot fieldbot_launch.py \
  world:=$(ros2 pkg prefix fieldbot)/share/fieldbot/worlds/vineyard_variable.sdf
```

### Manual Control (Testing)

```bash
# Publish velocity commands directly
ros2 topic pub /diff_drive_base_controller/cmd_vel_unstamped \
  geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.0}}"
```

---

## 🗺️ Field Mapping Workflow

Use the Row Surveyor to build reusable field maps:

```bash
# 1. Launch the system
ros2 launch fieldbot fieldbot_launch.py

# 2. Drive to start of row 1, then mark it
ros2 service call /mark_start std_srvs/srv/Trigger

# 3. Drive to end of row 1, then mark it
ros2 service call /mark_end std_srvs/srv/Trigger

# 4. Repeat for all rows and field boundaries
ros2 service call /mark_fence std_srvs/srv/Trigger

# 5. Waypoints are saved to: field_map.yaml
cat field_map.yaml
```

---

## 📐 Coordinate Systems (REP-103)

The system strictly follows ROS 2 spatial standards:

**Robot Body Frame** (`base_link`):
- **+X**: Forward
- **+Y**: Left
- **+Z**: Up

**Camera Optical Frame** (`camera_link`):
- **+Z**: Into the world (lens direction)
- **+X**: Right
- **+Y**: Down

**Global Frame** (`map`):
- **ENU**: East-North-Up coordinate system aligned with GPS

---

## 📖 Documentation

Comprehensive technical deep-dives available in [`docs/`](./docs/):

| Document | Description |
|----------|-------------|
| [`gps_imu_ekf_integration.md`](./docs/gps_imu_ekf_integration.md) | Complete dual-EKF setup, TF tree debugging, feedback loop fixes |
| [`perception_and_mechanics.md`](./docs/perception_and_mechanics.md) | RGB-D camera integration, byte alignment fixes, URDF specifications |
| [`launch_architecture.md`](./docs/launch_architecture.md) | Event-driven deterministic startup with `RegisterEventHandler` |
| [`advanced_roadmap.md`](./docs/advanced_roadmap.md) | Future AI perception and coverage path planning |
| [`modifications_summary.md`](./docs/modifications_summary.md) | Technical record of all optimizations and polishes |

---

## ⚙️ Configuration Files

| File | Purpose |
|------|---------|
| [`params/fieldbot_params.yaml`](./params/fieldbot_params.yaml) | Nav2 stack configuration |
| [`params/ekf.yaml`](./params/ekf.yaml) | Dual-EKF and NavSat transform settings |
| [`config/ros2_controllers.yaml`](./config/ros2_controllers.yaml) | Differential drive controller config |
| [`rviz/fieldbot.rviz`](./rviz/fieldbot.rviz) | RViz visualization profile |

---

## 🏗️ Architecture Highlights

### Event-Driven Launch System
Uses `RegisterEventHandler` instead of brittle timers for deterministic startup:

```python
load_nav2 = RegisterEventHandler(
    event_handler=OnProcessStart(
        target_action=ekf_global,
        on_start=[nav2_bringup],
    )
)
```

### Hardware Abstraction Layer
`ros2_control` enables seamless sim-to-real transfer. Only the plugin changes:
- **Simulation**: `gz_ros2_control/GazeboSimSystem`
- **Hardware**: `your_driver/PhysicalMotorSystem`

### Sensor Optimization
- **LiDAR**: 30Hz update rate (bumped from 10Hz) for smooth tracking
- **Transform Tolerance**: 0.5s to absorb Gazebo clock jitter
- **Physics Step**: 1ms (0.001s) for high-fidelity collision detection

---

## 🚧 Status

**Current Implementation**: ✅ Fully functional GPS-based outdoor navigation

**Under Development**: 🔮 AI-powered perception and coverage path planning (see [`docs/advanced_roadmap.md`](./docs/advanced_roadmap.md))

---

## 🛡️ License

Apache 2.0 License

---

*Developed as a learning-in-public milestone for Advanced ROS 2 Robotics.*
