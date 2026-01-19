"""Session History UI Component"""

import streamlit as st

from core import get_all_sessions, create_session, delete_session


# Confirmation dialogs
if 'confirm_delete_session_id' not in st.session_state:
    st.session_state['confirm_delete_session_id'] = None


def render_delete_confirmation(session_id: str):
    """Render confirmation dialog for deleting a single session"""
    @st.dialog(f"Delete Session {session_id}?")
    def confirm():
        st.warning(f"Are you sure you want to delete session {session_id}? This cannot be undone.")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Confirm", type="primary"):
                delete_session(session_id)
                if st.session_state.get('selected_session_id') == session_id:
                    st.session_state.pop('selected_session_id', None)
                st.session_state['confirm_delete_session_id'] = None
                st.rerun()
        with col_no:
            if st.button("Cancel"):
                st.session_state['confirm_delete_session_id'] = None
                st.rerun()
    
    confirm()


def render_clear_all_confirmation():
    """Render confirmation dialog for clearing all sessions"""
    @st.dialog("Clear All Sessions?")
    def confirm():
        sessions = get_all_sessions()
        st.warning(f"Are you sure you want to delete all {len(sessions)} sessions? This cannot be undone.")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("Confirm", type="primary"):
                for session in sessions:
                    delete_session(session['id'])
                new_session = create_session()
                st.session_state['selected_session_id'] = new_session['id']
                st.query_params['session_id'] = new_session['id']
                st.success("All sessions cleared. Created new session.")
                st.rerun()
        with col_no:
            if st.button("Cancel"):
                st.rerun()
    
    confirm()


def render_session_history() -> None:
    """Render session history viewer"""
    st.header("📚 Session History")
    st.markdown("Manage sessions and view history")
    
    # Check if we need to show confirmation dialogs
    if st.session_state.get('confirm_delete_session_id'):
        render_delete_confirmation(st.session_state['confirm_delete_session_id'])
    
    # Session management buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Create New Session", type="primary", icon="📚"):
            new_session = create_session()
            st.session_state['selected_session_id'] = new_session['id']
            st.query_params['session_id'] = new_session['id']
            st.success(f"Created new session: {new_session['id']}")
            st.rerun()
    
    with col2:
        if st.button("Clear All Sessions", type="secondary", icon="🗑️"):
            render_clear_all_confirmation()
    
    st.divider()
    
    # Session list
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
                if st.button(f"Switch to Session {session['id']}", key=f"load_{session['id']}", type="primary", icon="🔄"):
                    st.session_state['selected_session_id'] = session['id']
                    st.query_params['session_id'] = session['id']
                    st.success(f"Switched to session {session['id']}")
                    st.rerun()
            
            with col2:
                if st.button(f"Delete Session {session['id']}", key=f"delete_{session['id']}", type="secondary", icon="🗑️"):
                    st.session_state['confirm_delete_session_id'] = session['id']
                    st.rerun()
