FROM ubuntu:24.04

# Set the locale
RUN apt-get update && apt-get install -y locales && \
    locale-gen en_US en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 && \
    export LANG=en_US.UTF-8

# Set the timezone
ENV ROS_VERSION=2
ENV ROS_DISTRO=jazzy
ENV ROS_PYTHON_VERSION=3
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Setup the sources
RUN apt-get update && apt-get install -y software-properties-common curl && \
    add-apt-repository universe && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 packages
RUN apt-get update && apt-get upgrade -y && \
	apt-get install -y ros-${ROS_DISTRO}-desktop 

# ros pkgs
RUN apt-get install -y \
    ros-${ROS_DISTRO}-joint-state-publisher-gui \
    ros-${ROS_DISTRO}-xacro \
    ros-${ROS_DISTRO}-ros2-control \
    ros-${ROS_DISTRO}-rqt \
    ros-${ROS_DISTRO}-controller-manager \
    ros-${ROS_DISTRO}-controller-manager-msgs \
    ros-${ROS_DISTRO}-rqt-tf-tree \
    ros-${ROS_DISTRO}-urdf-tutorial  \
    ros-${ROS_DISTRO}-ros2-controllers

    
# image-transport
RUN apt-get install -y ros-${ROS_DISTRO}-image-transport
 
# Gazebo Harmonic for Jazzy distro
RUN apt-get install -y ros-${ROS_DISTRO}-ros-gz* \
    ros-${ROS_DISTRO}-gz-ros2-control

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-rosinstall-generator \
    build-essential

# Install ros2 navigation stack
RUN apt install -y ros-${ROS_DISTRO}-navigation2 \
    ros-${ROS_DISTRO}-nav2-bringup \
    ros-${ROS_DISTRO}-turtlebot3*

RUN apt install iputils-ping -y
RUN apt install nano -y

# Create a user to match the host uid 
ARG USERNAME=ros
ARG USER_ID=1001
ARG USER_GID=${USER_ID}

RUN groupadd --gid ${USER_GID} ${USERNAME} \
    && useradd -s /bin/bash --uid ${USER_ID} --gid ${USER_GID} -m ${USERNAME} \ 
    && mkdir /home/$USERNAME/.config && chown $USER_ID:$USER_GID /home/$USERNAME/.config

# Customization
WORKDIR /root

WORKDIR /root/ros_ws

# Source the inner layer
RUN /bin/bash -c "source /opt/ros/$ROS_DISTRO/setup.bash"

# Add the source command to .bashrc
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> /root/.bashrc

# Define the ENV variables
ENV PYTHONPATH=${PYTHONPATH}:/opt/ros/$ROS_DISTRO/lib/py

ENV CMAKE_PREFIX_PATH=$CMAKE_PREFIX_PATH:/opt/ros/$ROS_DISTRO
ENV CMAKE_MODULE_PATH=/opt/ros/$ROS_DISTRO/share/ament_cmake/cmake
ENV CMAKE_MAKE_PROGRAM=/usr/bin/make
ENV CMAKE_C_COMPILER=/usr/bin/gcc
ENV CMAKE_CXX_COMPILER=/usr/bin/g++

ENV ROS_DOMAIN_ID=5
# Set the ament_cmake_DIR variable
ENV ament_cmake_DIR /opt/ros/$ROS_DISTRO/share/ament_cmake/cmake

# Initialize the ws
RUN colcon build

# source the first layer
RUN /bin/bash -c "source install/local_setup.bash"

#COPY ros2_entrypoint.sh /root/.
#ENTRYPOINT ["/root/ros2_entrypoint.sh"]
CMD ["bash"]
