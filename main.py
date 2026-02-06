from services.agents import agent_executor

# Test the agent with a math question
response = agent_executor.invoke({"messages": [("user", "What is 5 + 3?")]})

# Print the last message (the agent's response)
print(response["messages"][-1].content)
