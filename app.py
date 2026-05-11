import streamlit as st
from pathlib import Path
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from user_interface.ui import render_content, render_sidebar

st.set_page_config(page_title="Community Event Manager", layout="centered")
st.title("Community Event Manager")


# Set up the session states
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"

if "selected_event_id" not in st.session_state:
    st.session_state["selected_event_id"] = None

if "editing_event" not in st.session_state:
    st.session_state["editing_event"] = False

if "editing_event_id" not in st.session_state:
    st.session_state["editing_event_id"] = None

if "chatbot_open" not in st.session_state:
    st.session_state["chatbot_open"] = False

if "chatbot_open" not in st.session_state:
    st.session_state["chatbot_open"] = False

if "chatbot_history" not in st.session_state:
    st.session_state["chatbot_history"] = []

if "chatbot_input" not in st.session_state:
    st.session_state["chatbot_input"] = ""




# Make the side bar and content come up
render_sidebar()
render_content()