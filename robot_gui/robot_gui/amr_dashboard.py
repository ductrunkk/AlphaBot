#!/usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, 
    QPushButton, QVBoxLayout
)
from PyQt5.QtCore import Qt, QThread

class RosWorker(QThread):
    def __init__(self):
        super().__init__()
        self.node = None
        self._is_running = True

    def run(self):
        rclpy.init(args=None)
        self.node = Node('amr_gui_node')
        self.goal_pub = self.node.create_publisher(PoseStamped, '/goal_pose', 10)
        self.node.get_logger().info("ROS 2 Worker Thread Started.")
        
        while rclpy.ok() and self._is_running:
            rclpy.spin_once(self.node, timeout_sec=0.1)
            
        self.node.destroy_node()
        rclpy.shutdown()

    def publish_goal(self, x: float, y: float, rz: float, rw: float):
        if self.node is not None:
            msg = PoseStamped()
            msg.header.frame_id = 'map'
            msg.header.stamp = self.node.get_clock().now().to_msg()
            msg.pose.position.x = float(x)
            msg.pose.position.y = float(y)
            msg.pose.position.z = 0.0
            
            msg.pose.orientation.x = 0.0
            msg.pose.orientation.y = 0.0
            msg.pose.orientation.z = float(rz)
            msg.pose.orientation.w = float(rw)
            
            self.goal_pub.publish(msg)
            self.node.get_logger().info(f"Published Goal: x={x}, y={y}")

    def stop(self):
        self._is_running = False
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Semantic Navigation Controls")
        self.resize(350, 250)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("Locations")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        self.btn_canteen_room = QPushButton("Canteen Room")
        self.btn_canteen_room.setCursor(Qt.PointingHandCursor)
        main_layout.addWidget(self.btn_canteen_room)
        
        self.btn_charging_station = QPushButton("Charging Station")
        self.btn_charging_station.setCursor(Qt.PointingHandCursor)
        main_layout.addWidget(self.btn_charging_station)
        
        button_style = """
            QPushButton {
                background-color: #0078D7;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
            QPushButton:hover { background-color: #005A9E; }
            QPushButton:pressed { background-color: #004578; }
        """
        self.btn_canteen_room.setStyleSheet(button_style)
        self.btn_charging_station.setStyleSheet(button_style)
        main_layout.addStretch()
        
        self.ros_thread = RosWorker()
        
        self.btn_canteen_room.clicked.connect(lambda: self.ros_thread.publish_goal(x=15.0305, y=0.897978, rz=-0.953415, rw=0.301662))
        self.btn_charging_station.clicked.connect(lambda: self.ros_thread.publish_goal(x=0.0, y=0.0, rz=0.0, rw=1.0))
        
        self.ros_thread.start()

    def closeEvent(self, event):
        self.ros_thread.stop()
        event.accept()

def main(args=None):
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
