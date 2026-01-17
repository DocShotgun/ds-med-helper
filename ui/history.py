"""Session History UI Component"""

import streamlit as st

from core import get_all_sessions, get_session_by_id, create_session, delete_session, update_session


def render_session_history() -> None:
    """Render session history viewer"""
    st.header("📚 Session History")
    
    sessions = get_all_sessions()
    
    if not sessions:
        st.info("No previous sessions found.")
        return
    
    # Create a container for each session
    for session in sessions:
        with st.expander(f"Session {session['id']} - {session.get('updated_at', 'Unknown')[:19]}", expanded=False):
            st.json(session)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"Switch to Session {session['id']}", key=f"load_{session['id']}"):
                    st.session_state['selected_session_id'] = session['id']
                    st.success(f"Switched to session {session['id']}")
                    st.rerun()
            
            with col2:
                if st.button(f"Delete Session {session['id']}", key=f"delete_{session['id']}", type="primary"):
                    delete_session(session['id'])
                    st.success(f"Deleted session {session['id']}")
                    # Clear selected session if it was deleted
                    if st.session_state.get('selected_session_id') == session['id']:
                        st.session_state.pop('selected_session_id', None)
                    st.rerun()
