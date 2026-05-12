import streamlit as st
import os
from pathlib import Path
import json
from dotenv import load_dotenv
from openai import OpenAI
from services.chatbot_service import build_ai_prompt, get_ai_response, get_events_context

env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY") or getattr(st, "secrets", {}).get("OPENAI_API_KEY")
if not api_key:
    st.error(
        "OpenAI API Key was not found. Set OPENAI_API_KEY in your .env file or in Streamlit secrets."
    )
    st.stop()

client = OpenAI(api_key=api_key)

# Load chat logs
def load_logs(filepath):
    json_path = Path(filepath)
    if json_path.exists():
        with open(json_path, "r") as f:
            return json.load(f)
    else:
        return []

def save_logs(filepath, logs):
    json_path = Path(filepath)
    with open(json_path, "w") as f:
        json.dump(logs, f, indent=2)

logs = load_logs("chatbot_logs.json")

def ensure_chatbot_session_state():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        for log in logs:
            st.session_state["messages"].append(
                {
                    "role": log.get("role", "assistant"),
                    "content": log.get("content", "")
                }
            )
        if len(st.session_state["messages"]) == 0:
            st.session_state["messages"].append(
                {
                    "role": "assistant",
                    "content": "Hi, ask me about events or available items!"
                }
            )

    if "chatbot_open" not in st.session_state:
        st.session_state["chatbot_open"] = False


def render_chatbot():
    ensure_chatbot_session_state()
    if not st.session_state.get("chatbot_open", False):
        return

    st.markdown("---")
    st.markdown("## Community Event Chatbot")
    st.markdown("Ask about events, event dates, locations, or which items are still available.")

    for message in st.session_state['messages']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    user_input = st.chat_input("Ask me a question...")

    if user_input:
        st.session_state['messages'].append(
            {
                "role": "user",
                "content": user_input
            }
        )
        with st.chat_message('user'):
            st.markdown(user_input)

        
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking...."):
                context = get_events_context()
                ai_response = get_ai_response(client, st.session_state['messages'], context)
                st.markdown(ai_response)

        st.session_state['messages'].append(
            {
                'role': 'assistant',
                'content': ai_response
            }
        )

        # Save logs
        logs = load_logs("chatbot_logs.json")
        logs.append({
            'role': 'user',
            'content': user_input
        })
        logs.append({
            'role': 'assistant',
            'content': ai_response
        })
        save_logs("chatbot_logs.json", logs)

    col1, col2 = st.columns([1, 1])
    if col1.button("Close Chatbot"):
        st.session_state["chatbot_open"] = False
        st.rerun()
    if col2.button("Reset Chat"):
        st.session_state["messages"] = [
            {
                'role': 'assistant',
                'content': "Hi, ask me about events or available items!"
            }
        ]
        st.rerun()