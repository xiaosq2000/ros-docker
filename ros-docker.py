#!/usr/bin/env python3
import os
import yaml
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from jinja2 import Environment, FileSystemLoader

# Initialize Rich console
console = Console()


def get_available_ros_distros():
    """Get list of available ROS distributions from config files."""
    configs = [
        f.replace("ros_", "").replace(".yaml", "")
        for f in os.listdir("configs")
        if f.startswith("ros_") and f.endswith(".yaml")
    ]
    return sorted(configs)


def render_template(template_file, config, output_file):
    """Render a Jinja2 template with the given config and save to output_file."""
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(template_file)

    # Render the template with the config
    output = template.render(**config)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write the rendered template to the output file
    with open(output_file, "w") as f:
        f.write(output)

    return output_file


@click.group(
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.version_option(version="1.0.0")
@click.pass_context
def cli(ctx):
    """Generate Docker files for ROS (Robot Operating System) distributions."""
    # If no command is provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(cli.get_help(ctx))


@cli.command("list")
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


@cli.command("generate")
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

    # Load the config for the specified ROS distribution
    config_file = f"configs/ros_{ros_distro}.yaml"
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            console.print(
                f"Loaded configuration for [bold cyan]{ros_distro}[/bold cyan]"
            )
    except FileNotFoundError:
        console.print(
            f"[bold red]Error:[/bold red] Config file not found for ROS distribution: [bold cyan]{ros_distro}[/bold cyan]"
        )
        return

    if preview:
        console.print(
            Panel.fit(
                "[bold green]Preview Mode[/bold green] - Files will not be saved",
                title="Preview",
            )
        )

    generated_files = []

    # Generate Dockerfile
    output_dockerfile = f"{output_dir}/Dockerfile.{ros_distro}"
    if preview:
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("Dockerfile.j2")
        output = template.render(**config)
        console.print(
            Panel(
                Syntax(output, "dockerfile", theme="monokai", line_numbers=True),
                title=f"Dockerfile.{ros_distro}",
                subtitle="Preview",
            )
        )
    else:
        generated_files.append(
            render_template("Dockerfile.j2", config, output_dockerfile)
        )

    # Generate docker-compose.yml
    output_compose = f"{output_dir}/docker-compose.{ros_distro}.yml"
    if preview:
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("docker-compose.yml.j2")
        output = template.render(**config)
        console.print(
            Panel(
                Syntax(output, "yaml", theme="monokai", line_numbers=True),
                title=f"docker-compose.{ros_distro}.yml",
                subtitle="Preview",
            )
        )
    else:
        generated_files.append(
            render_template("docker-compose.yml.j2", config, output_compose)
        )

    # Generate .env
    output_envfile = f"{output_dir}/.env"
    env_content = f"""COMPOSE_BAKE=true
UID={os.getuid()}
GID={os.getgid()}
"""

    if preview:
        console.print(
            Panel(
                Syntax(env_content, "bash", theme="monokai", line_numbers=True),
                title=".env",
                subtitle="Preview",
            )
        )
    else:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_envfile), exist_ok=True)

        with open(output_envfile, "w") as f:
            f.write(env_content)
        generated_files.append(output_envfile)

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

    if not preview and generated_files:
        # Create a table to display generated files
        table = Table(title="Generated Files")
        table.add_column("File", style="cyan")
        table.add_column("Path", style="green")

        for file in generated_files:
            table.add_row(os.path.basename(file), file)

        console.print(table)

        # Show next steps
        console.print(
            Panel.fit(
                f"[bold green]Next Steps:[/bold green]\n"
                f"cd {output_dir}\n"
                f"docker compose -f docker-compose.{ros_distro}.yml up --build",
                title="Build and Run",
            )
        )


if __name__ == "__main__":
    cli()
