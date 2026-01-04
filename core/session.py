"""Session Management Functions"""

import json
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from .config import load_config


def load_session_data() -> Dict[str, Any]:
    """Load session data from persistent storage"""
    config = load_config()
    storage_file = config.get('session', {}).get('storage_file', 'sessions/session_data.json')
    
    if os.path.exists(storage_file):
        try:
            with open(storage_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"sessions": [], "current_session": None}


def save_session_data(data: Dict[str, Any]) -> None:
    """Save session data to persistent storage"""
    config = load_config()
    storage_file = config.get('session', {}).get('storage_file', 'sessions/session_data.json')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(storage_file), exist_ok=True)
    
    with open(storage_file, 'w') as f:
        json.dump(data, f, indent=2)


def create_session() -> Dict[str, Any]:
    """Create a new session"""
    data = load_session_data()
    max_history = data.get('max_history', 100)
    
    session = {
        "id": str(uuid.uuid4())[:8],
        "created_at": datetime.now().isoformat(),
        "scribe_transcript": "",
        "scribe_note": "",
        "scribe_context": "",
        "edit_original": "",
        "edit_instructions": "",
        "edit_result": ""
    }
    
    data["sessions"].insert(0, session)
    data["sessions"] = data["sessions"][:max_history]
    data["current_session"] = session["id"]
    
    save_session_data(data)
    return session


def get_current_session() -> Optional[Dict[str, Any]]:
    """Get the current active session"""
    data = load_session_data()
    current_id = data.get("current_session")
    
    for session in data.get("sessions", []):
        if session["id"] == current_id:
            return session
    return None


def update_session(session_id: str, updates: Dict[str, Any]) -> None:
    """Update session data"""
    data = load_session_data()
    
    for session in data.get("sessions", []):
        if session["id"] == session_id:
            session.update(updates)
            session["updated_at"] = datetime.now().isoformat()
            break
    
    save_session_data(data)


def delete_session(session_id: str) -> None:
    """Delete a session"""
    data = load_session_data()
    data["sessions"] = [s for s in data.get("sessions", []) if s["id"] != session_id]
    if data.get("current_session") == session_id:
        data["current_session"] = data["sessions"][0]["id"] if data["sessions"] else None
    save_session_data(data)
