# Description:   This Dockerfile creates a image with compiled ROS packages.
#
# Company:       Robotnik Automation S.L.L.
# Creation Year: 2023
# Author:        Rafael Martin <rmartin@robotnik.es>
#
#
# Copyright (c) 2023, Robotnik Automation S.L.L.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Robotnik Automation S.L.L. nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Robotnik Automation S.L.L. BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Global ARGs
ARG output_path=/tmp
ARG output_pkg=${output_path}/deb.pkgs.tar
ARG base_image="robotnik/ros"
ARG ros_distro="use-args"
ARG image_base_version="use-args"
ARG version="use-args"
ARG ros_mirror="user-args"
ARG alpine_version="use-args"

FROM ${base_image}:${ros_distro}-base-${image_base_version} AS base

LABEL maintainer="rmartin@robotnik.es" \
      org.opencontainers.image.title="realsense-${ros_distro}" \
      org.opencontainers.image.version="${version} " \
    #   org.opencontainers.image.created="2023-04-18T07:42:19Z" \
      org.opencontainers.image.description="realsense" \
      org.opencontainers.image.source="https://github.com/RobotnikAutomation/" \
    #   org.opencontainers.image.revision="5674a2e5a89952c07b50b79144abafcc2ab9be9a" \
      org.opencontainers.image.vendor="Robotnik Automation S.L." \
      org.opencontainers.image.licenses="BSD-3-Clause" \
      org.opencontainers.image.authors="Rafael Martin <rmartin@robotnik.es>"

ENV DEBIAN_FRONTEND=noninteractive
ARG ros_mirror

FROM ${base_image}:${ros_distro}-builder-${image_base_version} AS builder

USER root
ENV DEBIAN_FRONTEND=noninteractive
ARG ros_mirror

# Install compiled packages
RUN --mount=type=bind,\
target=/tmp/requirements.txt,\
source=container/requirements/builder/packages.txt \
    true \
    && if \
        timeout 2 curl -IsS http://${ros_mirror} &>/dev/null; \
        then \
        sed -i \
            "s#packages.ros.org#${ros_mirror}#" \
            /etc/apt/sources.list.d/ros-latest.list ;\
        fi \
    && apt-fast update \
    && apt-fast install -q -y \
        --no-install-recommends \
        $(eval "echo $(cat /tmp/requirements.txt | xargs)") \
    && apt-get clean -q -y \
    && apt-get autoremove -q -y \
    && rm -rf /var/lib/apt/lists/* \
    && true

USER ${USER_NAME}

RUN --mount=type=bind,\
source=./robot_description.repo.yaml,\
target=/tmp/common.repo.yml,ro \
     vcs import \
        --input /tmp/common.repo.yml  \
        --shallow

COPY ../ src/

# Generate deb packages
RUN generate_debs.sh

ARG output_pkg
RUN tar -cvzf ${output_pkg} ./debs

FROM ${base_image}:${ros_distro}-builder-${image_base_version} AS compressed

ARG output_path
ARG output_pkg
COPY --from=builder ${output_pkg} ${output_path}/builder.pkgs.tar.gz

RUN find ${output_path} -name '*.pkgs.tar.gz' -exec tar -xvzf {} -C ${output_path} \;

# Generate Packages.gz
RUN cd ${output_path}/debs && dpkg-scanpackages . | gzip -9c > Packages.gz

# Compress all
RUN cd ${output_path} && tar -cvzf ${output_pkg} ./debs


# Output setup
FROM docker.io/library/alpine:${alpine_version} AS packages
RUN mkdir -p /data
WORKDIR /data
ARG output_pkg
COPY --from=compressed ${output_pkg} /data/debs.pkgs.tar.gz
ARG pkg_path=/data/debs.pkgs.tar.gz
RUN cd /data && tar -xf $pkg_path --strip-components=1

# Download gazebo models
FROM base

USER root
# Install dependancies
RUN \
    --mount=\
type=bind,\
target=/tmp/requirements.txt,\
source=container/requirements/base/packages.txt \
    true \
    && if \
        timeout 2 curl -IsS http://${ros_mirror} &>/dev/null; \
        then \
        sed -i \
            "s#packages.ros.org#${ros_mirror}#" \
            /etc/apt/sources.list.d/ros-latest.list ;\
        fi \
    && apt-get update \
    && apt-fast install -q -y \
        --no-install-recommends \
        $(eval "echo $(cat /tmp/requirements.txt | xargs)") \
    && sed -i "s#${ros_mirror}#packages.ros.org#" /etc/apt/sources.list.d/ros-latest.list \
    && apt-get clean -q -y \
    && apt-get autoremove -q -y \
    && rm -rf /var/lib/apt/lists/* \
    && true

# Install compiled packages
RUN \
    --mount=\
type=bind,\
from=packages,\
source=/data/debs,\
target=/tmp/debs \
    --mount=\
type=bind,\
target=/tmp/requirements.txt,\
source=container/requirements/local/packages.txt \
    true \
    && if \
        timeout 2 curl -IsS http://${ros_mirror} &>/dev/null; \
        then \
        sed -i \
            "s#packages.ros.org#${ros_mirror}#" \
            /etc/apt/sources.list.d/ros-latest.list ;\
        fi \
    && echo "deb [trusted=yes] file:///tmp/debs/ ./" | tee /etc/apt/sources.list.d/debs.list \
    && apt-get update \
    && apt-fast install -q -y \
        --no-install-recommends \
        $(eval "echo $(cat /tmp/requirements.txt | xargs)") \
    && sed -i "s#${ros_mirror}#packages.ros.org#" /etc/apt/sources.list.d/ros-latest.list \
    && apt-get clean -q -y \
    && apt-get autoremove -q -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm /etc/apt/sources.list.d/debs.list \
    && true


USER ${USER_NAME}

# ENV DEBUG_LAUNCH "-d"
ENV DEBUG_LAUNCH ""

# Set environment variables
ENV STARTUP_TYPE        "launch"
ENV ROS_BU_PKG          "robotnik_simple_twist_mux_bringup"
ENV ROS_BU_LAUNCH       "robotnik_twist_mux_launch.py ${DEBUG_LAUNCH}"

ENV ROS_DOMAIN_ID       "60"
ENV RMW_IMPLEMENTATION  "rmw_cyclonedds_cpp"

ENV ROBOT_ID            "robot"

# ENV LOG_LEVEL 'info',
# ENV NODE_NAME 'front_rgbd_camera',
# ENV DEVICE_TYPE 'd435',
# ENV SERIAL_NO '',
# ENV CAMERA_NAME 'front_camera',
# ENV CAMERA_BASE_FRAME 'camera_link',
# ENV CONFIG_PATH ,