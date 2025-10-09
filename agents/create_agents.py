
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

PROJECT_CONNECTION_STRING = "eastus.api.azureml.ms;95717284-5de1-45e3-a461-5fe0db848584;aoairg;azure-ai-projects-for-agents"
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=PROJECT_CONNECTION_STRING
)

with project_client:
    agent = project_client.agents.create_agent(
        model="gpt-4o-mini",
        name="my-agent",
        instructions="You are helpful agent",
    )
    print(f"Created agent, agent ID: {agent.id}")

    # Create a thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a message
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Who is PM of India?",
    )
    print(f"Created message, message ID: {message.id}")

    # Run the agent
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        print(f"Run failed: {run.last_error}")

    #Get messages from the thread
    messages = project_client.agents.list_messages(thread_id=thread.id)
    agent_response = messages.data[0].content[0].text.value
    print(f"Agent: {agent_response}")


    # Delete the agent once done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")
