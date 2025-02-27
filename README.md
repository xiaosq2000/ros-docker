# ROS Docker

A Python-based tool to generate Docker environments for ROS (Robot Operating System) distributions. Easily create and configure containerized ROS environments with customizable settings.

## Features

- Generate Dockerfiles and docker-compose configurations for different ROS distributions
- Support for X11 forwarding for GUI applications
- NVIDIA GPU support for hardware acceleration
- D-Bus integration for system communications
- Customizable system packages and environment variables

## Prerequisites

Ensure you have the following installed and configured:

- [Docker](https://docs.docker.com/engine/install/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#) (required if using NVIDIA GPU support)
- [uv](https://docs.astral.sh/uv/) (optional while highly recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/xiaosq2000/ros-docker.git
   cd ros-docker
   ```

2. If `uv` is not installed, use `pip` to install the dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

## Usage

> [!TIP]
> In the following shell commands, use `uv run` instead of `python` if `uv` is available.

### List Available ROS Distributions

To see all available ROS distributions that can be generated:
```bash
python ros-docker.py list
```

### Generate Docker Files

Generate Docker files for a specific ROS distribution:

```bash
python ros-docker.py generate noetic
```

> [!TIP]
> 1. Preview the generated files without saving them:
>    ```bash
>    python ros-docker.py generate noetic --preview
>    ```
> 2. Specify a custom output directory:
>    ```bash
>    python ros-docker.py generate noetic --output-dir my_ros_docker
>    ```

## Customization

You can customize the Docker environment by editing the YAML configuration files in the `configs` directory. Each ROS distribution has its own configuration file, e.g., `configs/ros_noetic.yaml`.

