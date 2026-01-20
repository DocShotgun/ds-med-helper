"""Note Edit Mode UI Component"""

import streamlit as st

from api import llm_stream_to_list, format_note_edit_prompt, run_async
from core import load_templates, get_fallback_templates, update_session


def render_edit_mode(config: dict, session: dict) -> None:
    """Render the Note Edit Mode interface
    
    Args:
        config: Application configuration
        session: The currently selected session dict
    """
    st.header("✏️ Note Edit Mode")
    st.markdown("Edit physician notes with AI assistance")
    
    # Initialize session state from persistent storage BEFORE creating widgets
    if 'original_note_area' not in st.session_state:
        st.session_state['original_note_area'] = session.get('edit_original', '')
    if 'edit_instr' not in st.session_state:
        st.session_state['edit_instr'] = session.get('edit_instructions', '')
    if 'edit_result' not in st.session_state:
        st.session_state['edit_result'] = session.get('edit_result', '')
    if 'edit_show_clear_confirm' not in st.session_state:
        st.session_state['edit_show_clear_confirm'] = False
    
    # Clear confirmation dialog
    if st.session_state.get('edit_show_clear_confirm'):
        @st.dialog("Clear Edit Fields?")
        def confirm():
            st.warning("Are you sure you want to clear all Edit fields? This cannot be undone.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Confirm", type="primary", key="edit_confirm_clear"):
                    # Clear all edit fields in session state
                    st.session_state['original_note_area'] = ''
                    st.session_state['edit_instr'] = ''
                    st.session_state['edit_result'] = ''
                    # Clear in persistent storage
                    update_session(session['id'], {
                        'edit_original': '',
                        'edit_instructions': '',
                        'edit_result': ''
                    })
                    st.session_state['edit_show_clear_confirm'] = False
                    st.rerun()
            with col_no:
                if st.button("Cancel", key="edit_confirm_cancel"):
                    st.session_state['edit_show_clear_confirm'] = False
                    st.rerun()
        confirm()
    
    # Clear button at top
    col_clear, col_spacer = st.columns([1, 10])
    with col_clear:
        if st.button("Clear All", type="secondary", key="edit_clear_btn", icon="🗑️"):
            st.session_state['edit_show_clear_confirm'] = True
            st.rerun()
    
    st.divider()
    
    # Get templates - first try loading from folder, fall back to config
    templates = load_templates()
    if not templates:
        templates = get_fallback_templates()
    
    template_options = {t['name']: t for t in templates}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Note")
        
        # Auto-save original note
        def save_original_note():
            update_session(session['id'], {'edit_original': st.session_state.original_note_area})
        
        original_note = st.text_area(
            "Paste your clinical note here",
            height=400,
            key="original_note_area",
            on_change=save_original_note
        )
    
    with col2:        
        st.subheader("Edit Instructions")
        
        # Auto-save instructions
        def save_instructions():
            update_session(session['id'], {'edit_instructions': st.session_state.edit_instr})
        
        instructions = st.text_area(
            "Describe what changes you want",
            height=150,
            placeholder="e.g., 'Make the HPI more concise' or 'Clean up the Assessment/Plan formatting'",
            key="edit_instr",
            on_change=save_instructions
        )

        # Template selection
        selected_template_name = st.selectbox(
            "Select note template",
            options=list(template_options.keys()),
            index=0,
            key="edit_template"
        )
        
        can_edit = original_note and instructions
        if st.button("Generate Edited Note", type="primary", key="generate_edit_btn", icon="📝", disabled=not can_edit):
            if can_edit:
                config_llm = config.get('llm', {})
                template = template_options[selected_template_name]
                
                prompt = format_note_edit_prompt(original_note.strip(), instructions.strip(), template['system_prompt'])
                
                with st.spinner("Editing note..."):
                    chunks = run_async(llm_stream_to_list(
                        prompt=prompt,
                        system_prompt=config_llm.get('system_prompt', ''),
                        endpoint=config_llm.get('endpoint', ''),
                        model=config_llm.get('model', ''),
                        api_key=config_llm.get('api_key', ''),
                        max_tokens=config_llm.get('max_tokens', -1),
                        temperature=config_llm.get('temperature', 0.8),
                        top_k=config_llm.get('top_k', 40),
                        top_p=config_llm.get('top_p', 0.95),
                        min_p=config_llm.get('min_p', 0.05)
                    ))
                    
                    edited_output = "".join(chunks)
                    
                    if edited_output:
                        update_session(session['id'], {
                            'edit_result': edited_output
                        })
                        st.session_state['edit_result'] = edited_output
                        st.success("Edit complete!")
    
    # Show edited note if it exists in session state
    if st.session_state.get('edit_result'):
        st.subheader("Edited Note")
        st.code(st.session_state['edit_result'], language=None)
