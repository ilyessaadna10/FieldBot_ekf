import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped, Twist
from std_srvs.srv import Trigger
import time

class SurveyBot(Node):
    def __init__(self):
        super().__init__('survey_bot')
        self.cmd_vel_pub = self.create_publisher(TwistStamped, '/diff_drive_base_controller/cmd_vel', 10)
        self.srv_mark_right = self.create_client(Trigger, 'mark_tree_right')
        self.srv_mark_left = self.create_client(Trigger, 'mark_tree_left')
        self.srv_end_row = self.create_client(Trigger, 'end_row')
        self.srv_start_row = self.create_client(Trigger, 'start_row')

    def start_row(self):
        self.get_logger().info("Starting Row...")
        self.srv_start_row.call_async(Trigger.Request())
        time.sleep(2.0)

    def move_and_mark(self, linear_x, duration, mark_side=None):
        self.get_logger().info(f"Moving x={linear_x} for {duration}s...")
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.twist.linear.x = linear_x
        
        start_time = time.time()
        while time.time() - start_time < duration:
            msg.header.stamp = self.get_clock().now().to_msg()
            self.cmd_vel_pub.publish(msg)
            time.sleep(0.1)
        
        # Stop
        msg.twist.linear.x = 0.0
        msg.header.stamp = self.get_clock().now().to_msg()
        self.cmd_vel_pub.publish(msg)
        time.sleep(1.0) 

        if mark_side == 'right':
            self.get_logger().info("Marking Tree Right...")
            self.srv_mark_right.call_async(Trigger.Request())
        elif mark_side == 'left':
            self.get_logger().info("Marking Tree Left...")
            self.srv_mark_left.call_async(Trigger.Request())
        elif mark_side == 'end':
            self.get_logger().info("Ending Row...")
            self.srv_end_row.call_async(Trigger.Request())
        
        time.sleep(2.0) 

def main():
    rclpy.init()
    bot = SurveyBot()
    
    # 0. Start Row
    bot.start_row()
    
    # 1. Move and mark tree right
    bot.move_and_mark(0.5, 3.0, 'right')
    
    # 2. Move and mark tree left
    bot.move_and_mark(0.5, 3.0, 'left')
    
    # 3. Move and end row
    bot.move_and_mark(0.5, 3.0, 'end')
    
    bot.get_logger().info("Survey script finished.")
    bot.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
