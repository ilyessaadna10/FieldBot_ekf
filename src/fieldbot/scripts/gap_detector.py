#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32, Int32
import numpy as np
import math

class GapDetector(Node):
    def __init__(self):
        super().__init__('gap_detector')
        
        # Parameters
        self.declare_parameter('tool_width', 0.6) # Width of the weeding tool
        self.declare_parameter('min_overlap', 0.1) # Minimum overlap between passes (meters)
        
        self.tool_width = self.get_parameter('tool_width').value
        self.min_overlap = self.get_parameter('min_overlap').value
        
        # Subscriptions
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            rclpy.qos.qos_profile_sensor_data
        )
        
        # Publishers
        self.width_pub = self.create_publisher(Float32, '/alley_width', 10)
        self.passes_pub = self.create_publisher(Int32, '/passes_required', 10)
        
        self.get_logger().info('Gap Detector Node Started')

    def scan_callback(self, msg):
        # We only care about the sides (perpendicular to robot movement)
        # Assuming robot x is forward, y is left.
        # Standard LIDAR 0 degree is usually forward.
        # Left side (+90 deg), Right side (-90 deg)
        
        ranges = np.array(msg.ranges)
        angles = np.linspace(msg.angle_min, msg.angle_max, len(ranges))
        
        # Filter for valid ranges
        valid_indices = np.where((ranges >= msg.range_min) & (ranges <= msg.range_max))
        valid_ranges = ranges[valid_indices]
        valid_angles = angles[valid_indices]
        
        if len(valid_ranges) == 0:
            return

        # Convert to Cartesian (Robot Local Frame)
        points_x = valid_ranges * np.cos(valid_angles)
        points_y = valid_ranges * np.sin(valid_angles)
        
        # Identify "Left Row" and "Right Row"
        # We look for the closest points in a narrow window around y-axis (perpendicular)
        # for a small x window (e.g. -0.5 to 0.5) to get current row width
        
        window_x = 1.0 # 1 meter window (-0.5 to 0.5)
        mask_local = (points_x > -window_x/2) & (points_x < window_x/2)
        
        points_y_local = points_y[mask_local]
        
        if len(points_y_local) == 0:
            return
            
        left_side = points_y_local[points_y_local > 0]
        right_side = points_y_local[points_y_local < 0]
        
        if len(left_side) == 0 or len(right_side) == 0:
            # We are likely at a break in the row (headland)
            return
            
        # Find the distance to the row walls
        # We use the percentile to avoid noise from individual leaves/posts
        dist_left = np.percentile(left_side, 10) # Closest 10%
        dist_right = np.percentile(right_side, 90) # Closest 10% (largest negative is closest)
        
        alley_width = dist_left - dist_right
        
        # Calculate passes
        # passes = ceil((width - tool_width) / (tool_width - overlap)) + 1
        # Example: width 1.8, tool 0.6, overlap 0.1
        # pass 1: at y=0 covers [-0.3, 0.3] -> too narrow
        effective_step = self.tool_width - self.min_overlap
        num_passes = math.ceil(alley_width / self.tool_width)
        
        # Publish
        self.width_pub.publish(Float32(data=float(alley_width)))
        self.passes_pub.publish(Int32(data=int(num_passes)))
        
        # Log occasionally
        # self.get_logger().info(f'Width: {alley_width:.2f}m | Passes: {num_passes}', throttle_duration_sec=1.0)

def main(args=None):
    rclpy.init(args=args)
    node = GapDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
