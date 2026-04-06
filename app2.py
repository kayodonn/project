import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time


st.set_page_config(page_title="Community Event Manager", layout="centered")

## Set up the variables (login status, user info, role, page goes to login page immediately)
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


# If not logged in, keep auth-related state clean.
if not st.session_state["logged_in"]:
    st.session_state["user"] = None
    st.session_state["role"] = None
    if st.session_state["page"] not in ("dashboard", "login", "register"):
        st.session_state["page"] = "dashboard"

## Set up users data
users = [
    {
        "user_id": "1",
        "full_name": "Database View",
        "username": "dbview",
        "password": "password",
        "role": "databaseview"
    },
    {
        "user_id": "2",
        "full_name": "System Admin",
        "username": "admin1",
        "password": "123ssag@43AE",
        "role": "Admin",
        "registered_at": "..."
    },
    {
        "user_id": "3",
        "full_name": "Normal Attendee",
        "username": "attendee1",
        "password": "abcdefg",
        "role": "Attendee",
        "registered_at": "..."
    },
    {
        "user_id": "4",
        "full_name": "joey",
        "username": "joey",
        "password": "joey",
        "role": "Admin",
        "registered_at": "2026-04-02T23:30:53"
    }
]

json_path = Path("users.json")
if json_path.exists():
    with open(json_path, "r") as f:
        loaded_users = json.load(f)
        # If file is empty, keep defaults
        if isinstance(loaded_users, list) and len(loaded_users) > 0:
            users = loaded_users


## These def functions are to make sure that the code later is easier to read
def save_users(data):
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")



## make a function to get the next user id for making new users.
def next_user_id(users):
    numeric_ids = [int(u["user_id"]) for u in users if str(u.get("user_id")).isdigit()]
    return str(max(numeric_ids) + 1) if numeric_ids else "1"


## Set up events data
events = [
    {
        "event_id": "1",
        "title": "Community Pizza Party",
        "host_id": "1",
        "needs_list": {"plates": "Elmo", "cups": "Cookie Monster"},
        "event_date": "2025-05-01",
        "event_location": "Community Center",
    }
]

next_event_id_counter = 1
## We couldn't figure out a better way to do this than using a def
def next_event_id(events):
    numeric_ids = [int(u["event_id"]) for u in events if str(u.get("event_id")).isdigit()]
    return str(max(numeric_ids) + 1) if numeric_ids else "1"

json_path_event = Path("events.json")

#Load the data from a json file
if json_path_event.exists():
    with json_path_event.open("r", encoding= "utf-8") as f:
        loaded_events = json.load(f)
        if isinstance(loaded_events, list) and len(loaded_events) > 0:
            events = loaded_events

# use the def function to save the data to the json easily
def save_events(data):
    json_path_event.write_text(json.dumps(data, indent=2), encoding="utf-8")


## Establish who is the user once logged in
user = st.session_state["user"]

## Make a database view for us to see all the events and users
if st.session_state["logged_in"] and st.session_state["role"] == "databaseview":
    st.markdown("## Users")
    st.dataframe(users)

    st.markdown("## Events")
    st.dataframe(events)



