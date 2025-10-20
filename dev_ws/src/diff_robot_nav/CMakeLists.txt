cmake_minimum_required(VERSION 3.8)
project(diff_robot_nav)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(navigation2 REQUIRED)
find_package(nav2_bringup REQUIRED)
find_package(slam_toolbox REQUIRED)
find_package(robot_localization REQUIRED)
find_package(geometry_msgs REQUIRED)

add_executable(cmd_vel_remapper src/remapper.cpp)

ament_target_dependencies(cmd_vel_remapper rclcpp geometry_msgs)

install(
  TARGETS cmd_vel_remapper
  DESTINATION lib/${PROJECT_NAME}
  )

install(
  DIRECTORY config maps launch rviz
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
