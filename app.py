import requests
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time


st.set_page_config(page_title="Community Event Manager", layout="centered")


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"


users = [
        {
        "id": "1",
        "full_name": "System Admin",
        "username": "admin1",
        "password": "123ssag@43AE",
        "role": "Admin",
        "registered_at": "..."
    },
    {
        "id": "2",
        "full_name": "Normal Attendee",
        "username": "attendee1",
        "password": "abcdefg",
        "role": "Attendee",
        "registered_at": "..."
    }
]

json_path = Path("users.json")
if json_path.exists():
    with open(json_path, "r") as f:
        users = json.load(f)

events = [
    {
        "id" : "Event1",
        "title": "Community Pizza Party",
        "host" : "John Doe",
        "needs_list" : {"plates": "Elmo", "cups": "Cookie Monster"},
        "event_date": "2025-05-01",
        "event_location": "Community Center",
    }
]


json_path_event = Path("events.json")

#Load the data from a json file
if json_path_event.exists():
    with json_path_event.open("r", encoding= "utf-8") as f:
        events = json.load(f)


if st.session_state["role"] == "Attendee":
    st.markdown("### Welcome! This is the Attendee Dashboard")
    st.markdown("## All Events")
    st.markdown("Select an event to sign up!")

    col1,col2 = st.columns([4,2])
    with col1:
        

        st.dataframe(events)
        selected_event = st.selectbox("Events", options=events, key= "event_selector",
                    format_func= lambda x: f"{x['title']}")




elif st.session_state['role'] == "Admin":
    st.markdown("Welcome! This is the Manager Dashboard")



else:

    # --- LOGIN --
    st.subheader("Log In")
    with st.container(border=True):
        username_input = st.text_input("Username", key= "username_login")
        password_input = st.text_input("Password", type="password",key="password_login")
        
        if st.button("Log In", type="primary", use_container_width=True):
            with st.spinner("Logging in..."):
                time.sleep(2) # Fake backend delay
                found_user = None
                for user in users:
                    if user["username"].strip().lower() == username_input.strip().lower() and user["password"] == password_input:
                        found_user = user
                        break
                
                if found_user:
                    st.success(f"Welcome back, {found_user['username']}!")
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = found_user
                    st.session_state["role"] = found_user["role"]
                    st.session_state["page"] = "home"


                    time.sleep(2)
                    st.rerun()


    # --- REGISTRATION ---
    st.subheader("New Admin Account")
    with st.container(border=True):
        new_username = st.text_input("Username", key= "username_register")
        new_password = st.text_input("Password", type="password", key= "password_register")
        
        if st.button("Create Account", key= "register_btn"):
            with st.spinner("Creating account..."):
                pass

    st.write("---")

with st.sidebar:
    st.markdown("Event Manager Sidebar")
    if  st.session_state["logged_in"] == True:
        user = st.session_state["user"]
        st.markdown(f"Loged Username: {user['username']}")
        if st.button("Log out", type="primary", use_container_width= True):
            with st.spinner("loggin out..."):
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["page"]= "login"
                time.sleep(4)
                st.rerun()
    






### This is a test


