# Copyright (c) 2022, Robotnik Automation S.L.L.
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

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, Command, FindExecutable
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.descriptions import ParameterValue
from robotnik_common.launch import ExtendedArgument, AddArgumentParser

def generate_launch_description():

    ld = LaunchDescription()
    add_to_launcher = AddArgumentParser(ld)

    arg = ExtendedArgument(
        name='robot_id',
        description='Robot ID',
        default_value='robot',
        use_env=True,
        environment='ROBOT_ID',
    )
    add_to_launcher.add_arg(arg)

    arg = ExtendedArgument(
        name='namespace',
        description='Namespace',
        default_value='robot',
        use_env=True,
        environment='NAMESPACE',
    )
    add_to_launcher.add_arg(arg)

    arg = ExtendedArgument(
        name='robot_model',
        description='Robot model',
        default_value='robot_description',
        use_env=True,
        environment='ROBOT_MODEL',
    )
    add_to_launcher.add_arg(arg)

    arg = ExtendedArgument(
        name='robot_xacro_package',
        description='Package where the xacro file is located',
        default_value='robot_description',
        use_env=True,
        environment='ROBOT_XACRO_PACKAGE',
    )
    add_to_launcher.add_arg(arg)

    arg = ExtendedArgument(
        name='robot_xacro_file',
        description='Name of the xacro file',
        default_value='versions/rb_kairos/rbkairos_base.urdf.xacro',
        use_env=True,
        environment='ROBOT_XACRO_FILE',
    )
    add_to_launcher.add_arg(arg)

    robot_xacro_package = LaunchConfiguration('robot_xacro_package')
    robot_xacro_file = LaunchConfiguration('robot_xacro_file')
    arg = ExtendedArgument(
        name='robot_xacro_path',
        description='Path to the xacro file',
        default_value=[FindPackageShare(robot_xacro_package), '/robots/', robot_xacro_file],
        use_env=True,
        environment='ROBOT_XACRO_PATH',
    )
    add_to_launcher.add_arg(arg)

    params = add_to_launcher.process_arg()

    robot_description_content = Command(
        [
            FindExecutable(name="xacro"),
            " ",
            params['robot_xacro_path'],
            " prefix:='robot_'",
        ]
    )
    robot_description_param = ParameterValue(robot_description_content, value_type=str)

    ld.add_action(Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        namespace=params['namespace'],
        output='screen',
        parameters=[
            {
              'robot_description': robot_description_param,
              'publish_frequency': 100.0,
              'frame_prefix': [params['robot_id'], '_'],
            }
        ],
    ))

    return ld


