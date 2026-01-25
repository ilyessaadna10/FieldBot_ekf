cmake_minimum_required(VERSION 3.8)
project(bakus_bot)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 1. FIND DEPENDENCIES
find_package(ament_cmake REQUIRED)

# 2. INSTALL DIRECTORIES (The Shipping Manifest)
# This moves your files from src to install/share so ROS can see them.
install(DIRECTORY
  launch
  urdf
  params
  worlds
  config   # Added this for ros2_control
  maps     # Added this for future map saving
  rviz     # Custom RViz configs
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()