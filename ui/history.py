"""Session History UI Component"""

import streamlit as st

from core import get_current_session, create_session, delete_session, load_session_data, save_session_data


def render_session_history() -> None:
    """Render session history viewer"""
    st.header("📚 Session History")
    
    data = load_session_data()
    sessions = data.get("sessions", [])
    
    if not sessions:
        st.info("No previous sessions found.")
        return
    
    # Create a container for each session
    for session in sessions:
        with st.expander(f"Session {session['id']} - {session.get('created_at', 'Unknown')[:19]}", expanded=False):
            st.json(session)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"Load Session {session['id']}", key=f"load_{session['id']}"):
                    data['current_session'] = session['id']
                    save_session_data(data)
                    st.success(f"Loaded session {session['id']}")
                    st.rerun()
            
            with col2:
                if st.button(f"Delete Session {session['id']}", key=f"delete_{session['id']}", type="primary"):
                    if session['id'] == data.get('current_session'):
                        # Don't allow deleting current session, create new one first
                        new_session = create_session()
                        st.warning(f"Deleted current session. Switched to new session {new_session['id']}")
                    else:
                        delete_session(session['id'])
                        st.success(f"Deleted session {session['id']}")
                    st.rerun()
