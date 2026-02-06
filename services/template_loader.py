from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Set up Jinja2 to load from prompts/ folder
env = Environment(
    loader=FileSystemLoader(PROJECT_ROOT / "prompts")
)

def load_template(template_name: str) -> str:
    """Load a template from the prompts folder."""
    template = env.get_template(template_name)
    return template.render()  # Returns the rendered string