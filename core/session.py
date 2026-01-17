"""Session Management Functions

Uses individual session files for better concurrency:
- Each session stored as sessions/s_<id>.json
- No shared index file - scan folder for session list
- Safe for multiple users working on different sessions
"""

import json
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

# Folder for session files
SESSIONS_FOLDER = 'sessions'


def _get_session_file(session_id: str) -> str:
    """Get the file path for a session"""
    return os.path.join(SESSIONS_FOLDER, f"s_{session_id}.json")


def create_session() -> Dict[str, Any]:
    """Create a new session"""
    session_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    session = {
        "updated_at": now,
        "scribe_transcript": "",
        "scribe_note": "",
        "scribe_context": "",
        "edit_original": "",
        "edit_instructions": "",
        "edit_result": "",
        "synthesize_instructions": "",
        "synthesize_hp": "",
        "synthesize_consults": "",
        "synthesize_studies": "",
        "synthesize_progress": "",
        "synthesize_result": ""
    }
    
    # Ensure directory exists
    os.makedirs(SESSIONS_FOLDER, exist_ok=True)
    
    # Save individual session file
    session_file = _get_session_file(session_id)
    with open(session_file, 'w') as f:
        json.dump(session, f, indent=2)
    
    # Return session with ID for convenience
    session['id'] = session_id
    return session


def get_all_sessions() -> List[Dict[str, Any]]:
    """Get all sessions by scanning folder, sorted by updated date (newest first)"""
    os.makedirs(SESSIONS_FOLDER, exist_ok=True)
    
    sessions = []
    
    # Scan folder for session files
    for filename in os.listdir(SESSIONS_FOLDER):
        if filename.startswith('s_') and filename.endswith('.json'):
            session_id = filename[2:-5]  # Remove 's_' prefix and '.json' suffix
            session_file = _get_session_file(session_id)
            
            try:
                with open(session_file, 'r') as f:
                    session = json.load(f)
                    # Add id from filename for convenience
                    session['id'] = session_id
                    sessions.append(session)
            except:
                pass
    
    # Sort by updated_at descending (newest first)
    return sorted(sessions, key=lambda x: x.get('updated_at', ''), reverse=True)


def get_session_by_id(session_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific session by ID"""
    session_file = _get_session_file(session_id)
    
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r') as f:
                session = json.load(f)
                session['id'] = session_id
                return session
        except:
            pass
    return None


def update_session(session_id: str, updates: Dict[str, Any]) -> None:
    """Update session data"""
    session_file = _get_session_file(session_id)
    now = datetime.now().isoformat()
    
    # Load existing session
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r') as f:
                session = json.load(f)
        except:
            return
    else:
        return
    
    # Apply updates
    session.update(updates)
    session['updated_at'] = now
    
    # Save session file
    with open(session_file, 'w') as f:
        json.dump(session, f, indent=2)


def delete_session(session_id: str) -> None:
    """Delete a session file"""
    session_file = _get_session_file(session_id)
    
    if os.path.exists(session_file):
        try:
            os.remove(session_file)
        except:
            pass
