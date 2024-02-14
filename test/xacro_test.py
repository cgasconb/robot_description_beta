"""Xacro test module."""

import os
import shutil
import subprocess
import tempfile

from ament_index_python.packages import get_package_share_directory


def check_xacro_file(name: str):
    """Check if the xacro file is valid."""

    description_path = os.path.join(
        get_package_share_directory("robot_description"),
        "robots",
        name,
    )

    _, urdf_file = tempfile.mkstemp(suffix=".urdf")
    xacro_command = f"{shutil.which('xacro')}" f" {description_path}" f" > {urdf_file}"
    urdf_command = f"{shutil.which('check_urdf')}" f" {urdf_file}"

    try:
        xacro_process = subprocess.run(
            xacro_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            check=False,
        )

        if xacro_process.returncode != 0:
            print(xacro_process.stdout.decode("utf-8"))
            print(xacro_process.stderr.decode("utf-8"))

        assert xacro_process.returncode == 0, "Xacro process failed!"

        urdf_process = subprocess.run(
            urdf_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            check=False,
        )

        if urdf_process.returncode != 0:
            print(urdf_process.stdout.decode("utf-8"))
            print(urdf_process.stderr.decode("utf-8"))

        assert urdf_process.returncode == 0, "URDF process failed!"

    finally:
        os.remove(urdf_file)


def test_xacro_default():
    """Test xacro default."""
    check_xacro_file("default.urdf.xacro")


def test_xacro_default_with_sensors():
    """Test xacro default with sensors."""
    check_xacro_file("default_with_sensors.urdf.xacro")


if __name__ == "__main__":
    test_xacro_default()
    test_xacro_default_with_sensors()
