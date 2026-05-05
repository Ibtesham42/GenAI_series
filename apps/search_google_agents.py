from dotenv import load_dotenv
load_dotenv()
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

llm = ChatGroq(model="openai/gpt-oss-20b")
search =GoogleSerperAPIWrapper()


agent  = create_agent(model=llm, 
                      tools=[search.run],
                      system_prompt="You are a helpful assistant that can answer questions by searching the web.",
                      checkpointer=MemorySaver() 
                      )

while True:
    query = input("User: ")
    if query.lower() in ['exit', 'quit']:
        print("Exiting the agent. Goodbye!")
        break
    response = agent.invoke({'messages':[{'role':'user', 'content':query}]},
    {'configurable':{'thread_id': '1'}}                     
    )

    print("Agent:", response['messages'][-1].content)