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





if st.session_state["role"] == "User":
    if st.session_state["page"] == "home":
        st.markdown("Welcome! This is the User Dashboard")
        if st.button("Go to Dashboard", key= "dashboard_view_btn", type= "primary",use_container_width=True):
            st.session_state["page"] = "dashboard"
            st.rerun()
    elif st.session_state["page"] == "dashboard":
        st.markdown("Dashboard")
            




elif st.session_state['role'] == "Admin":
    st.markdown("Welcome! This is the Manager Dashboard")

    if st.button("Log out", type="primary", use_container_width= True):
        with st.spinner("loggin out..."):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.session_state["page"]= "login"
            time.sleep(4)
            st.rerun()


else:

    # --- LOGIN --
    st.subheader("Log In")
    with st.container(border=True):
        email_input = st.text_input("Email", key= "email_login")
        password_input = st.text_input("Password", type="password",key="password_login")
        
        if st.button("Log In", type="primary", use_container_width=True):
            with st.spinner("Logging in..."):
                time.sleep(2) # Fake backend delay
                pass
    # --- REGISTRATION ---
    st.subheader("New Admin Account")
    with st.container(border=True):
        new_email = st.text_input("Email", key= "email_register")
        new_password = st.text_input("Password", type="password", key= "password_edit")
        
        if st.button("Create Account", key= "register_btn"):
            with st.spinner("Creating account..."):
                pass

    st.write("---")

with st.sidebar:
    st.markdown("Event Manager Sidebar")
    if  st.session_state["logged_in"] == True:
        user = st.session_state["user"]
        st.markdown(f"Loged User Email: {user['email']}")






### This is a test