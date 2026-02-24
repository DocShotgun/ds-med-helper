"""Settings UI Component"""

import json

import streamlit as st

from core import save_config


def reset_settings_session():
    """Reset session state to force re-initialization from config"""
    for key in list(st.session_state.keys()):
        if key.startswith('settings_'):
            del st.session_state[key]


def init_settings_session(config: dict) -> None:
    """Initialize settings session state from config if not already set"""
    if 'settings_host' not in st.session_state:
        server_config = config.get('server', {})
        llm_config = config.get('llm', {})
        stt_config = config.get('stt', {})
        
        st.session_state['settings_host'] = server_config.get('host', '0.0.0.0')
        st.session_state['settings_port'] = server_config.get('port', 8501)
        st.session_state['settings_llm_endpoint'] = llm_config.get('endpoint', 'http://localhost:8080')
        st.session_state['settings_llm_api_key'] = llm_config.get('api_key', '')
        st.session_state['settings_model'] = llm_config.get('model', 'google/medgemma-27b-text-it')
        st.session_state['settings_system_prompt'] = llm_config.get('system_prompt', '')
        st.session_state['settings_max_tokens'] = llm_config.get('max_tokens', -1)
        st.session_state['settings_temperature'] = llm_config.get('temperature', 0.8)
        st.session_state['settings_top_k'] = llm_config.get('top_k', 40)
        st.session_state['settings_top_p'] = llm_config.get('top_p', 0.95)
        st.session_state['settings_min_p'] = llm_config.get('min_p', 0.05)
        st.session_state['settings_stt_endpoint'] = stt_config.get('endpoint', 'http://localhost:8000')
        st.session_state['settings_stt_api_key'] = stt_config.get('api_key', '')
        st.session_state['settings_stt_model'] = stt_config.get('model', 'google/medasr')
        
        extra_params = llm_config.get('extra_api_params', {})
        st.session_state['settings_extra_api_params'] = json.dumps(extra_params) if extra_params else ''


def render_settings(config: dict) -> None:
    """Render settings page"""
    st.header("⚙️ Settings")
    st.markdown("Configure app settings and endpoints")
    
    # Initialize session state from config (only if not already set)
    init_settings_session(config)
    
    # Buttons at top
    col_save, col_reload = st.columns([1, 1])
    
    with col_save:
        if st.button("Save Settings", type="primary", icon="💾"):
            save_settings_from_session()
    
    with col_reload:
        if st.button("Reload Settings", icon="🔄", on_click=reset_settings_session):
            st.rerun()
    
    st.divider()
    
    # Server Configuration
    with st.expander("Server Configuration", expanded=True):
        st.text_input("Host", key="settings_host")
        st.number_input("Port", key="settings_port", min_value=1, max_value=65535)
    
    # LLM Configuration
    with st.expander("LLM Configuration", expanded=True):
        st.text_input("LLM Endpoint", key="settings_llm_endpoint", help="Base URL for llama.cpp server")
        st.text_input("API Key", key="settings_llm_api_key", type="password", help="Bearer token for authenticated endpoints")
        st.text_input("Model Name", key="settings_model")
        st.text_area("System Prompt", key="settings_system_prompt", height=150, help="Instructions for the LLM")
        st.number_input("Max Tokens", key="settings_max_tokens", min_value=-1)
        
        st.markdown("**Sampling Parameters**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.slider("Temperature", 0.0, 2.0, key="settings_temperature")
        with c2:
            st.slider("Top K", 0, 100, key="settings_top_k")
        with c3:
            st.slider("Top P", 0.0, 1.0, key="settings_top_p")
        with c4:
            st.slider("Min P", 0.0, 1.0, key="settings_min_p")
        
        st.text_area(
            "Extra API Parameters (JSON)",
            key="settings_extra_api_params",
            height=100,
            help='Additional parameters to pass to API (e.g., {"repeat_penalty": 1.1})'
        )
    
    # STT Configuration
    with st.expander("STT Configuration", expanded=True):
        st.text_input("STT Endpoint", key="settings_stt_endpoint", help="Base URL for ASR server")
        st.text_input("API Key", key="settings_stt_api_key", type="password", help="Bearer token for authenticated endpoints")
        st.text_input("STT Model", key="settings_stt_model", help="ASR model name")


def save_settings_from_session():
    """Save settings from session state to config file"""
    import streamlit as st
    from core import save_config
    
    config = {}
    config['server'] = {
        'host': st.session_state.get('settings_host', '0.0.0.0'),
        'port': int(st.session_state.get('settings_port', 8501))
    }
    config['llm'] = {
        'endpoint': st.session_state.get('settings_llm_endpoint', 'http://localhost:8080'),
        'api_key': st.session_state.get('settings_llm_api_key', ''),
        'model': st.session_state.get('settings_model', 'google/medgemma-27b-text-it'),
        'system_prompt': st.session_state.get('settings_system_prompt', ''),
        'max_tokens': int(st.session_state.get('settings_max_tokens', -1)) if st.session_state.get('settings_max_tokens', -1) > 0 else -1,
        'temperature': st.session_state.get('settings_temperature', 0.8),
        'top_k': st.session_state.get('settings_top_k', 40),
        'top_p': st.session_state.get('settings_top_p', 0.95),
        'min_p': st.session_state.get('settings_min_p', 0.05),
    }
    
    extra_params_str = st.session_state.get('settings_extra_api_params', '').strip()
    if extra_params_str:
        try:
            extra_params = json.loads(extra_params_str)
            if isinstance(extra_params, dict):
                config['llm']['extra_api_params'] = extra_params
            else:
                st.error("Extra API Parameters must be a JSON object (e.g., {\"key\": \"value\"})")
                return
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON in Extra API Parameters: {e}")
            return
    else:
        config['llm']['extra_api_params'] = {}
    config['stt'] = {
        'endpoint': st.session_state.get('settings_stt_endpoint', 'http://localhost:8000'),
        'api_key': st.session_state.get('settings_stt_api_key', ''),
        'model': st.session_state.get('settings_stt_model', 'google/medasr')
    }
    
    save_config(config)
    st.success("Settings saved! Reload the app to apply changes.")
