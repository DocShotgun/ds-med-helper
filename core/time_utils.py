"""Client-side time utilities for Streamlit"""

import streamlit as st
import json


def get_client_time_component(key: str = "client_time") -> str:
    """
    Get the client's current date and time using JavaScript.
    Returns the ISO formatted datetime string.
    """
    # Initialize session state for client time if not exists
    if key not in st.session_state:
        st.session_state[key] = None
    
    # If we already have client time, display it
    if st.session_state[key]:
        return st.session_state[key]
    
    # JavaScript to get client time and store in session state
    # This creates a hidden form that when submitted passes the time back
    import streamlit.components.v1 as components
    
    html = """
    <div id='time-placeholder' style='display:none;'></div>
    <script>
        const timeValue = new Date().toISOString();
        const timeInput = document.createElement('input');
        timeInput.type = 'hidden';
        timeInput.name = 'client_time';
        timeInput.value = timeValue;
        
        // Find the Streamlit form and submit it
        const forms = document.querySelectorAll('form');
        if (forms.length > 0) {
            const timeField = document.createElement('input');
            timeField.type = 'hidden';
            timeField.name = 'client_time';
            timeField.value = timeValue;
            forms[0].appendChild(timeField);
            
            // Store in sessionStorage for persistence
            sessionStorage.setItem('ds_client_time', timeValue);
        }
    </script>
    """
    
    # Alternative: Use Streamlit's setComponentValue if using custom components
    # For now, let's use a simpler approach with query params
    
    return None


def get_client_time_via_query_params() -> str:
    """
    Get client time using URL query parameters.
    Requires the page to be reloaded with the time in the URL.
    """
    # Check if time is in query params
    query_params = st.query_params
    
    if 'client_time' in query_params:
        return query_params['client_time']
    
    # Otherwise, inject JavaScript to reload with time
