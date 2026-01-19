"""Settings UI Component"""

import streamlit as st

from core import save_config


def render_settings(config: dict) -> None:
    """Render settings page"""
    st.header("⚙️ Settings")
    st.markdown("Configure app settings and endpoints")

    st.divider()
    
    with st.expander("Server Configuration", expanded=True):
        server_config = config.get('server', {})
        new_host = st.text_input("Host", value=server_config.get('host', '0.0.0.0'))
        new_port = st.number_input("Port", value=server_config.get('port', 8501), min_value=1, max_value=65535)
    
    with st.expander("LLM Configuration", expanded=True):
        llm_config = config.get('llm', {})
        new_llm_endpoint = st.text_input(
            "LLM Endpoint",
            value=llm_config.get('endpoint', 'http://localhost:8080'),
            help="Base URL for llama.cpp server (e.g., http://localhost:8080)"
        )
        new_model = st.text_input("Model Name", value=llm_config.get('model', 'google/medgemma-27b-text-it'))
        new_system_prompt = st.text_area(
            "System Prompt",
            value=llm_config.get('system_prompt', ''),
            height=150,
            help="Instructions for the LLM on how to generate clinical notes"
        )
        new_max_tokens = st.number_input("Max Tokens", value=llm_config.get('max_tokens', -1), min_value=-1)
        
        st.markdown("**Sampling Parameters**")
        col_temp, col_topk, col_topp, col_minp = st.columns(4)
        with col_temp:
            new_temperature = st.slider("Temperature", 0.0, 2.0, llm_config.get('temperature', 0.8))
        with col_topk:
            new_top_k = st.slider("Top K", 0, 100, llm_config.get('top_k', 40))
        with col_topp:
            new_top_p = st.slider("Top P", 0.0, 1.0, llm_config.get('top_p', 0.95))
        with col_minp:
            new_min_p = st.slider("Min P", 0.0, 1.0, llm_config.get('min_p', 0.05))
    
    with st.expander("STT Configuration", expanded=True):
        stt_config = config.get('stt', {})
        new_stt_endpoint = st.text_input(
            "STT Endpoint",
            value=stt_config.get('endpoint', 'http://localhost:8000'),
            help="Base URL for ASR server (e.g., http://localhost:8000)"
        )
        new_stt_model = st.text_input(
            "STT Model",
            value=stt_config.get('model', 'google/medasr'),
            help="ASR model name"
        )
    
    col_save, col_reload = st.columns([1, 1])
    
    with col_save:
        if st.button("Save Settings", type="primary", icon="💾"):
            config['server'] = {'host': new_host, 'port': int(new_port)}
            config['llm'] = {
                'endpoint': new_llm_endpoint,
                'model': new_model,
                'system_prompt': new_system_prompt,
                'max_tokens': int(new_max_tokens) if new_max_tokens > 0 else -1,
                'temperature': new_temperature,
                'top_k': new_top_k,
                'top_p': new_top_p,
                'min_p': new_min_p,
            }
            config['stt'] = {'endpoint': new_stt_endpoint, 'model': new_stt_model}
            save_config(config)
            st.success("Settings saved! Restart the app to apply changes.")
    
    with col_reload:
        if st.button("Reload Settings", icon="🔄"):
            st.rerun()
