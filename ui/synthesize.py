"""Synthesize Mode UI Component"""

import streamlit as st

from api import llm_stream_to_list, format_note_synthesis_prompt, run_async
from core import load_templates, get_fallback_templates, update_session


def render_synthesize_mode(config: dict, session: dict) -> None:
    """Render the Synthesize Mode interface
    
    Args:
        config: Application configuration
        session: The currently selected session dict
    """
    st.header("📋 Synthesize Mode")
    st.markdown("Combine information from multiple sources to write a comprehensive clinical note.")
    
    # Initialize session state from persistent storage BEFORE creating widgets
    if 'synthesize_instructions' not in st.session_state:
        st.session_state['synthesize_instructions'] = session.get('synthesize_instructions', '')
    if 'synthesize_hp' not in st.session_state:
        st.session_state['synthesize_hp'] = session.get('synthesize_hp', '')
    if 'synthesize_consults' not in st.session_state:
        st.session_state['synthesize_consults'] = session.get('synthesize_consults', '')
    if 'synthesize_studies' not in st.session_state:
        st.session_state['synthesize_studies'] = session.get('synthesize_studies', '')
    if 'synthesize_progress' not in st.session_state:
        st.session_state['synthesize_progress'] = session.get('synthesize_progress', '')
    if 'synthesize_result' not in st.session_state:
        st.session_state['synthesize_result'] = session.get('synthesize_result', '')
    if 'synthesize_show_clear_confirm' not in st.session_state:
        st.session_state['synthesize_show_clear_confirm'] = False
    
    # Clear confirmation dialog
    if st.session_state.get('synthesize_show_clear_confirm'):
        @st.dialog("Clear Synthesize Fields?")
        def confirm():
            st.warning("Are you sure you want to clear all Synthesize fields? This cannot be undone.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Confirm", type="primary", key="synthesize_confirm_clear"):
                    # Clear all synthesize fields in session state
                    st.session_state['synthesize_instructions'] = ''
                    st.session_state['synthesize_hp'] = ''
                    st.session_state['synthesize_consults'] = ''
                    st.session_state['synthesize_studies'] = ''
                    st.session_state['synthesize_progress'] = ''
                    st.session_state['synthesize_result'] = ''
                    # Clear in persistent storage
                    update_session(session['id'], {
                        'synthesize_instructions': '',
                        'synthesize_hp': '',
                        'synthesize_consults': '',
                        'synthesize_studies': '',
                        'synthesize_progress': '',
                        'synthesize_result': ''
                    })
                    st.session_state['synthesize_show_clear_confirm'] = False
                    st.rerun()
            with col_no:
                if st.button("Cancel", key="synthesize_confirm_cancel"):
                    st.session_state['synthesize_show_clear_confirm'] = False
                    st.rerun()
        confirm()
    
    # Clear button at top
    col_clear, col_spacer = st.columns([1, 10])
    with col_clear:
        if st.button("🗑️ Clear All", type="secondary", key="synthesize_clear_btn"):
            st.session_state['synthesize_show_clear_confirm'] = True
            st.rerun()
    
    st.divider()
    
    # Get templates - first try loading from folder, fall back to config
    templates = load_templates()
    if not templates:
        templates = get_fallback_templates()
    
    template_options = {t['name']: t for t in templates}
    
    st.subheader("Input Information")

    col1, col2 = st.columns(2)

    with col1:
        def save_instructions():
            update_session(session['id'], {'synthesize_instructions': st.session_state.synthesize_instructions})
        
        st.text_area(
            "Synthesize Instructions",
            height=80,
            key="synthesize_instructions",
            on_change=save_instructions,
            placeholder="e.g., 'Write a Discharge Summary incorporating all available information'"
        )
        
        def save_hp():
            update_session(session['id'], {'synthesize_hp': st.session_state.synthesize_hp})
        
        st.text_area(
            "History and Physical",
            height=150,
            key="synthesize_hp",
            on_change=save_hp,
        )
        
        def save_consults():
            update_session(session['id'], {'synthesize_consults': st.session_state.synthesize_consults})
        
        st.text_area(
            "Consult Note(s)",
            height=150,
            key="synthesize_consults",
            on_change=save_consults,
        )
    
    with col2:
        def save_studies():
            update_session(session['id'], {'synthesize_studies': st.session_state.synthesize_studies})
        
        st.text_area(
            "Studies and Procedures",
            height=150,
            key="synthesize_studies",
            on_change=save_studies,
        )
        
        def save_progress():
            update_session(session['id'], {'synthesize_progress': st.session_state.synthesize_progress})
        
        st.text_area(
            "Progress Note(s)",
            height=150,
            key="synthesize_progress",
            on_change=save_progress,
        )
    
    # Template selection and generate
    st.subheader("📄 Note Generation")
    
    selected_template_name = st.selectbox(
        "Select Note Template",
        options=list(template_options.keys()),
        index=0,
        key="synthesize_template"
    )
    
    if st.button("📝 Generate Synthesized Note", type="primary", key="generate_synthesize_btn"):
        instructions = st.session_state.get('synthesize_instructions', '')
        hp = st.session_state.get('synthesize_hp', '')
        consults = st.session_state.get('synthesize_consults', '')
        studies = st.session_state.get('synthesize_studies', '')
        progress = st.session_state.get('synthesize_progress', '')
        
        # Check if at least one input field has content
        if any([hp, consults, studies, progress]):
            config_llm = config.get('llm', {})
            template = template_options[selected_template_name]
            
            prompt = format_note_synthesis_prompt(
                instructions=instructions,
                template_prompt=template['system_prompt'],
                hp=hp,
                consults=consults,
                studies=studies,
                progress=progress
            )
            
            with st.spinner("Synthesizing clinical note..."):
                chunks = run_async(llm_stream_to_list(
                    prompt=prompt,
                    system_prompt=config_llm.get('system_prompt', ''),
                    endpoint=config_llm.get('endpoint', ''),
                    model=config_llm.get('model', ''),
                    max_tokens=config_llm.get('max_tokens', -1),
                    temperature=config_llm.get('temperature', 0.8),
                    top_k=config_llm.get('top_k', 40),
                    top_p=config_llm.get('top_p', 0.95),
                    min_p=config_llm.get('min_p', 0.05)
                ))
                
                note_output = "".join(chunks)
                
                if note_output:
                    update_session(session['id'], {
                        'synthesize_result': note_output
                    })
                    st.session_state['synthesize_result'] = note_output
                    st.success("Note synthesized!")
                    st.rerun()
        else:
            st.warning("Please provide at least one source of information")
    
    # Show synthesized note
    if st.session_state.get('synthesize_result'):
        st.subheader("📃 Synthesized Clinical Note")
        st.code(st.session_state['synthesize_result'], language=None)
