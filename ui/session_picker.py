"""Session Picker UI Component"""

import streamlit as st

from core import get_all_sessions, get_session_by_id, create_session


def init_session_state():
    """Initialize session state for the current browser using URL params"""
    # Get session_id from URL query params, or default to first session
    query_params = st.query_params
    
    # Check if session_id is in URL
    if 'session_id' in query_params:
        url_session_id = query_params['session_id']
        # Verify the session exists
        if get_session_by_id(url_session_id):
            st.session_state['selected_session_id'] = url_session_id
            return
    
    # If no URL param or session doesn't exist, use session state or default
    if 'selected_session_id' not in st.session_state:
        sessions = get_all_sessions()
        if sessions:
            st.session_state['selected_session_id'] = sessions[0]['id']
        else:
            new_session = create_session()
            st.session_state['selected_session_id'] = new_session['id']
    
    # Set URL params to match current session (for bookmarking)
    st.query_params['session_id'] = st.session_state['selected_session_id']


def get_selected_session() -> dict:
    """Get the currently selected session"""
    init_session_state()
    session_id = st.session_state.get('selected_session_id')
    
    if session_id:
        session = get_session_by_id(session_id)
        if session:
            return session
    
    # Fallback: create a new session
    new_session = create_session()
    st.session_state['selected_session_id'] = new_session['id']
    return new_session


def render_session_picker() -> dict:
    """
    Render session picker at the top of the app.
    Uses URL query parameters to persist session selection across refreshes.
    
    Returns:
        The currently selected session dict
    """
    # Initialize session state FIRST (may create session)
    init_session_state()
    
    # Get sessions AFTER init (so we have the latest)
    sessions = get_all_sessions()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if sessions:
            session_options = {s['id']: f"{s['id']} ({s.get('updated_at', '')[:10]})" for s in sessions}
            current_id = st.session_state.get('selected_session_id', sessions[0]['id'])
            
            selected_id = st.selectbox(
                "Session",
                options=list(session_options.keys()),
                format_func=lambda x: session_options[x],
                index=list(session_options.keys()).index(current_id) if current_id in session_options else 0,
                key="session_picker_select",
                label_visibility="collapsed"
            )
            
            if selected_id != st.session_state.get('selected_session_id'):
                st.session_state['selected_session_id'] = selected_id
                # Update URL to persist selection
                st.query_params['session_id'] = selected_id
                st.rerun()
        else:
            st.info("No sessions yet")
            selected_id = None
    
    with col2:
        if st.button("📚 New Session", type="primary"):
            new_session = create_session()
            st.session_state['selected_session_id'] = new_session['id']
            # Update URL
            st.query_params['session_id'] = new_session['id']
            st.rerun()
    
    # Return the selected session
    if selected_id:
        return get_session_by_id(selected_id)
    elif sessions:
        return sessions[0]
    else:
        return create_session()
