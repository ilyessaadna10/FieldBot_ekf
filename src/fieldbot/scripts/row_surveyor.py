#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_srvs.srv import Trigger
import yaml
import os

class RowSurveyor(Node):
    def __init__(self):
        super().__init__('row_surveyor')
        
        # Subscribe to global fused odometry
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odometry/global',
            self.odom_callback,
            10
        )
        self.current_pose = None
        
        # Services for semantic tagging
        self.srv_start = self.create_service(Trigger, 'mark_start', self.mark_start_callback)
        self.srv_end = self.create_service(Trigger, 'mark_end', self.mark_end_callback)
        self.srv_fence = self.create_service(Trigger, 'mark_fence', self.mark_fence_callback)
        
        self.map_file = 'field_map.yaml'
        self.get_logger().info(f'Row Surveyor ready. Services: /mark_start, /mark_end, /mark_fence -> {self.map_file}')

    def odom_callback(self, msg):
        self.current_pose = msg.pose.pose

    def mark_start_callback(self, request, response):
        return self.save_pose('row_start', response)

    def mark_end_callback(self, request, response):
        return self.save_pose('row_end', response)

    def mark_fence_callback(self, request, response):
        return self.save_pose('fence', response)

    def save_pose(self, tag, response):
        if self.current_pose is None:
            response.success = False
            response.message = "No odometry received yet."
            return response
            
        x = self.current_pose.position.x
        y = self.current_pose.position.y
        
        self.get_logger().info(f"Recording {tag}: x={x:.2f}, y={y:.2f}")
        
        # Append to YAML file with semantic tag
        data = {
            'x': float(x),
            'y': float(y),
            'type': tag
        }
        
        # Read existing or create new
        existing_data = []
        if os.path.exists(self.map_file):
            with open(self.map_file, 'r') as f:
                try:
                    loaded = yaml.safe_load(f)
                    if loaded and 'waypoints' in loaded:
                        existing_data = loaded['waypoints']
                except yaml.YAMLError:
                    pass
        
        existing_data.append(data)
        
        with open(self.map_file, 'w') as f:
            yaml.dump({'waypoints': existing_data}, f)
            
        response.success = True
        response.message = f"Saved {tag} #{len(existing_data)}: ({x:.2f}, {y:.2f})"
        return response

def main(args=None):
    rclpy.init(args=args)
    node = RowSurveyor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