## Attendee View
elif st.session_state["logged_in"] and st.session_state["role"] == "Attendee":
    if st.session_state["page"] == "dashboard":
        st.title("Attendee Dashboard")
        st.header("Your Events")
        user_events = []
        for event in events:
            for item in event["needs_list"]:
                if event["needs_list"][item] == user["full_name"]:
                    user_events.append(event)
        if not user_events:
            st.info("You have not signed up for any events yet.")
        else:
            for event in user_events:
                with st.container(border=True):
                    st.markdown(f"### **{event['title']}**")
                    st.markdown(f"**Date:** {event['event_date']}")
                    st.markdown(f"**Location:** {event['event_location']}")
                    st.markdown("Needs you have signed up for:")
                    for item, claimer in event["needs_list"].items():
                        if claimer == user["full_name"]:
                            st.markdown(f"- {item}")
                    ## Added in the leave event button
                    st.write("")
                    st.write("---")
                    if st.button("Leave Event", key=f"leave_event_btn_{event['event_id']}", type="secondary"):
                        with st.spinner("Processing your request..."):
                            time.sleep(1)
                            event_index = events.index(event)
                            for item in events[event_index]["needs_list"]:
                                if events[event_index]["needs_list"][item] == user["full_name"]:
                                    events[event_index]["needs_list"][item] = 0
                            save_events(events)
                            st.success(f"You have left {event['title']}.")
                            time.sleep(2)
                            st.rerun()

    elif st.session_state["page"] == "sign_up":
        st.title("Sign Up for an Event")
            
        st.header("All Events")
        st.subheader("Select an event to sign up.")
        col1,col2 = st.columns([3,5])
        with col1:
            selected_event = st.radio("Events", options=events, key= "attendee_event_selector",
                    format_func= lambda x: f"{x['title']}")
        with col2:
            with st.container(border=True):
                st.markdown("### Event Details")
                if selected_event:
                    st.markdown(f"**Title:** {selected_event['title']}")
                    st.markdown(f"**Date:** {selected_event['event_date']}")
                    st.markdown(f"**Location:** {selected_event['event_location']}")
                    st.markdown("**Needs List:**")
                    needs_list = selected_event["needs_list"]
                    if not needs_list:
                        st.write("No needs listed.")
                    else:
                        for item in needs_list:
                            if needs_list[item] == 0 or needs_list[item] == "" or needs_list[item] is None:
                                st.markdown(f"- {item} (Unclaimed)")
                            else:
                                st.markdown(f"- {item} claimed by {needs_list[item]}")
                    available_items = [i for i, v in needs_list.items() if v == 0]
                    claimed_count = len([v for v in needs_list.values() if v not in (0, "", None)])
                    total_count = len(needs_list)

                    st.markdown(f"**Status:** {claimed_count}/{total_count} items claimed")

                    if not available_items:
                        st.warning("All items have been claimed for this event.")
                        item = None
                    else:
                        item = st.selectbox("Select a need to claim", options=available_items,key="attendee_need_select")
                    signup_disabled = not available_items

                    if st.button("Sign Up",key="attendee_signup_btn",use_container_width=True,
                        type="primary",disabled=signup_disabled):
                        if item:
                            with st.spinner("Processing your request…"):
                                time.sleep(1)
                                event_index = events.index(selected_event)
                                events[event_index]["needs_list"][item] = user["full_name"]
                                with json_path_event.open("w",encoding="utf-8") as f:
                                    json.dump(events,f)
                                st.success(f"You have signed up to bring {item} for {selected_event['title']}.")
                                time.sleep(2)
                                st.session_state["page"] = "dashboard"
                                st.rerun()
    



