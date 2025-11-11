# Medical Autonomous Robot

This project details an Autonomous Mobile Robot (AMR) designed for medical environments, built on the ROS 2 framework. The robot is capable of autonomous mapping (SLAM), localization, and smart navigation using Nav2. It integrates **Computer Vision (YOLO)** to enhance object recognition and improve obstacle avoidance.
## 1. Key Features

* **Autonomous Navigation:** Utilizes the full Nav2 stack (A\* Global Planner, DWB Local Planner), SLAM Toolbox (mapping), and AMCL (localization).
* **AI-Enhanced Avoidance:** Integrates a **YOLO** model to detect objects, which are then inserted into the **Nav2 Costmap**.
* **Low-Level Control:** A real-time **PID control** loop and **Wheel Odometry** calculation are executed on a dedicated ESP32 microcontroller.
* **Distributed Architecture:** A Raspberry Pi handles high-level ROS 2 processing, while the ESP32 manages low-level real-time control, communicating via UART.

## 2. Technology Architecture

### High-Level Controller (Raspberry Pi)
* Runs ROS 2, Nav2, SLAM, and AMCL.
* Executes the Computer Vision (YOLO) node for object detection.
* Runs **Inverse Kinematics** to convert velocity commands into wheel speeds.

### Low-Level Controller (ESP32)
* Executes a high-frequency **PID control loop** to match target wheel speeds.
* Reads **Encoders** to calculate and publish **Odometry** data back to the Pi.
* Sends PWM signals to the **L298N Motor Driver**.

## 3. Core Hardware

* **Processing:** Raspberry Pi (ROS 2) & ESP32 (PID/Odometry).
* **Sensors:** Lidar A1m8 (SLAM/Nav), Webcam (AI/YOLO), IMU MPU6050 (Orientation).
* **Actuators:** DC Motors with Encoders, L298N Motor Driver.
