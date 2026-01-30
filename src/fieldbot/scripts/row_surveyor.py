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
        
        # State management for hierarchical mapping
        self.active_row = None
        
        # Services for hierarchical tagging
        self.srv_start_row = self.create_service(Trigger, 'start_row', self.start_row_callback)
        self.srv_end_row = self.create_service(Trigger, 'end_row', self.end_row_callback)
        self.srv_mark_tree_right = self.create_service(Trigger, 'mark_tree_right', self.mark_tree_right_callback)
        self.srv_mark_tree_left = self.create_service(Trigger, 'mark_tree_left', self.mark_tree_left_callback)
        self.srv_mark_fence = self.create_service(Trigger, 'mark_fence', self.mark_fence_callback)
        
        self.declare_parameter('map_file', 'field_map.yaml')
        
        self.get_logger().info(f'Hierarchical Row Surveyor ready.')
        self.get_logger().info(f'Services: /start_row, /end_row, /mark_tree_right, /mark_tree_left, /mark_fence')

    def odom_callback(self, msg):
        self.current_pose = msg.pose.pose

    def get_map_path(self):
        # Dynamically read parameter to allow GUI/User to change it
        return self.get_parameter('map_file').value

    def start_row_callback(self, request, response):
        self.map_file = self.get_map_path()
        if self.active_row is not None:
            response.success = False
            response.message = f"Row already in progress. End it first."
            return response
            
        if self.current_pose is None:
            response.success = False
            response.message = "No odometry."
            return response

        self.active_row = {
            'start': {'x': float(self.current_pose.position.x), 'y': float(self.current_pose.position.y)},
            'end': None,
            'trees_right': [],
            'trees_left': []
        }
        response.success = True
        response.message = "Started new row. Mark trees_right, trees_left or end row when done."
        return response

    def end_row_callback(self, request, response):
        if self.active_row is None:
            response.success = False
            response.message = "No active row to end."
            return response
            
        if self.current_pose is None:
            response.success = False
            response.message = "No odometry."
            return response

        self.active_row['end'] = {'x': float(self.current_pose.position.x), 'y': float(self.current_pose.position.y)}
        
        # Save the completed row
        data = self.load_map()
        if 'rows' not in data: data['rows'] = []
        data['rows'].append(self.active_row)
        self.save_map(data)
        
        self.active_row = None
        response.success = True
        response.message = f"Saved row #{len(data['rows'])}."
        return response

    def mark_tree_right_callback(self, request, response):
        return self._mark_tree('trees_right', response)

    def mark_tree_left_callback(self, request, response):
        return self._mark_tree('trees_left', response)

    def _mark_tree(self, side, response):
        if self.active_row is None:
            response.success = False
            response.message = "Must start a row before marking trees."
            return response
            
        if self.current_pose is None:
            response.success = False
            response.message = "No odometry."
            return response

        tree = {'x': float(self.current_pose.position.x), 'y': float(self.current_pose.position.y)}
        self.active_row[side].append(tree)
        
        response.success = True
        response.message = f"Marked tree #{len(self.active_row[side])} on {side}."
        return response

    def mark_fence_callback(self, request, response):
        if self.current_pose is None:
            response.success = False
            response.message = "No odometry."
            return response

        data = self.load_map()
        if 'fence' not in data: data['fence'] = []
        data['fence'].append({'x': float(self.current_pose.position.x), 'y': float(self.current_pose.position.y)})
        self.save_map(data)
        
        response.success = True
        response.message = f"Added fence point #{len(data['fence'])}."
        return response

    def load_map(self):
        if os.path.exists(self.map_file):
            with open(self.map_file, 'r') as f:
                try:
                    return yaml.safe_load(f) or {}
                except yaml.YAMLError:
                    return {}
        return {}

    def save_map(self, data):
        with open(self.map_file, 'w') as f:
            yaml.dump(data, f)

    def get_existing_rows(self):
        data = self.load_map()
        return data.get('rows', [])

def main(args=None):
    rclpy.init(args=args)
    node = RowSurveyor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
