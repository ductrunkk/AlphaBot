# AlphaBot

AlphaBot is a ROS 2 workspace for a differential-drive mobile robot with support for:

- Simulation in Gazebo
- Real hardware bringup (ros2_control + sensors)
- Teleoperation with joystick
- Localization and navigation (Nav2)
- SLAM mapping (slam_toolbox)
- YOLOv8-based object detection

## Repository Structure

This repository is organized as multiple ROS 2 packages:

- `robot_bringup` — system launch files and runtime configs
- `robot_controller` — robot controllers and twist relay
- `robot_description` — URDF/Xacro, meshes, Gazebo worlds/models
- `robot_firmware` — ros2_control hardware interface + serial/IMU scripts
- `robot_sensor` — sensor processing nodes (IMU republisher, odometry tools)
- `robot_localize` — localization-related package scaffolding
- `robot_map` — map YAML assets
- `robot_utils` — safety stop utility node
- `robot_recognition` — YOLOv8 ROS 2 integration
- `yolov8_msgs` — custom messages for detection outputs

## Prerequisites

- Ubuntu (recommended for ROS 2 workflows)
- ROS 2 (Humble or compatible)
- `colcon`, `rosdep`, and common ROS 2 build tools
- Gazebo + ROS 2 Gazebo integration packages
- Navigation2 + slam_toolbox
- Optional hardware dependencies:
  - RPLidar (`rplidar_ros`)
  - USB camera (`usb_cam`)
  - Joystick stack (`joy`, `joy_teleop`, `twist_mux`)
- Optional perception dependencies:
  - Python packages: `ultralytics`, `opencv-python`, `numpy`

## Setup

From the repository root:

```bash
cd /home/runner/work/AlphaBot/AlphaBot
```

Install ROS dependencies:

```bash
rosdep update
rosdep install --from-paths . --ignore-src -r -y
```

Build the workspace:

```bash
colcon build --symlink-install
source install/setup.bash
```

## Run

### 1) Simulation Bringup

```bash
ros2 launch robot_bringup launch_sim.launch.py
```

This launches Gazebo, controllers, joystick teleop, and the safety stop node.

### 2) Real Robot Bringup

```bash
ros2 launch robot_bringup launch_real.launch.py
```

This launches hardware interface, controllers, lidar, USB camera, IMU driver, and joystick teleop.

### 3) Localization

- Local EKF localization:

```bash
ros2 launch robot_bringup local_localization.py
```

- Global localization with map server + AMCL:

```bash
ros2 launch robot_bringup global_localization.py
```

### 4) Navigation (Nav2)

```bash
ros2 launch robot_bringup navigation.launch.py use_sim_time:=true
```

Use `use_sim_time:=false` for real robot usage.

### 5) SLAM Mapping

```bash
ros2 launch robot_bringup slam.launch.py use_sim_time:=true
```

### 6) YOLOv8 Perception

```bash
ros2 launch robot_recognition launch_yolov8.launch.py
```

The YOLO node subscribes to camera topic `rgb_cam/image_raw` and publishes:

- `/Yolov8_Inference`
- `/inference_result`

> Note: No `.pt` model file is currently stored in this repository. The default model parameter is `yolov8n.pt`, so ensure model weights are available at runtime.

## Useful Config Paths

- Nav2 params: `robot_bringup/config/robot_params.yaml`
- SLAM params: `robot_bringup/config/slam_toolbox.yaml`
- EKF params: `robot_bringup/config/ekf.yaml`
- Controller params: `robot_bringup/config/robot_controllers.yaml`
- Lidar params: `robot_bringup/config/rplidar_a1.yaml`
- Camera params: `robot_bringup/config/webcam.yaml`

## Notes

- Several package manifests still contain placeholder metadata (`TODO` description/license).
- In this environment, `colcon` may not be preinstalled; install ROS 2 tooling before building.
