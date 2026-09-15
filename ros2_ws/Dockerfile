FROM ghcr.io/sloretz/ros:humble-desktop

ARG ROS_WS=/home/ros_user/ws

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-pip \
        python3-serial \
    && pip3 install --no-cache-dir inputs pyserial \
    && rm -rf /var/lib/apt/lists/*

WORKDIR ${ROS_WS}
COPY src/ ${ROS_WS}/src/

RUN /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"

CMD ["/bin/bash"]
