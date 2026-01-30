#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class SurveyGui(Node):
    def __init__(self):
        super().__init__('survey_gui')
        
        # Service Clients
        self.cli_start = self.create_client(Trigger, 'start_row')
        self.cli_end = self.create_client(Trigger, 'end_row')
        self.cli_tree_left = self.create_client(Trigger, 'mark_tree_left')
        self.cli_tree_right = self.create_client(Trigger, 'mark_tree_right')
        self.cli_fence = self.create_client(Trigger, 'mark_fence')
        self.cli_start_mission = self.create_client(Trigger, 'start_mission')
        
        # Parameter Clients
        self.cli_param_surveyor = self.create_client(SetParameters, '/row_surveyor/set_parameters')
        self.cli_param_navigator = self.create_client(SetParameters, '/tree_navigator/set_parameters')
        
        # State tracking for UI
        self.last_status = "Ready"
        self.row_active = False

    def call_trigger(self, client, name, callback=None):
        if not client.wait_for_service(timeout_sec=1.0):
            self.last_status = f"Service {name} not available!"
            if callback: callback(False, self.last_status)
            return

        req = Trigger.Request()
        future = client.call_async(req)
        
        def done_callback(fut):
            try:
                res = fut.result()
                if res.success:
                    self.last_status = res.message
                    if callback: callback(True, res.message)
                else:
                    self.last_status = f"Error: {res.message}"
                    if callback: callback(False, res.message)
            except Exception as e:
                self.last_status = f"Call failed: {str(e)}"
                if callback: callback(False, self.last_status)

        future.add_done_callback(done_callback)

    def set_map_parameter(self, filename, callback=None):
        param = Parameter()
        param.name = 'map_file'
        param.value.type = 4 # STRING
        param.value.string_value = filename
        
        req = SetParameters.Request()
        req.parameters = [param]
        
        # We try to set it for both. Even if one fails (e.g. not running), we continue.
        self.cli_param_surveyor.call_async(req)
        fut_nav = self.cli_param_navigator.call_async(req)
        
        if callback:
            fut_nav.add_done_callback(lambda f: callback(True, f"Map file set to {filename}"))

class App:
    def __init__(self, root, node):
        self.root = root
        self.node = node
        self.root.title("FieldBot Vineyard Surveyor")
        self.root.geometry("400x500")
        
        style = ttk.Style()
        style.configure("TButton", padding=10, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))
        
        # Main Frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        ttk.Label(main_frame, text="Vineyard Surveyor", style="Header.TLabel").pack(pady=10)
        
        # Map Management Section
        map_frame = ttk.LabelFrame(main_frame, text="Map Management", padding="10")
        map_frame.pack(fill=tk.X, pady=10)

        ttk.Label(map_frame, text="Map Filename:").pack(side=tk.LEFT)
        self.ent_map = ttk.Entry(map_frame)
        self.ent_map.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.ent_map.insert(0, "field_map.yaml")
        
        self.btn_load_map = ttk.Button(map_frame, text="Apply Map", command=self.on_apply_map)
        self.btn_load_map.pack(side=tk.LEFT)

        # Row Section
        row_frame = ttk.LabelFrame(main_frame, text="Row Controls", padding="10")
        row_frame.pack(fill=tk.X, pady=10)

        self.btn_start = ttk.Button(row_frame, text="START NEW ROW", command=self.on_start_row)
        self.btn_start.pack(fill=tk.X, pady=5)

        tree_frame = ttk.Frame(row_frame)
        tree_frame.pack(fill=tk.X, pady=5)
        
        self.btn_left = ttk.Button(tree_frame, text="TREE LEFT", command=self.on_tree_left, state=tk.DISABLED)
        self.btn_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.btn_right = ttk.Button(tree_frame, text="TREE RIGHT", command=self.on_tree_right, state=tk.DISABLED)
        self.btn_right.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.btn_end = ttk.Button(row_frame, text="END ROW & SAVE", command=self.on_end_row, state=tk.DISABLED)
        self.btn_end.pack(fill=tk.X, pady=5)

        # Static Section
        env_frame = ttk.LabelFrame(main_frame, text="Environment", padding="10")
        env_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(env_frame, text="MARK FENCE POINT", command=self.on_fence).pack(fill=tk.X)

        # Mission Section
        mission_frame = ttk.LabelFrame(main_frame, text="Mission Control", padding="10")
        mission_frame.pack(fill=tk.X, pady=10)
        
        style.configure("Mission.TButton", background="#4CAF50", font=('Helvetica', 10, 'bold'))
        self.btn_mission = ttk.Button(mission_frame, text="START AUTONOMOUS MISSION", 
                                     style="Mission.TButton", command=self.on_start_mission)
        self.btn_mission.pack(fill=tk.X)

        # Status Section
        status_frame = ttk.Frame(main_frame, padding="10")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.lbl_status = ttk.Label(status_frame, text="Status: Ready", wraplength=350)
        self.lbl_status.pack()

    def update_status(self, success, message):
        color = "black" if success else "red"
        self.lbl_status.config(text=f"Status: {message}", foreground=color)

    def on_apply_map(self):
        filename = self.ent_map.get()
        if not filename:
            messagebox.showwarning("Warning", "Please enter a map filename.")
            return
        self.node.set_map_parameter(filename, self.update_status)

    def on_start_row(self):
        def cb(success, msg):
            if success:
                self.btn_start.config(state=tk.DISABLED)
                self.btn_left.config(state=tk.NORMAL)
                self.btn_right.config(state=tk.NORMAL)
                self.btn_end.config(state=tk.NORMAL)
            self.update_status(success, msg)
        
        self.node.call_trigger(self.node.cli_start, "Start Row", cb)

    def on_end_row(self):
        def cb(success, msg):
            if success:
                self.btn_start.config(state=tk.NORMAL)
                self.btn_left.config(state=tk.DISABLED)
                self.btn_right.config(state=tk.DISABLED)
                self.btn_end.config(state=tk.DISABLED)
            self.update_status(success, msg)
            
        self.node.call_trigger(self.node.cli_end, "End Row", cb)

    def on_tree_left(self):
        self.node.call_trigger(self.node.cli_tree_left, "Tree Left", self.update_status)

    def on_tree_right(self):
        self.node.call_trigger(self.node.cli_tree_right, "Tree Right", self.update_status)

    def on_fence(self):
        self.node.call_trigger(self.node.cli_fence, "Fence Point", self.update_status)

    def on_start_mission(self):
        filename = self.ent_map.get()
        self.node.set_map_parameter(filename) # Set without waiting
        self.node.call_trigger(self.node.cli_start_mission, "Start Mission", self.update_status)

def main():
    rclpy.init()
    node = SurveyGui()
    
    # Run ROS spinner in a separate thread
    thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    thread.start()
    
    root = tk.Tk()
    app = App(root, node)
    root.mainloop()
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
