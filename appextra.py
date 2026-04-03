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
    st.session_state["page"] = "login"



# If not logged in, keep auth-related state clean.
if not st.session_state["logged_in"]:
    st.session_state["user"] = None
    st.session_state["role"] = None
    if st.session_state["page"] not in ("login", "register"):
        st.session_state["page"] = "login"

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
    if st.session_state["page"] == "home":
        st.markdown("Welcome! This is the Attendee Dashboard")
        if st.button("Go to Dashboard", key= "dashboard_view_btn", type= "primary",use_container_width=True):
            st.session_state["page"] = "dashboard"
            st.rerun()
    elif st.session_state["page"] == "dashboard":
        st.markdown("Dashboard")
            
    st.markdown("### Welcome! This is the Attendee Dashboard")
    st.markdown("## All Events")
    st.markdown("Select an event to sign up!")
    



## Admin View
elif st.session_state["logged_in"] and st.session_state["role"] == "Admin":
    if st.session_state["page"] == "create_event":
        st.subheader("Create New Event")
        if st.button("Back to Event Dashboard", key="back_to_dashboard_btn", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()
        #Create a new event form
        title = st.text_input("Event Title")
        event_date = st.date_input("Event Date")
        event_location = st.text_input("Location")
        needs_raw = st.text_area("Needs List (one item per line)")
        submitted = st.button("Save Event", use_container_width=True)

        if submitted:
            if not title.strip() or not event_location.strip():
                st.error("Title and location are required.")
            else:
                # Do the fun new line dictionary thing
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
                st.success("Event created!")
                st.session_state["page"] = "home"
                st.rerun()

        st.stop()

    if st.session_state["page"] == "home":
        st.markdown("## Event Dashboard")

        if st.button("Create New Event", key="create_event_btn", type="primary", use_container_width=True):
            st.session_state["page"] = "create_event"
            st.rerun()

        st.write("---")

    # Get the user info from the stuff
    user = st.session_state["user"]
    user_id = user["user_id"]

    # Get the events where the current user is the host
    user_events = [e for e in events if e["host_id"] == user_id]

    col1, col2 = st.columns([1, 2])

    # Left side event list
    with col1:
        st.markdown("### Your Events")

        if not user_events:
            st.info("No Events Planned")
            selected_event = None
        else:
            event_titles = [event["title"] for event in user_events]

            selected_title = st.radio("Select an event", event_titles, key="event_selector")

            # Get selected event object
            selected_event = next((e for e in user_events if e["title"] == selected_title), None )

    # --- RIGHT SIDE (Event Details) ---
    with col2:
        if selected_event:
            st.markdown(f"### {selected_event['title']}")
            st.markdown(f"**Date:** {selected_event['event_date']}")
            st.markdown(f"**Location:** {selected_event['event_location']}")

            st.markdown("### Needs")

            needs_list = selected_event.get("needs_list", {})
            event_needs = []
            event_claimed = []

            if not needs_list:
                st.write("No needs listed.")
            else:
                for item, value in needs_list.items():
                    if value == 0 or value == "" or value is None:
                        event_needs.append(item)
                    else:
                        event_claimed.append((item, value))
            st.markdown("#### Unclaimed Needs:")
            for item in event_needs:
                st.markdown(f"- {item}")
            st.markdown("#### Claimed Needs:")
            for item, claimer in event_claimed:
                st.markdown(f"- {item} claimed by {claimer}")
                    


elif st.session_state["logged_in"] and st.session_state["role"] not in ("Admin", "Attendee", "databaseview"):
    st.info("No dashboard for this role yet. Try logging in as another role.")



else:

    # Login Page
    st.subheader("Log In")
    with st.container(border=True):
        username_input = st.text_input("Username", key="username_login")
        password_input = st.text_input("Password", type="password", key="password_login")

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
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Login failed. Check your username/password.")

    # Register a New Account
    st.subheader("Register")
    with st.container(border=True):
        if st.button("Create New Account", key="show_register_btn", use_container_width=True):
            st.session_state["page"] = "register"
            st.rerun()

        if st.session_state["page"] == "register":
            with st.container(border=True):
                new_name = st.text_input("Full Name", key="full_name_register")
                new_username = st.text_input("Username", key="username_register")
                new_password = st.text_input("Password", type="password", key="password_register")
                new_role = st.selectbox("Role", ["Admin", "Attendee"], key="role_register")

            if st.button("Create Account", key="register_btn", use_container_width=True):
                with st.spinner("Creating account..."):
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
    st.markdown("## Event Manager Sidebar")
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
    else:
        st.markdown("# Please log in to access the dashboard.")
        st.markdown("Use following for database view:")
        st.markdown("- Username: dbview")
        st.markdown("- Password: password")
        st.markdown("Admin view: joey")
        st.markdown("Attendee view: jim")


## Notes to change
#### Add user id to the host tab instead of a name.
#### add above: user = st.session_state["user"]
