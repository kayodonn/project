import streamlit as st
from datetime import datetime
from typing import Dict
from services.services import user_service, event_service
from user_interface.chatbot import render_chatbot


def setup_session_state():
    defaults = {
        "logged_in": False,
        "user": None,
        "role": None,
        "page": "dashboard",
        "selected_event_id": None,
        "editing_event": False,
        "editing_event_id": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state["logged_in"] and st.session_state["page"] not in ("dashboard", "login", "register"):
        st.session_state["page"] = "dashboard"


def render_sidebar():
    with st.sidebar:
        st.title("Event Manager Sidebar")

        if st.button("Log Out", use_container_width=True):
            logout()

        if st.session_state["logged_in"]:
            user = st.session_state["user"]
            st.markdown(f"**User:** {user['username']}")
            st.markdown(f"**Role:** {user['role']}")
            st.write("---")

            if st.button("Chatbot Assistant", use_container_width=True, type="secondary"):
                st.session_state["chatbot_open"] = True
                st.rerun()

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


def logout():
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.session_state["role"] = None
    st.session_state["page"] = "login"
    st.rerun()


def render_content():
    

    if st.session_state["logged_in"] and st.session_state["role"] == "databaseview":
        render_database_view()
    elif st.session_state["logged_in"] and st.session_state["role"] == "Attendee":
        render_attendee()
        if st.session_state.get("chatbot_open", False):
            render_chatbot()
    elif st.session_state["logged_in"] and st.session_state["role"] == "Admin":
        render_admin()
        if st.session_state.get("chatbot_open", False):
            render_chatbot()
    elif st.session_state["logged_in"] and st.session_state["role"] not in ("Admin", "Attendee", "databaseview"):
        st.info("No dashboard for this role yet. Try logging in as another role.")
    else:
        render_public()


def render_database_view():
    st.header("Welcome to Database View")
    st.markdown("## Users")
    users = user_service.get_all_users()
    st.dataframe(users)
    
    st.divider()
    st.markdown("## Events")
    events = event_service.get_all_events()
    st.dataframe(events)


def render_attendee():
    if st.session_state["page"] == "dashboard":
        render_attendee_dashboard()
    elif st.session_state["page"] == "sign_up":
        render_attendee_sign_up()
    else:
        st.session_state["page"] = "dashboard"
        st.rerun()


def render_attendee_dashboard():
    st.header("Attendee Dashboard")
    st.divider()
    st.subheader("Your Events:")

    user = st.session_state["user"]
    events = event_service.get_all_events()
    user_events = [event for event in events if any(claimer == user["full_name"] for claimer in event["needs_list"].values())]

    if not user_events:
        st.info("You have not signed up for any events yet.")
        return

    for event in user_events:
        with st.container(border=True):
            st.markdown(f"### **{event['title']}**")
            st.markdown(f"**Date:** {event['event_date']}")
            st.markdown(f"**Location:** {event['event_location']}")
            st.markdown("Needs you have signed up for:")
            for item, claimer in event["needs_list"].items():
                if claimer == user["full_name"]:
                    st.markdown(f"- {item}")
            st.write("")
            st.write("---")
            if st.button("Leave Event", key=f"leave_event_btn_{event['event_id']}", type="secondary"):
                with st.spinner("Processing your request..."):
                    for item in event["needs_list"]:
                        if event["needs_list"][item] == user["full_name"]:
                            event["needs_list"][item] = 0
                    event_service.update_event(event)
                    st.success(f"You have left {event['title']}.")
                    st.rerun()


def render_attendee_sign_up():
    st.header("Sign Up for an Event")
    st.header("All Events")
    st.subheader("Select an event to sign up.")

    events = event_service.get_all_events()
    col1, col2 = st.columns([3, 5])

    with col1:
        selected_event = st.radio("Events", options=events, key="attendee_event_selector", format_func=lambda x: f"{x['title']}")

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
                    for item, claimer in needs_list.items():
                        if claimer in [0, "", None]:
                            st.markdown(f"- {item} (Unclaimed)")
                        else:
                            st.markdown(f"- {item} claimed by {claimer}")

                available_items = [item for item, claimer in needs_list.items() if claimer in [0, "", None]]
                claimed_count = len([v for v in needs_list.values() if v not in (0, "", None)])
                total_count = len(needs_list)
                st.markdown(f"**Status:** {claimed_count}/{total_count} items claimed")

                if available_items:
                    item = st.selectbox("Select a need to claim", options=available_items, key="attendee_need_select")
                else:
                    st.warning("All items have been claimed for this event.")
                    item = None

                if st.button("Sign Up", key="attendee_signup_btn", use_container_width=True, type="primary", disabled=(item is None)):
                    with st.spinner("Processing your request…"):
                        selected_event["needs_list"][item] = st.session_state["user"]["full_name"]
                        event_service.update_event(selected_event)
                        st.success(f"You have signed up to bring {item} for {selected_event['title']}.")
                        st.session_state["page"] = "dashboard"
                        st.rerun()


def render_admin():
    if st.session_state["page"] == "create_event":
        render_admin_create_event()
    else:
        render_admin_dashboard()


def render_admin_create_event():
    st.header("Create New Event")
    if st.button("Back to Event Dashboard", key="admin_back_btn", use_container_width=True):
        st.session_state["page"] = "home"
        st.rerun()

    with st.container(border=True):
        title = st.text_input("Event Title")
        event_date = st.date_input("Event Date")
        event_location = st.text_input("Location")
        needs_raw = st.text_area("Needs List (one item per line)")
        submitted = st.button("Save Event", key="save_event_btn", use_container_width=True)

    if submitted:
        if not title.strip() or not event_location.strip():
            st.error("Title and location are required.")
            return

        needs_list = {}
        for line in needs_raw.splitlines():
            item = line.strip()
            if item:
                needs_list[item] = 0

        event_service.create_event(
            title=title,
            host_id=st.session_state["user"]["user_id"],
            event_date=event_date.isoformat(),
            event_location=event_location,
            needs_list=needs_list,
        )
        st.success("Event created successfully.")
        st.session_state["page"] = "home"
        st.rerun()


def render_admin_dashboard():
    st.header("Admin Dashboard")
    user = st.session_state["user"]
    events = event_service.get_all_events()
    user_events = [event for event in events if event["host_id"] == user["user_id"]]

    col1, col2 = st.columns([3, 5])
    with col1:
        st.subheader("Your Events")
        if not user_events:
            st.info("You have not created any events yet.")
            selected_event = None
        else:
            event_titles = [event["title"] for event in user_events]
            selected_title = st.radio("Select an event", event_titles, key="admin_event_selector")
            selected_event = next((event for event in user_events if event["title"] == selected_title), None)

    with col2:
        if selected_event:
            render_admin_event_detail(selected_event)


def render_admin_event_detail(selected_event: Dict):
    with st.container(border=True):
        if st.session_state.get("editing_event") and st.session_state.get("editing_event_id") == selected_event["event_id"]:
            render_admin_event_edit(selected_event)
        else:
            render_admin_event_view(selected_event)


def render_admin_event_view(selected_event: Dict):
    st.header(f"{selected_event['title']}")
    st.markdown(f"**Date:** {selected_event['event_date']}")
    st.markdown(f"**Location:** {selected_event['event_location']}")
    st.write("---")
    st.markdown("#### Needs")

    needs_list = selected_event.get("needs_list", {})
    event_needs = [item for item, value in needs_list.items() if value in [0, "", None]]
    event_claimed = [(item, value) for item, value in needs_list.items() if value not in [0, "", None]]

    st.markdown("##### Unclaimed Needs:")
    for item in event_needs:
        st.markdown(f"- {item}")

    st.markdown("##### Claimed Needs:")
    for item, claimer in event_claimed:
        st.markdown(f"- {item} claimed by {claimer}")

    st.write("---")
    col_edit, col_cancel = st.columns(2)
    with col_edit:
        if st.button("Edit Event", key="edit_event_btn", use_container_width=True):
            st.session_state["editing_event"] = True
            st.session_state["editing_event_id"] = selected_event["event_id"]
            st.rerun()
    with col_cancel:
        if st.button("Cancel Event", key="cancel_event_btn", use_container_width=True, type="primary"):
            if event_service.delete_event(selected_event["event_id"]):
                st.success("Event cancelled.")
                st.session_state["page"] = "home"
                st.rerun()


def render_admin_event_edit(selected_event: Dict):
    st.header("Edit Event")
    edit_title = st.text_input("Event Title", value=selected_event["title"], key="edit_title")
    edit_date = st.date_input("Event Date", value=datetime.fromisoformat(selected_event["event_date"]).date(), key="edit_date")
    edit_location = st.text_input("Event Location", value=selected_event["event_location"], key="edit_location")
    st.markdown("#### Needs")
    st.markdown("Add items needed for this event (one per line):")
    needs_text = st.text_area("Needs List", value="\n".join(selected_event.get("needs_list", {}).keys()), key="edit_needs", height=100)

    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("Save Changes", key="save_edit_btn", use_container_width=True, type="primary"):
            new_needs = {}
            current_needs = selected_event.get("needs_list", {})
            for line in needs_text.split("\n"):
                item = line.strip()
                if item:
                    if item in current_needs and current_needs[item] not in [0, "", None]:
                        new_needs[item] = current_needs[item]
                    else:
                        new_needs[item] = 0
            selected_event["title"] = edit_title.strip()
            selected_event["event_date"] = edit_date.isoformat()
            selected_event["event_location"] = edit_location.strip()
            selected_event["needs_list"] = new_needs
            event_service.update_event(selected_event)
            st.success("Event updated successfully!")
            st.session_state["editing_event"] = False
            st.session_state["editing_event_id"] = None
            st.rerun()

    with col_cancel:
        if st.button("Cancel Edit", key="cancel_edit_btn", use_container_width=True):
            st.session_state["editing_event"] = False
            st.session_state["editing_event_id"] = None
            st.rerun()


def render_public():
    if st.session_state["page"] == "dashboard":
        st.subheader("Community Event Manager App")
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

    if st.session_state["page"] == "login":
        render_login()
    elif st.session_state["page"] == "register":
        render_register()


def render_login():
    st.subheader("Log In")
    with st.container(border=True):
        username_input = st.text_input("Username", key="username_login")
        password_input = st.text_input("Password", type="password", key="password_login")

        if st.button("Log In", type="primary", use_container_width=True):
            with st.spinner("Logging In..."):
                found_user = user_service.authenticate_user(username_input, password_input)
                if found_user:
                    st.success(f"Welcome Back, {found_user['username']}!")
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = found_user
                    st.session_state["role"] = found_user["role"]
                    if st.session_state["role"] == "Admin":
                        st.session_state["page"] = "home"
                    elif st.session_state["role"] == "Attendee":
                        st.session_state["page"] = "dashboard"
                    else:
                        st.session_state["page"] = "dashboard"
                    st.rerun()
                else:
                    st.error("Login failed. Check your username/password.")

    st.write("---")
    if st.button("Create New Account", key="show_register_btn", use_container_width=True):
        st.session_state["page"] = "register"
        st.rerun()


def render_register():
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
            else:
                try:
                    new_user = user_service.create_user(new_name, new_username, new_password, new_role)
                except ValueError as e:
                    st.error(str(e))
                else:
                    st.success("Account created! Logging you in...")
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = new_user
                    st.session_state["role"] = new_user["role"]
                    if st.session_state["role"] == "Admin":
                        st.session_state["page"] = "home"
                    else:
                        st.session_state["page"] = "dashboard"
                    st.rerun()