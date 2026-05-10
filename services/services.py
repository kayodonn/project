from typing import List, Dict, Optional
from datetime import datetime
import uuid
from pathlib import Path
import json



## Set up the user service tab. 
class UserService:

    
    def __init__(self):
        self.users_file = Path("users.json")
        self._load_users()
    
    def _load_users(self):
## get the users from the JSON File
        if self.users_file.exists():
            with open(self.users_file, "r") as f:
                self.users = json.load(f)
        else:
            self.users = []
    
    def _save_users(self):
## Save the users to the JSON File
        with open(self.users_file, "w") as f:
            json.dump(self.users, f, indent=2)
    
    def get_all_users(self) -> List[Dict]:
        return self.users.copy()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
## Verify the passwords and usernames
        for user in self.users:
            if user["username"].lower() == username.lower() and user["password"] == password:
                return user
        return None
    
    def create_user(self, full_name: str, username: str, password: str, role: str) -> Dict:
## Check if username exists
        if any(u["username"].lower() == username.lower() for u in self.users):
            raise ValueError("Username already exists")
        
## This makes the user ID increase by 1 when making a new user      
        user_ids = [int(u["user_id"]) for u in self.users if u["user_id"].isdigit()]
        next_id = str(max(user_ids) + 1) if user_ids else "1"

## Sets up the new user information in the json file        
        new_user = {
            "user_id": next_id,
            "full_name": full_name,
            "username": username,
            "password": password,
            "role": role,
            "registered_at": datetime.now().isoformat(timespec="seconds")
        }
        
        self.users.append(new_user)
        self._save_users()
        return new_user

## So that you can find the user by ID   
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        for user in self.users:
            if user["user_id"] == user_id:
                return user
        return None


## Event Details
class EventService:
    
    def __init__(self):
        self.events_file = Path("events.json")
        self._load_events()
    
    def _load_events(self):
## Load the events from the json file
        if self.events_file.exists():
            with open(self.events_file, "r") as f:
                self.events = json.load(f)
        else:
            self.events = []
    
    def _save_events(self):
## This saves the events to the json file
        with open(self.events_file, "w") as f:
            json.dump(self.events, f, indent=2)
    
    def get_all_events(self) -> List[Dict]:
## This is to return all the events as a dictionary
        return self.events.copy()
    
    def get_events_by_host(self, host_id: str) -> List[Dict]:
## This is so that you can get the events for each host
        return [event for event in self.events if event["host_id"] == host_id]
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict]:
## This is to get the events by event ID
        for event in self.events:
            if event["event_id"] == event_id:
                return event
        return None

    def update_event(self, updated_event: Dict) -> bool:
## Update an existing event in the JSON storage
        for i, event in enumerate(self.events):
            if event["event_id"] == updated_event["event_id"]:
                self.events[i] = updated_event
                self._save_events()
                return True
        return False
    
    def create_event(self, title: str, host_id: str, event_date: str, event_location: str, needs_list: Dict = None) -> Dict:
## Makes a new event
        if needs_list is None:
            needs_list = {}
        
## Gets the ID for the next event based on the previous event's id
        event_ids = [int(e["event_id"]) for e in self.events if e["event_id"].isdigit()]
        next_id = str(max(event_ids) + 1) if event_ids else "1"

## Gets the new event info in order to save to the json file       
        new_event = {
            "event_id": next_id,
            "title": title,
            "host_id": host_id,
            "needs_list": needs_list,
            "event_date": event_date,
            "event_location": event_location
        }
        
        self.events.append(new_event)
        self._save_events()
        return new_event
    
    def delete_event(self, event_id: str) -> bool:
## Deletes an event
        for i, event in enumerate(self.events):
            if event["event_id"] == event_id:
                del self.events[i]
                self._save_events()
                return True
        return False
    
    def claim_item(self, event_id: str, item: str, claimer: str) -> bool:
## To get the people to claim the item
        event = self.get_event_by_id(event_id)
        if event and item in event["needs_list"]:
            if event["needs_list"][item] in [None, 0, "", "0"]:
                event["needs_list"][item] = claimer
                self._save_events()
                return True
        return False
    
    def unclaim_item(self, event_id: str, item: str, claimer: str) -> bool:
## makes the unclaimed item list
        event = self.get_event_by_id(event_id)
        if event and item in event["needs_list"] and event["needs_list"][item] == claimer:
            event["needs_list"][item] = 0
            self._save_events()
            return True
        return False

## sets up the services so that it can be used clearly in the app.py file
user_service = UserService()
event_service = EventService()