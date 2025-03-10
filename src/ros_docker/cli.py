#!/usr/bin/env python3
import os
import yaml
import click
import git
import toml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from jinja2 import Environment, FileSystemLoader
from .utils import (
    get_available_ros_distros,
    get_available_dev_profiles,
    render_template,
)
from .generate import (
    generate_env_file,
    generate_dockerfile,
    generate_docker_compose,
)

# Initialize Rich console
console = Console()


@click.group(
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.version_option(
    version=toml.load(
        os.path.join(
            git.Repo(search_parent_directories=True).working_tree_dir, "pyproject.toml"
        )
    )["project"]["version"]
)
@click.pass_context
def main(ctx):
    """Generate Docker files for ROS (Robot Operating System) distributions."""
    # If no command is provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(main.get_help(ctx))


@main.command("list")
def list_distributions():
    """List available ROS distributions."""
    distributions = get_available_ros_distros()

    # Create a table to display available distributions
    table = Table(title="Available ROS Distributions")
    table.add_column("Distribution", style="cyan")
    table.add_column("Base Image", style="green")
    table.add_column("ROS Package", style="yellow")

    for distro in distributions:
        try:
            with open(f"configs/ros_{distro}.yaml", "r") as f:
                config = yaml.safe_load(f)
                table.add_row(
                    distro,
                    config.get("base_image", "N/A"),
                    config.get("ros_package", "N/A"),
                )
        except FileNotFoundError:
            table.add_row(distro, "N/A", "N/A")

    console.print(table)


@main.command("generate")
@click.argument("ros_distro", required=True)
@click.option(
    "--output-dir",
    "-o",
    default="generated",
    help="Output directory for generated files.",
)
@click.option(
    "--preview", "-p", is_flag=True, help="Preview the generated files without saving."
)
def generate(ros_distro, output_dir, preview):
    """Generate Docker files for a specific ROS distribution."""
    # Check if the ROS distribution is available
    available_distros = get_available_ros_distros()
    if ros_distro not in available_distros:
        console.print(
            f"[bold red]Error:[/bold red] ROS distribution '[bold cyan]{ros_distro}[/bold cyan]' not found."
        )
        console.print(
            f"Available distributions: {', '.join(['[bold cyan]' + d + '[/bold cyan]' for d in available_distros])}"
        )
        return

    if preview:
        console.print(
            Panel.fit(
                "[bold green]Preview Mode[/bold green] - Files will not be saved",
                title="Preview",
            )
        )

    # Generate Dockerfile
    dockerfile_content = generate_dockerfile(
        output_dir=output_dir, ros_distro=ros_distro, save=not preview
    )

    # Generate docker-compose.yml
    docker_compose_content = generate_docker_compose(
        output_dir=output_dir, ros_distro=ros_distro, save=not preview
    )

    # Generate .env
    env_file_content = generate_env_file(output_dir=output_dir, save=not preview)

    if preview:
        console.print(
            Panel(
                Syntax(
                    dockerfile_content, "dockerfile", theme="monokai", line_numbers=True
                ),
                title=f"Dockerfile.{ros_distro}",
                subtitle="Preview",
            )
        )
        console.print(
            Panel(
                Syntax(
                    docker_compose_content, "yaml", theme="monokai", line_numbers=True
                ),
                title=f"docker-compose.{ros_distro}.yml",
                subtitle="Preview",
            )
        )
        console.print(
            Panel(
                Syntax(env_file_content, "sh", theme="monokai", line_numbers=True),
                title=".env",
                subtitle="Preview",
            )
        )
    else:
        generated_file_paths = [
            f"{output_dir}/Dockerfile.{ros_distro}",
            f"{output_dir}/docker-compose.{ros_distro}.yml",
            f"{output_dir}/.env",
        ]

        # Create a table to display generated files
        table = Table(title="Generated Files")
        table.add_column("File", style="cyan")
        table.add_column("Path", style="green")

        for file in generated_file_paths:
            table.add_row(os.path.basename(file), file)

        console.print(table)

        # Next steps
        console.print(
            Panel.fit(
                "[green]# build and run[/green]\n"
                f"cd {output_dir}\n"
                f"docker compose -f docker-compose.{ros_distro}.yml up --build -d\n"
                "[green]# interact with the container[/green]\n"
                f"docker exec -it ros-{ros_distro}-container bash",
                title="Next Steps",
            )
        )

    # # TODO:
    # # Generate entrypoint.sh
    # if config.get("entrypoint"):
    #     output_entrypoint = f"{output_dir}/{config['entrypoint']}"
    #     if preview:
    #         env = Environment(loader=FileSystemLoader("templates"))
    #         template = env.get_template("entrypoint.sh.j2")
    #         output = template.render(**config)
    #         console.print(
    #             Panel(
    #                 Syntax(output, "bash", theme="monokai", line_numbers=True),
    #                 title=config["entrypoint"],
    #                 subtitle="Preview",
    #             )
    #         )
    #     else:
    #         generated_files.append(
    #             render_template("entrypoint.sh.j2", config, output_entrypoint)
    #         )
    #         # Make entrypoint executable
    #         os.chmod(output_entrypoint, 0o755)


@main.command("list-profiles")
def list_dev_profiles():
    """List available development profiles."""
    profiles = get_available_dev_profiles()

    # Create a table to display available profiles
    table = Table(title="Available Development Profiles")
    table.add_column("Profile", style="cyan")
    table.add_column("Packages", style="green")
    table.add_column("URL", style="magenta")

    for profile in profiles:
        try:
            with open(f"configs/dev_profiles/{profile}.yaml", "r") as f:
                config = yaml.safe_load(f)
                table.add_row(
                    profile,
                    ", ".join(config.get("dev_packages", [])[:3])
                    + ("..." if len(config.get("dev_packages", [])) > 3 else ""),
                    config.get("url"),
                )
        except FileNotFoundError:
            table.add_row(profile, "N/A")

    console.print(table)


@main.command("generate-dev")
@click.argument("ros_distro", required=True)
@click.option(
    "--profile",
    "-p",
    default="default",
    help="Development profile to use.",
)
@click.option(
    "--output-dir",
    "-o",
    default="generated",
    help="Output directory for generated files.",
)
@click.option(
    "--preview", is_flag=True, help="Preview the generated files without saving."
)
def generate_dev(ros_distro, profile, output_dir, preview):
    """Generate development Docker files for a specific ROS distribution."""
    # Check if the ROS distribution is available
    available_distros = get_available_ros_distros()
    if ros_distro not in available_distros:
        console.print(
            f"[bold red]Error:[/bold red] ROS distribution '[bold cyan]{ros_distro}[/bold cyan]' not found."
        )
        return

    # Check if the development profile is available
    available_profiles = get_available_dev_profiles()
    if profile not in available_profiles:
        console.print(
            f"[bold red]Error:[/bold red] Development profile '[bold cyan]{profile}[/bold cyan]' not found."
        )
        return

    # Load the ROS config
    with open(f"configs/ros_{ros_distro}.yaml", "r") as f:
        ros_config = yaml.safe_load(f)

    # Load the development profile
    with open(f"configs/dev_profiles/{profile}.yaml", "r") as f:
        dev_config = yaml.safe_load(f)

    # Merge configurations
    config = {**ros_config, **dev_config}

    # Override image name for the development image
    config["base_image_name"] = ros_config["image_name"]
    config["image_name"] = f"{ros_config['image_name']}-{profile}"
    config["container_name"] = f"{ros_config['container_name']}-{profile}"

    # Generate Dockerfile.dev
    output_dockerfile = f"{output_dir}/Dockerfile.{ros_distro}.{profile}"
    if preview:
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("Dockerfile.dev.j2")
        output = template.render(**config)
        console.print(
            Panel(
                Syntax(output, "dockerfile", theme="monokai", line_numbers=True),
                title=f"Dockerfile.{ros_distro}.{profile}",
                subtitle="Preview",
            )
        )
    else:
        render_template("Dockerfile.dev.j2", config, output_dockerfile)

    # Update docker-compose to use the dev image
    config["dockerfile_path"] = f"Dockerfile.{ros_distro}.{profile}"
    output_compose = f"{output_dir}/docker-compose.{ros_distro}.{profile}.yml"
    if preview:
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("docker-compose.yml.j2")
        output = template.render(**config)
        console.print(
            Panel(
                Syntax(output, "yaml", theme="monokai", line_numbers=True),
                title=f"docker-compose.{ros_distro}.{profile}.yml",
                subtitle="Preview",
            )
        )
    else:
        render_template("docker-compose.yml.j2", config, output_compose)

    if not preview:
        # Show next steps
        console.print(
            Panel.fit(
                f"[green]# build and run development environment[/green]\n"
                f"cd {output_dir}\n"
                f"docker compose -f docker-compose.{ros_distro}.{profile}.yml up --build -d",
                title="Next Steps",
            )
        )


if __name__ == "__main__":
    main()
