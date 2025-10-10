
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
load_dotenv('agents.env')

# Create an AIProjectClient from an endpoint, copied from your Azure AI Foundry project.
# You need to login to Azure subscription via Azure CLI and set the environment variables
project_endpoint = os.environ["PROJECT_ENDPOINT"]  # Ensure the PROJECT_ENDPOINT environment variable is set

# Create an AIProjectClient instance
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),  # Use Azure Default Credential for authentication
)

with project_client:
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],  # Model deployment name
        name="my-agent",  # Name of the agent
        instructions="You are helpful agent",
    )
    print(f"Created agent, agent ID: {agent.id}")

    # Create a thread
    thread = project_client.agents.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a message
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="Who is CEO of Amazon?",
    )
    print(f"Created message, message ID: {message.id}")

    # Run the agent
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        print(f"Run failed: {run.last_error}")

    #Get messages from the thread
    messages = project_client.agents.messages.list(thread_id=thread.id)
    #agent_response = messages[0].content[0].text.value # messages.data[0].content[0].text.value
    #print(f"Agent: {agent_response}")
    for message in messages:
    # If content is a list of parts (common in Azure SDKs)
        if message.role == "assistant":
            for part in message.content:
                if hasattr(part, "text"):
                    print(f"Agent response: {part.text.value}")
                else:
                    print(f"Agent response: {part}")


    # Delete the agent once done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")
