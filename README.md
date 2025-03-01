# ROS Docker

A Python-based CLI tool to generate Docker environments for various ROS (Robot Operating System) distributions.

Easily create and configure containerized ROS environments with customizable settings.

## Prerequisites

Ensure you have the following installed and configured:

- [Docker](https://docs.docker.com/engine/install/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#) (required if using NVIDIA GPU)
- [uv](https://docs.astral.sh/uv/) (optional and recommended)

## Get Started

### Clone the Repository

```bash
git clone https://github.com/xiaosq2000/ros-docker.git
cd ros-docker
```

> [!NOTE]
> If `uv` is unavailable:
> 1. Install the dependencies at first:
>  ```bash
>  python -m venv .venv
>  source .venv/bin/activate
>  pip install -e .
>  ```
> 2. In the following shell commands, use `python` instead of `uv run`.

### List Available ROS Distributions

To see all available ROS distributions that can be generated:
```bash
uv run ros-docker.py list
```

[![asciicast-list](https://asciinema.org/a/lV1pG47m55K2QqsFPQHpZcjIl.svg)](https://asciinema.org/a/lV1pG47m55K2QqsFPQHpZcjIl)

Take ROS1 Noetic as an example.

### Generate Docker Files

Generate Docker files for a specific ROS distribution:

```bash
uv run ros-docker.py generate noetic
```

[![asciicast-generate](https://asciinema.org/a/9SKLe3k4ZMxfw279FfsKTJ7yV.svg)](https://asciinema.org/a/9SKLe3k4ZMxfw279FfsKTJ7yV)

> [!TIP]
> 1. Preview the generated files without saving them:
>    ```bash
>    uv run ros-docker.py generate noetic --preview
>    ```
> 2. Specify a custom output directory (default: './generated'):
>    ```bash
>    uv run ros-docker.py generate noetic --output-dir ./generated/noetic 
>    ```

### Build and Run

```sh
cd generated
docker compose -f docker-compose.noetic.yml up --build -d
```

[![asciicast-build-and-run](https://asciinema.org/a/wFgrt0IjXlMZXaJ8RX1bChstQ.svg)](https://asciinema.org/a/wFgrt0IjXlMZXaJ8RX1bChstQ)

### Interact with the Container

```sh
docker exec -it ros-noetic-container bash
```

[![asciicast-roscore](https://asciinema.org/a/aJK3gOdr6wcnR0SFCqGYILBWW.svg)](https://asciinema.org/a/aJK3gOdr6wcnR0SFCqGYILBWW)

## Customization

### Base Docker Images

You can customize the Docker environment by editing the YAML configuration files in the `configs` directory. Each ROS distribution has its own configuration file, e.g., `configs/ros_noetic.yaml`.

### Development Docker Images

The tool supports creating development environments with custom tooling and configurations through development profiles.

Create your own development profiles by adding YAML files to the `configs/dev_profiles/` directory.

```bash
uv run ros-docker.py list-profiles
uv run ros-docker.py generate-dev <ros-distro> --profile <your-profile>
```
