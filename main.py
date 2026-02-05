from services.langchain_service import chain

response = chain.invoke({"question": "hello say something nice"}) 

print(response.content)
