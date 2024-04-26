cmake_minimum_required(VERSION 3.5)
project(robot_description NONE)

find_package(ament_cmake REQUIRED)
ament_package_xml()

install(
    DIRECTORY launch meshes urdf robots
    DESTINATION share/${PROJECT_NAME})

ament_package()
