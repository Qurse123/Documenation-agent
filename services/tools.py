from langchain_core.tools import tool 
from datetime import datetime


@tool
def add_nums(a: int, b: int ) -> int:
    """Add two numbers togther use when needing to add """
    return a + b

@tool
def get_time() -> str:
    """Get the current date"""
    return datetime.now().strftime("%H:%M:%S")


