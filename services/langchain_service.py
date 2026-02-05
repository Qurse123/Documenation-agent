from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo")

prompt = ChatPromptTemplate.from_messages([  ## from messages is factory class method that excepts tuple of (role, "question"// {{}})
    ("system", "You are an assisant that only gives mean answers to normal questions longer than 10 charcters."),
    ("user", "{{ question }}")
], template_format="jinja2") ## this is the format you want the llm to use 

chain = prompt | llm  
"""
#| means pass the prompt which creates the message to as the input for hte llm to use
"""
