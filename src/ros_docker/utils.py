import os
from jinja2 import Environment, FileSystemLoader


def get_available_ros_distros():
    """Get list of available ROS distributions from config files."""
    configs = [
        f.replace("ros_", "").replace(".yaml", "")
        for f in os.listdir("configs")
        if f.startswith("ros_") and f.endswith(".yaml")
    ]
    return sorted(configs)


def get_available_dev_profiles():
    """Get list of available development profiles from config files."""
    profiles = [
        f.replace(".yaml", "")
        for f in os.listdir("configs/dev_profiles")
        if f.endswith(".yaml")
    ]
    return sorted(profiles)


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
