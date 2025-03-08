import os
import yaml
from .utils import render_template


def generate_env_file(output_dir, save=True):
    # Generate .env
    output_path = f"{output_dir}/.env"
    env_file_content = f"""COMPOSE_BAKE=true
UID={os.getuid()}
GID={os.getgid()}
"""
    if save:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(env_file_content)

    return env_file_content


def generate_dockerfile(output_dir, ros_distro, template="Dockerfile.j2", save=True):
    config_file = f"configs/ros_{ros_distro}.yaml"
    output_dockerfile = f"{output_dir}/Dockerfile.{ros_distro}"
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"{config_file} not found.")
        exit(1)

    return render_template(template, config, output_dockerfile, save)


def generate_docker_compose(output_dir, ros_distro, save=True):
    config_file = f"configs/ros_{ros_distro}.yaml"
    output_docker_compose = f"{output_dir}/docker-compose.{ros_distro}.yml"
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"{config_file} not found.")
        exit(1)

    return render_template("docker-compose.yml.j2", config, output_docker_compose, save)