## Admin View
elif st.session_state["logged_in"] and st.session_state["role"] == "Admin":
    if st.session_state["page"] == "create_event":
        st.title("Create New Event")
        if st.button("Back to Event Dashboard", key="admin_back_btn", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()
        #Create a new event form
        with st.container(border=True):
            title = st.text_input("Event Title")
            event_date = st.date_input("Event Date")
            event_location = st.text_input("Location")
            needs_raw = st.text_area("Needs List (one item per line)")
            submitted = st.button("Save Event", key= "save_event_btn",use_container_width=True)

        if submitted:
            if not title.strip() or not event_location.strip():
                st.error("Title and location are required.")
            else:
                needs_list = {}
                for line in needs_raw.splitlines():
                    item = line.strip()
                    if item:
                        needs_list[item] = 0

                new_event = {
                    "event_id": next_event_id(events),
                    "title": title,
                    "host_id": st.session_state["user"]["user_id"],
                    "needs_list": needs_list,
                    "event_date": event_date.isoformat(),
                    "event_location": event_location,
                }
                events.append(new_event)
                save_events(events)
                st.success("Event created successfully.")
                st.session_state["page"] = "home"
                st.rerun()


    if st.session_state["page"] == "home":
        st.title("Admin Dashboard")

    # Get the user info from the stuff
    user = st.session_state["user"]
    user_id = user["user_id"]

    # Get the events where the current user is the host
    user_events = [e for e in events if e["host_id"] == user_id]

    col1, col2 = st.columns([3, 5])

    # Left side event list
    with col1:
        st.header("Your Events")

        if not user_events:
            st.info("You have not created any events yet.")
            selected_event = None
        else:
            event_titles = [event["title"] for event in user_events]

            selected_title = st.radio("Select an event", event_titles, key="admin_event_selector")

            # Get selected event object
            selected_event = next((e for e in user_events if e["title"] == selected_title), None )

    # --- RIGHT SIDE (Event Details) ---
    with col2:
        if selected_event:
            with st.container(border=True):
                st.header(f"{selected_event['title']}")
                st.markdown(f"**Date:** {selected_event['event_date']}")
                st.markdown(f"**Location:** {selected_event['event_location']}")
                st.write("---")

                st.markdown("#### Needs")

                needs_list = selected_event.get("needs_list", {})
                event_needs = []
                event_claimed = []

                if not needs_list:
                    st.write("No items have been added to this event yet.")
                else:
                    for item, value in needs_list.items():
                        if value == 0 or value == "" or value is None:
                            event_needs.append(item)
                        else:
                            event_claimed.append((item, value))
                st.markdown("##### Unclaimed Needs:")
                for item in event_needs:
                    st.markdown(f"- {item}")
                st.markdown("##### Claimed Needs:")
                for item, claimer in event_claimed:
                    st.markdown(f"- {item} claimed by {claimer}")
                st.write("")
                st.write("---")
                if st.button("Cancel Event", key="cancel_event_btn", use_container_width=True, type="primary"):
                    with st.spinner("Cancelling event..."):
                        time.sleep(1)
                        events.remove(selected_event)
                        save_events(events)
                        st.success("Event cancelled.")
                        time.sleep(2)
                        st.session_state["page"] = "home"
                        st.rerun()


elif st.session_state["logged_in"] and st.session_state["role"] not in ("Admin", "Attendee", "databaseview"):
    st.info("No dashboard for this role yet. Try logging in as another role.")



else:
    if st.session_state["page"] == "dashboard":
        st.title("Community Event Manager App")
        st.markdown("Log in or create an account below")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Go to Login", key="login_btn", use_container_width=True, type="primary"):
                st.session_state["page"] = "login"
                st.rerun()
        with col2:
            if st.button("Create Account", key="register_btn", use_container_width=True):
                st.session_state["page"] = "register"
                st.rerun()

    # Login Page
    if st.session_state["page"] == "login":
        st.subheader("Log In")
        with st.container(border=True):
            username_input = st.text_input("Username", key="username_login")
            password_input = st.text_input("Password", type="password", key="password_login")

            if st.button("Log In", type="primary", use_container_width=True):
                with st.spinner("Logging In..."):
                    time.sleep(2) 
                    found_user = None
                    for user in users:
                        if user["username"].strip().lower() == username_input.strip().lower() and user["password"] == password_input:
                            found_user = user
                            break

                    if found_user:
                        st.success(f"Welcome Back, {found_user['username']}!")
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = found_user
                        st.session_state["role"] = found_user["role"]
                        if st.session_state["role"] == "Admin":
                            st.session_state["page"] = "home"
                        if st.session_state["role"] == "Attendee":
                            st.session_state["page"] = "dashboard"
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Login failed. Check your username/password.")

        st.write("---")
        if st.button("Create New Account", key="show_register_btn", use_container_width=True):
            st.session_state["page"] = "register"
            st.rerun()

    # Register a New Account
    if st.session_state["page"] == "register":
        st.subheader("Register")
        if st.button("Back to Login", key="back_to_login_btn", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()
        with st.container(border=True):
            new_name = st.text_input("Full Name", key="full_name_register")
            new_username = st.text_input("Username", key="username_register")
            new_password = st.text_input("Password", type="password", key="password_register")
            new_role = st.selectbox("Role", ["Admin", "Attendee"], key="role_register")

        if st.button("Create Account", key="register_btn", use_container_width=True):
            with st.spinner("Creating Account..."):
                if not new_username.strip() or not new_password.strip():
                    st.error("Username and password are required.")
                elif any(u["username"].strip().lower() == new_username.strip().lower() for u in users):
                    st.error("That username already exists.")
                else:
                    new_user = {
                        "user_id": next_user_id(users),
                        "full_name": new_name.strip(),
                        "username": new_username.strip(),
                        "password": new_password,
                        "role": new_role,
                        "registered_at": datetime.now().isoformat(timespec="seconds"),
                    }
                    users.append(new_user)
                    save_users(users)
                    st.success("Account created! Logging you in...")
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = new_user
                    st.session_state["role"] = new_user["role"]
                    st.session_state["page"] = "home"
                    time.sleep(1)
                    st.rerun()

    st.write("---")


# Do the Sidebar
with st.sidebar:
    st.title("Event Manager Sidebar")
    if st.button("Log Out", use_container_width= True):
            with st.spinner("Logging Out..."):
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["page"]= "login"
                time.sleep(2)
                st.rerun()
                
    if st.session_state["logged_in"] == True:
        user = st.session_state["user"]
        st.markdown(f"**User:** {user['username']}")
        st.markdown(f"**Role:** {user['role']}")
        st.write("---")
        if st.session_state["role"] == "Attendee":
            if st.session_state.get("page") == "dashboard":
                if st.button("Sign Up for an Event", key="sidebar_attendee_signup_btn", use_container_width=True, type="primary"):
                    st.session_state["page"] = "sign_up"
                    st.rerun()
            elif st.session_state.get("page") == "sign_up":
                if st.button("Back to Dashboard", key="sidebar_attendee_back_btn", use_container_width=True):
                    st.session_state["page"] = "dashboard"
                    st.rerun()
            st.write("---")
        if st.session_state["role"] == "Admin":
            if st.session_state.get("page") == "home":
                if st.button("Create New Event", key="sidebar_admin_create_btn", use_container_width=True, type="primary"):
                    st.session_state["page"] = "create_event"
                    st.rerun()
            elif st.session_state.get("page") == "create_event":
                if st.button("Back to Dashboard", key="sidebar_admin_back_btn", use_container_width=True):
                    st.session_state["page"] = "home"
                    st.rerun()
        
    else:
        st.markdown("Please log in to access your dashboard.")
        st.markdown("Use following for database view:")
        st.markdown("- Username: dbview")
        st.markdown("- Password: password")
        st.markdown("Admin view: joey")
        st.markdown("Attendee view: jim")

