#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from yolov8_msgs.msg import Yolov8Inference
import math

class YoloToLaserScan(Node):
    def __init__(self):
        super().__init__('yolo_to_laser_scan')

        self.subscription = self.create_subscription(
            Yolov8Inference,
            '/Yolov8_Inference',
            self.yolo_callback,
            10)

        self.scan_pub = self.create_publisher(LaserScan, '/yolo_scan', 10)

        self.image_width = 320.0
        self.image_height = 240.0
        self.camera_fov_rad = 83.0 * (math.pi / 180.0) # Camera Field of View (83 degrees)
        
        # Distance formula: Distance = K / (y_bottom - horizon_y)
        # If the robot avoids too early -> Decrease K. If it avoids too late -> Increase K.
        self.K_factor = 31.0   # Focal length * camera height constant
        self.horizon_y = 120.0    # Horizon (Usually the middle of the screen)
        
        self.last_scan_msg = None
        self.last_detect_time = self.get_clock().now()
        self.memory_duration = 1.0  # seconds

    def yolo_callback(self, msg):
        scan = LaserScan()
        scan.header.stamp = self.get_clock().now().to_msg()
        scan.header.frame_id = "rgb_cam_camera_link_frame" 
        has_obstacle = False

        scan.angle_min = -self.camera_fov_rad / 2.0
        scan.angle_max = self.camera_fov_rad / 2.0
        
        # Create 64 laser rays within the 60 degree FoV
        num_rays = 64
        scan.angle_increment = self.camera_fov_rad / num_rays
        scan.range_min = 0.10 # change
        scan.range_max = 5.0

        # Initialize all rays to Infinity (No obstacles)
        scan.ranges = [float('inf')] * num_rays

        # 2. Process each object detected by YOLO
        for r in msg.yolov8_inference:
            if r.class_name == "obstacle":
                has_obstacle = True
                # Calculate distance based on the bottom edge
                y_bottom = float(r.bottom)
                
                if y_bottom <= self.horizon_y:
                    continue # Skip if the object is above the horizon (too far)
                
                # Apply depth interpolation formula
                distance = self.K_factor / (y_bottom - self.horizon_y)
                
                # Limit fake distance
                if distance < scan.range_min or distance > scan.range_max:
                    continue

                # Calculate angles of the left and right edges of the Bounding Box
                # To create a "Wall" with the exact width of the obstacle
                angle_left = -(float(r.left) - self.image_width/2) * (self.camera_fov_rad / self.image_width)
                angle_right = -(float(r.right) - self.image_width/2) * (self.camera_fov_rad / self.image_width)

                # Find the laser ray index corresponding to that angle
                idx_start = int((min(angle_left, angle_right) - scan.angle_min) / scan.angle_increment)
                idx_end = int((max(angle_left, angle_right) - scan.angle_min) / scan.angle_increment)

                # Limit array
                idx_start = max(0, min(idx_start, num_rays - 1))
                idx_end = max(0, min(idx_end, num_rays - 1))

                # Write distance to those laser rays
                for i in range(idx_start, idx_end + 1):
                    # Only update if the new distance is closer than the old distance
                    if distance < scan.ranges[i]:
                        scan.ranges[i] = distance

        current_time = self.get_clock().now()
        
        # 3. SHORT-TERM MEMORY LOGIC
        if has_obstacle:
            # YOLO DETECTED -> Update memory and publish immediately
            self.last_scan_msg = scan
            self.last_detect_time = current_time
            self.scan_pub.publish(scan)
        else:
            time_diff = (current_time - self.last_detect_time).nanoseconds / 1e9
            if self.last_scan_msg is not None and time_diff < self.memory_duration:               
                self.last_scan_msg.header.stamp = current_time.to_msg() 
                self.scan_pub.publish(self.last_scan_msg)   
            else:
                self.scan_pub.publish(scan)

    
def main(args=None):
    rclpy.init(args=args)
    node = YoloToLaserScan()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()