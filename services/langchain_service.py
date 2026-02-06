from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Set up template loading
PROJECT_ROOT = Path(__file__).parent.parent
jinja_env = Environment(loader=FileSystemLoader(PROJECT_ROOT / "prompts"))

# Load template by name
assert jinja_env.loader is not None
template_content, _, _ = jinja_env.loader.get_source(jinja_env, "doc_agent.jinja2")

llm = ChatOpenAI(model="gpt-3.5-turbo")
prompt = PromptTemplate.from_template(template_content, template_format="jinja2")
chain = prompt | llm
