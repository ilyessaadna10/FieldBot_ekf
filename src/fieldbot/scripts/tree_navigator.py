#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from sensor_msgs.msg import LaserScan
from std_srvs.srv import Trigger
import yaml
import os

class TreeNavigator(Node):
    def __init__(self):
        super().__init__('tree_navigator')
        
        self.declare_parameter('map_file', 'field_map.yaml')
        
        # Nav2 Action Client
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Perception (LiDAR Only)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        
        # Safety State
        self.is_emergency_stop = False
        
        # Mission State Machine
        self.rows = []
        self.current_row_idx = 0
        self.current_waypoint_idx = 0 
        self.current_side = 'right' 
        self.state = 'IDLE' 
        self.mission_started = False
        
        # Services for Control
        self.srv_start_mission = self.create_service(Trigger, 'start_mission', self.start_mission_callback)
        self.srv_reload_map = self.create_service(Trigger, 'reload_map', self.reload_map_callback)
        
        # Timer for mission execution (runs at 1Hz)
        self.timer = self.create_timer(1.0, self.mission_control)
        
        self.get_logger().info(f"Tree Navigator (GPS Only) ready. Waiting for /start_mission service.")

    def start_mission_callback(self, request, response):
        self.map_file = self.get_parameter('map_file').value
        self.map_data = self.load_map()
        self.rows = self.map_data.get('rows', [])
        
        if not self.rows:
            response.success = False
            response.message = f"Failed to start: No rows found in {self.map_file}"
            return response

        self.mission_started = True
        self.state = 'IDLE'
        self.current_row_idx = 0
        self.current_waypoint_idx = 0
        response.success = True
        response.message = f"Mission started with {len(self.rows)} rows in {self.map_file}."
        return response

    def reload_map_callback(self, request, response):
        self.map_file = self.get_parameter('map_file').value
        self.map_data = self.load_map()
        self.rows = self.map_data.get('rows', [])
        response.success = True
        response.message = f"Reloaded map {self.map_file}. Found {len(self.rows)} rows."
        return response

    def load_map(self):
        if os.path.exists(self.map_file):
            with open(self.map_file, 'r') as f:
                try:
                    return yaml.safe_load(f) or {}
                except yaml.YAMLError:
                    return {}
        return {}

    def mission_control(self):
        if not self.mission_started:
            return

        if self.state == 'IDLE' and self.rows:
            self.state = 'NAVIGATING'
            self.current_side = 'right'
            self.start_next_waypoint()
        elif self.state == 'COMPLETED':
            self.get_logger().info("Full vineyard mission completed successfully.")
            self.mission_started = False # Reset for next run
            self.state = 'IDLE'

    def start_next_waypoint(self):
        if self.current_row_idx >= len(self.rows):
            self.state = 'COMPLETED'
            return

        row = self.rows[self.current_row_idx]
        
        # Hugging sequence: 
        # 1. Start -> All Right Trees -> End
        # 2. U-Turn
        # 3. End -> All Left Trees (reverse order) -> Start
        
        if self.current_side == 'right':
            # Pass 1: Forward (Start -> End), Hugging Right
            waypoints = [row['start']] + row['trees_right'] + [row['end']]
            if self.current_waypoint_idx < len(waypoints):
                target = waypoints[self.current_waypoint_idx]
                self.get_logger().info(f"Hugging RIGHT: Row {self.current_row_idx+1}, Waypoint {self.current_waypoint_idx}")
                self.navigate_to_pose(target)
            else:
                self.get_logger().info("Finished RIGHT side. Initiating U-Turn to return for LEFT side.")
                self.current_side = 'left'
                self.current_waypoint_idx = 0
                self.state = 'U_TURN'
                self.execute_u_turn()
        else: # side == 'left'
            # Pass 2: Return (End -> Start), Hugging original Left Trees
            # Note: These trees will now be on the robot's physical RIGHT as it returns.
            left_trees_reversed = row['trees_left'][::-1]
            waypoints = [row['end']] + left_trees_reversed + [row['start']]
            
            if self.current_waypoint_idx < len(waypoints):
                target = waypoints[self.current_waypoint_idx]
                self.get_logger().info(f"Hugging LEFT: Row {self.current_row_idx+1}, Waypoint {self.current_waypoint_idx}")
                self.navigate_to_pose(target)
            else:
                self.get_logger().info(f"Finished Row {self.current_row_idx+1}. Moving to next row.")
                # We treat each Row Space independently to ensure full coverage of both sides.
                self.current_row_idx += 1
                self.current_side = 'right'
                self.current_waypoint_idx = 0
                self.state = 'NAVIGATING'
                self.start_next_waypoint()

    def navigate_to_pose(self, coords):
        if self.is_emergency_stop:
            return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = coords['x']
        goal_msg.pose.pose.position.y = coords['y']
        goal_msg.pose.pose.orientation.w = 1.0 
        
        self.nav_to_pose_client.wait_for_server()
        self.goal_handle = self.nav_to_pose_client.send_goal_async(goal_msg)
        self.goal_handle.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self.active_goal_handle = future.result()
        if not self.active_goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        result_future = self.active_goal_handle.get_result_async()
        result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        status = future.result().status
        if status == 4: # SUCCEEDED
            self.get_logger().info('Waypoint reached!')
            self.current_waypoint_idx += 1
            self.state = 'NAVIGATING'
            self.start_next_waypoint()
        else:
            self.get_logger().warn(f'Goal failed with status: {status}')

    def execute_u_turn(self):
        self.get_logger().info("Executing U-Turn maneuver...")
        self.state = 'NAVIGATING'
        self.start_next_waypoint()

    def scan_callback(self, msg):
        min_dist = min(msg.ranges) if msg.ranges else float('inf')
        if min_dist < 0.2: # 20cm safety margin
            if not self.is_emergency_stop:
                self.get_logger().warn("OBSTACLE DETECTED! Emergency stop.")
                self.is_emergency_stop = True
                if hasattr(self, 'active_goal_handle') and self.active_goal_handle:
                    self.active_goal_handle.cancel_goal_async()
        elif min_dist > 0.4:
            if self.is_emergency_stop:
                self.get_logger().info("Clear path detected. Resuming mission.")
                self.is_emergency_stop = False
                self.start_next_waypoint()

def main(args=None):
    rclpy.init(args=args)
    node = TreeNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
