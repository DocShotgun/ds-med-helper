"""
DS Med Helper - Medical Documentation Assistant
A Streamlit-based web UI for physician documentation assistance.

Features:
- Scribe Mode: Record conversations/dictations and generate clinical notes
- Note Edit Mode: Edit and revise physician notes with AI assistance
- Synthesize Mode: Combine multiple sources into comprehensive notes
"""

from core import load_config
from ui import render_scribe_mode, render_edit_mode, render_synthesize_mode, render_settings, render_session_history, render_session_picker


def main():
    """Main application entry point"""
    # Load configuration
    config = load_config()
    
    import streamlit as st
    st.set_page_config(
        page_title="DS Med Helper",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main content
    st.title("🏥 DS Med Helper")
    
    # Session picker
    session = render_session_picker()
    
    # Navigation tabs (sticky)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Scribe", "✏️ Edit", "📋 Synthesize", "📚 History", "⚙️ Settings"])
    
    with tab1:
        render_scribe_mode(config, session)
    
    with tab2:
        render_edit_mode(config, session)
    
    with tab3:
        render_synthesize_mode(config, session)
    
    with tab4:
        render_session_history()
    
    with tab5:
        render_settings(config)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "*Copyright © 2026 Doctor Shotgun*"
    )


if __name__ == "__main__":
    main()
