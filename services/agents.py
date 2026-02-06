from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

from services.tools import add_nums, get_time

load_dotenv()

# 1. Create the LLM
llm = ChatOpenAI(model="gpt-3.5-turbo")

# 2. Define available tools
tools = [add_nums, get_time]

# 3. Create the agent (langgraph handles prompt internally)
agent_executor = create_react_agent(llm, tools)