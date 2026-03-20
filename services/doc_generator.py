import logging
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, BaseLoader
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from memory.state import DocAgentState

load_dotenv()

logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"

# Template loader
_loader: BaseLoader = FileSystemLoader(PROMPTS_DIR)
jinja_env = Environment(loader=_loader)


def _build_prompt(state: DocAgentState) -> str:
    """Render the Jinja2 prompt template with session state data.

    We use the Jinja environment and get_template() to load doc_agent.jinja2.
    We pass state (DocAgentState) by rendering the template with transcript (str)
    and screenshots (list of Screenshot dicts), and return the rendered string.
    """
    template = jinja_env.get_template("doc_agent.jinja2")
    return template.render(
        transcript=state["transcript"],
        screenshots=state["screenshots"],
    )


def _build_vision_messages(state: DocAgentState, prompt_text: str) -> list[HumanMessage]:
    """
    Build messages for the Vision API.
    Includes the text prompt and screenshot images so the LLM
    can actually see what was on screen.

    Screenshots are already base64-encoded in memory (image_data field),
    so no file I/O is needed here.
    "screenshots" is a key dict that allows you to acess the list of screenshots in state.py
    """
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt_text}]

    for i, shot in enumerate(state["screenshots"]):
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{shot['image_data']}",
                "detail": "low",
            },
        })
        logger.debug("Attached screenshot %d (timestamp: %s)", i + 1, shot["timestamp"])

    return [HumanMessage(content=content)]  # type: ignore[arg-type]


async def generate_documentation(state: DocAgentState) -> str:
    """
    Generate documentation from a completed session state.

    Takes the transcript and screenshots, sends them to GPT-4 Vision,
    and returns structured Markdown documentation.

    Args:
        state: Completed DocAgentState with screenshots and transcript.

    Returns:
        Generated documentation as a Markdown string.
    """
    logger.info(
        "Generating documentation from %d screenshots and %d chars of transcript",
        len(state["screenshots"]),
        len(state["transcript"]),
    )

    # Build the text prompt from template
    prompt_text = _build_prompt(state)

    # Build vision messages with embedded screenshots
    messages = _build_vision_messages(state, prompt_text)

    # Use GPT-4o for vision capabilities
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    logger.info("Sending to LLM for documentation generation...")
    response = await llm.ainvoke(messages)

    documentation = str(response.content)
    logger.info("Documentation generated. Length: %d chars", len(documentation))

    return documentation
