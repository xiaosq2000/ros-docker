#!/bin/bash
set -e

# Source ROS environment

source /opt/ros/noetic/setup.bash


# Source workspace if it exists and has been built
if [ -f "/ros_ws/devel/setup.bash" ]; then
	source "/ros_ws/devel/setup.bash"
elif [ -f "/ros_ws/install/setup.bash" ]; then
	source "/ros_ws/install/setup.bash"
fi

# Execute the command passed to the container
exec "$@"