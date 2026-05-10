## Data Layer
## This file holds all of the JSON reading files.


from pathlib import Path
import json


# Loading the JSONS

json_path = Path("users.json")
json_path_event = Path("events.json")


# Load data
def load_users():
    if json_path.exists():
        with open(json_path, "r") as f:
            loaded_users = json.load(f)
            # If file is empty, keep defaults
            if isinstance(loaded_users, list) and len(loaded_users) > 0:
                return loaded_users
    return []               
def load_events():
    if json_path_event.exists():
        with json_path_event.open("r", encoding= "utf-8") as f:
            loaded_events = json.load(f)
            if isinstance(loaded_events, list) and len(loaded_events) > 0:
                return loaded_events
    return []
        


# Saving the information to the JSONS
def save_users(data):
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
def save_events(data):
    json_path_event.write_text(json.dumps(data, indent=2), encoding="utf-8")



# Next ID's
def next_user_id(users):
    numeric_ids = [int(u["user_id"]) for u in users if str(u.get("user_id")).isdigit()]
    return str(max(numeric_ids) + 1) if numeric_ids else "1"
def next_event_id(events):
    numeric_ids = [int(u["event_id"]) for u in events if str(u.get("event_id")).isdigit()]
    return str(max(numeric_ids) + 1) if numeric_ids else "1"