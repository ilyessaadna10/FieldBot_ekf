#!/usr/bin/env python3
import math
import os

def generate_sdf(output_path):
    sdf_header = """<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="vineyard_variable">
    <physics name="1ms" type="ignored">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>
    <plugin filename="libgz-sim-physics-system.so" name="gz::sim::systems::Physics"></plugin>
    <plugin filename="libgz-sim-user-commands-system.so" name="gz::sim::systems::UserCommands"></plugin>
    <plugin filename="libgz-sim-scene-broadcaster-system.so" name="gz::sim::systems::SceneBroadcaster"></plugin>
    <plugin filename="libgz-sim-sensors-system.so" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>
    <plugin filename="libgz-sim-imu-system.so" name="gz::sim::systems::Imu"></plugin>
    <plugin filename="libgz-sim-navsat-system.so" name="gz::sim::systems::NavSat"></plugin>
    <plugin filename="libgz-sim-magnetometer-system.so" name="gz::sim::systems::Magnetometer"></plugin>

    <spherical_coordinates>
      <surface_model>EARTH_WGS84</surface_model>
      <world_frame_orientation>ENU</world_frame_orientation>
      <latitude_deg>43.610769</latitude_deg> <!-- Example: Southern France Vineyard -->
      <longitude_deg>3.876716</longitude_deg>
      <elevation>0</elevation>
      <heading_deg>0</heading_deg>
    </spherical_coordinates>

    <light name="sun" type="directional">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>100</mu>
                <mu2>50</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <cast_shadows>false</cast_shadows>
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.3 0.5 0.2 1</ambient>
            <diffuse>0.3 0.5 0.2 1</diffuse>
          </material>
        </visual>
      </link>
    </model>
"""

    sdf_footer = """
  </world>
</sdf>
"""

    vine_template = """
    <model name="vine_{idx}">
      <static>true</static>
      <pose>{x} {y} 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>0.05</radius>
              <length>1.0</length>
            </cylinder>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.05</radius>
              <length>1.0</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0.4 0.2 0.1 1</ambient>
            <diffuse>0.4 0.2 0.1 1</diffuse>
          </material>
        </visual>
      </link>
    </model>
"""

    # Parameters
    num_alleys = 3
    row_spacing = 4.0
    row_length = 24.0
    vine_spacing = 0.9 # 1.5 * 0.6 (robot width)
    amplitude = 0.4
    frequency = 0.4

    vines_sdf = ""
    idx = 0
    
    # Generate tree rows (num_alleys + 1 rows of trees create num_alleys gaps)
    for r in range(num_alleys + 1):
        # We shift the rows by half the spacing so the robot (at y=0) 
        # is in the center of the first alley.
        row_center_y = (r - 0.5) * row_spacing
        # Alternate phase to make the alley width change dynamically
        # even if both rows are "wavy"
        phase_shift = math.pi if r % 2 == 0 else 0
        
        for x in [i * vine_spacing for i in range(int(row_length / vine_spacing))]:
            # Variation makes the tree row "wavy"
            variation = math.sin(x * frequency + phase_shift) * amplitude
            
            vines_sdf += vine_template.format(idx=idx, x=x, y=row_center_y + variation)
            idx += 1

    with open(output_path, 'w') as f:
        f.write(sdf_header + vines_sdf + sdf_footer)

if __name__ == "__main__":
    output_path = os.path.expanduser("~/Desktop/ros2project/nav2/bakus_ws/src/fieldbot/worlds/vineyard_variable.sdf")
    generate_sdf(output_path)
    print(f"Generated {output_path}")
