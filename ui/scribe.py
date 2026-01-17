"""Scribe Mode UI Component"""

import streamlit as st

from api import asr_transcribe, llm_stream_to_list, format_note_writing_prompt, run_async
from core import load_templates, get_fallback_templates, update_session


def render_scribe_mode(config: dict, session: dict) -> None:
    """Render the Scribe Mode interface
    
    Args:
        config: Application configuration
        session: The currently selected session dict
    """
    st.header("📝 Scribe Mode")
    st.markdown("Record patient encounters or dictations and generate clinical notes")
    
    # Initialize session state from persistent storage BEFORE creating widgets
    # This allows Streamlit to use session state as default without conflicting with value parameter
    if 'transcript_edit' not in st.session_state:
        st.session_state['transcript_edit'] = session.get('scribe_transcript', '')
    if 'scribe_note' not in st.session_state:
        st.session_state['scribe_note'] = session.get('scribe_note', '')
    if 'scribe_context_input' not in st.session_state:
        st.session_state['scribe_context_input'] = session.get('scribe_context', '')
    
    # Get templates - first try loading from folder, fall back to config
    templates = load_templates()
    if not templates:
        templates = get_fallback_templates()
    
    template_options = {t['name']: t for t in templates}
    
    # Audio recording / upload
    st.subheader("🎙️ Recording")
    
    col_record, col_upload = st.columns(2)
    
    with col_record:
        audio_input = st.audio_input("Record patient encounter or dictation", key="audio_input_scribe")
    
    with col_upload:
        uploaded_file = st.file_uploader("Upload audio file", type=['wav', 'mp3', 'm4a', 'ogg'], key="audio_upload_scribe")
    
    # Use uploaded file if provided, otherwise use recording
    audio_to_use = uploaded_file if uploaded_file is not None else audio_input
    
    # Transcribe button and result
    st.subheader("📝 Transcription")
    
    if audio_to_use is not None:
        # Get audio bytes for display/download
        if hasattr(audio_to_use, 'read'):
            audio_bytes = audio_to_use.read()
        else:
            audio_bytes = audio_to_use
        
        st.audio(audio_bytes)
        
        # Download button for the recording
        col_download, col_transcribe = st.columns([1, 3])
        
        with col_download:
            st.download_button(
                "💾 Download Recording",
                data=audio_bytes,
                file_name=f"recording_{session['id']}.wav",
                mime="audio/wav"
            )
        
        with col_transcribe:
            if st.button("Transcribe Audio", type="primary", key="transcribe_btn"):
                with st.spinner("Transcribing..."):
                    config_stt = config.get('stt', {})
                    transcript_result = run_async(asr_transcribe(
                        audio_bytes,
                        config_stt.get('endpoint', ''),
                        config_stt.get('model', 'google/medasr')
                    ))
                    
                    if transcript_result:
                        # Update persistent session storage
                        update_session(session['id'], {
                            'scribe_transcript': transcript_result
                        })
                        # Update session state and rerun
                        st.session_state['transcript_edit'] = transcript_result
                        st.rerun()
    else:
        st.info("Record audio or upload a file to begin")
    
    # Editable transcription area
    def save_transcript():
        update_session(session['id'], {'scribe_transcript': st.session_state.transcript_edit})
    
    transcript = st.text_area(
        "Edit transcription",
        height=200,
        key="transcript_edit",
        on_change=save_transcript,
        placeholder="Transcription will appear here after recording"
    )
    
    # Additional context/instructions
    st.subheader("📋 Additional Context / Instructions")
    
    def save_context():
        update_session(session['id'], {'scribe_context': st.session_state.scribe_context_input})
    
    context = st.text_area(
        "Optional: Add pre-existing notes, context, or special instructions",
        height=100,
        key="scribe_context_input",
        on_change=save_context,
        placeholder="e.g., 'Update the following Progress Note with the interval events dictated above...'"
    )
    
    # Template selection
    st.subheader("📄 Note Generation")
    
    selected_template_name = st.selectbox(
        "Select note template",
        options=list(template_options.keys()),
        index=0,
        key="scribe_template",
        on_change=lambda: update_session(session['id'], {'scribe_template': selected_template_name})
    )
    
    if st.button("Generate Note", type="primary", key="generate_note_btn"):
        if transcript.strip():
            config_llm = config.get('llm', {})
            template = template_options[selected_template_name]
            
            prompt = format_note_writing_prompt(transcript, template['system_prompt'], context)
            
            with st.spinner("Generating clinical note..."):
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
                        'scribe_note': note_output
                    })
                    st.session_state['scribe_note'] = note_output
                    st.success("Note generated!")
                    st.rerun()
        else:
            st.warning("Please provide a transcription first")
    
    # Show generated note
    generated_note = st.session_state.get('scribe_note') or session.get('scribe_note', '')
    if generated_note:
        st.subheader("📃 Generated Clinical Note")
        st.code(generated_note, language=None)
