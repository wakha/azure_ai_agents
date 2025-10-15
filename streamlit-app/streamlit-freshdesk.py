import os
import json
import requests
import streamlit as st
from azure.ai.projects import AIProjectClient
from azure.identity import ClientSecretCredential
from azure.ai.agents.models import FunctionTool, ToolSet
from dotenv import load_dotenv
from typing import Any, Callable, Set
from datetime import datetime

# Load environment variables
load_dotenv('api_settings.env')

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Streamlit layout config
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# --- Banner Header ---
st.markdown("""
    <style>
        .banner {
            background-color: #f3f8fe;
            padding: 2rem 1rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .banner-title {
            font-size: 2rem;
            font-weight: 700;
            color: #0078D4;
            margin-bottom: 0.5rem;
        }
        .banner-description {
            font-size: 1.1rem;
            color: #555;
        }
        .agent-image {
            max-height: 150px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Replace with your image if needed
image_url = "https://images.pexels.com/photos/3184419/pexels-photo-3184419.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"

st.markdown(f"""
    <div class="banner">
        <div>
            <div class="banner-title">💬 Freshdesk AI Agent</div>
            <div class="banner-description">
                Instantly assist customers and create Freshdesk tickets with our smart AI support assistant.
            </div>
        </div>
        <img src="{image_url}" class="agent-image" alt="Support Agent">
    </div>
""", unsafe_allow_html=True)

# Sidebar Header
st.sidebar.header("Chat with Agent")

# CSS for Chat UI
st.markdown("""
    <style>
        .chat-container {
            display: flex;
            align-items: flex-start;
            margin-bottom: 15px;
            gap: 10px;
        }
        .chat-container.user { justify-content: flex-start; }
        .chat-container.agent { justify-content: flex-end; }
        .chat-bubble {
            padding: 10px;
            border-radius: 10px;
            max-width: 70%;
            word-wrap: break-word;
        }
        .user-bubble { background-color: #DCF8C6; margin-right: auto; }
        .agent-bubble { background-color: #E8E8E8; margin-left: auto; }
        .avatar {
            width: 40px; height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: white;
            flex-shrink: 0;
        }
        .user-avatar { background-color: #4CAF50; order: -1; }
        .agent-avatar { background-color: #2196F3; order: 1; }
        .message-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .fixed-input {
            position: fixed;
            bottom: 0; left: 0; right: 0;
            background-color: white;
            padding: 1rem;
            border-top: 1px solid #ddd;
            z-index: 1000;
        }
        .main { padding-bottom: 80px; }
        [data-testid="stVerticalBlock"] { padding-bottom: 80px; }
    </style>
""", unsafe_allow_html=True)

# Chat containers
chat_container = st.container()
input_container = st.container()

# Session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Freshdesk Ticket Creator
def create_freshdesk_ticket(email: str, subject: str) -> str:
    FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN")
    FRESHDESK_API_KEY = os.getenv("FRESHDESK_API_KEY")
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets"
    
    ticket_data = {
        "email": email,
        "subject": subject,
        "description": "This is a test ticket created via Azure AI Agent.",
        "priority": 2,
        "status": 2,
        "tags": ["API", "Python"]
    }
    
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    
    response = requests.post(url, auth=(FRESHDESK_API_KEY, "X"), headers=headers, data=json.dumps(ticket_data))
    
    if response.status_code == 201:
        return json.dumps(response.json(), indent=4)
    else:
        return json.dumps({"error": response.text, "status_code": response.status_code}, indent=4)

# Toolset and Azure agent
user_functions: Set[Callable[..., Any]] = {create_freshdesk_ticket}

credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

project_client = AIProjectClient(
    credential=credential,
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    #subscription_id=os.getenv("SUBSCRIPTION_ID"),
    #resource_group_name=os.getenv("RESOURCE_GRPUP"),
    #project_name=os.getenv("PROJECT_NAME"),
)

#project_client = AIProjectClient(
#    subscription_id=os.getenv("SUBSCRIPTION_ID"),
#    resource_group_name=os.getenv("RESOURCE_GRPUP"),
#    project_name=os.getenv("PROJECT_NAME"),
#    credential=credential
#)

functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)
project_client.agents.enable_auto_function_calls(tools=toolset)

agent = project_client.agents.create_agent(
    model=os.getenv("MODEL_DEPLOYMENT_NAME"),
    name="freshdesk-agent",
    instructions="You are a helpful agent who can create freshdesk tickets.",
    toolset=toolset
)

thread = project_client.agents.threads.create()

# Chat Display
with chat_container:
    for i in range(0, len(st.session_state.chat_history), 2):
        if i < len(st.session_state.chat_history):
            user_role, user_message = st.session_state.chat_history[i]
            st.markdown(f"""
                <div class="chat-container user">
                    <div class="message-content">
                        <div class="avatar user-avatar">U</div>
                        <div class="chat-bubble user-bubble">{user_message}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        if i + 1 < len(st.session_state.chat_history):
            agent_role, agent_message = st.session_state.chat_history[i + 1]
            st.markdown(f"""
                <div class="chat-container agent">
                    <div class="message-content">
                        <div class="chat-bubble agent-bubble">{agent_message}</div>
                        <div class="avatar agent-avatar">A</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Input field
with input_container:
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_input("Type your message here...", key="user_input", label_visibility="collapsed")
    with col2:
        send_button = st.button("Send")

# Process message
if send_button and user_input:
    project_client.agents.messages.create(thread_id=thread.id, role="user", content=user_input)
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    if run.status == "failed":
        response_text = f"Run failed: {run.last_error}"
    else:
        messages = project_client.agents.messages.list(thread_id=thread.id)
        latest_message = next(msg for msg in project_client.agents.messages.list(thread_id=thread.id) if msg.role == "assistant")
        response_text = next(content.text.value for content in latest_message.content if content.type == "text")

    st.session_state.chat_history.append(("User", user_input))
    st.session_state.chat_history.append(("Agent", response_text))
    st.rerun()
