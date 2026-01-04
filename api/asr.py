"""ASR (Speech-to-Text) Functions"""

import aiohttp
import streamlit as st

# OpenAI-compatible endpoint paths
ASR_PATH = "/v1/audio/transcriptions"


async def asr_transcribe(
    audio_file,
    endpoint: str,
    model: str = "google/medasr"
) -> str:
    """
    Generic ASR function - transcribe audio using OpenAI-compatible endpoint.
    
    Per OpenAI API spec (POST /audio/transcriptions):
    - Required: file (audio) and model
    - Optional: language, prompt, response_format, temperature
    
    Args:
        audio_file: Audio file data
        endpoint: Base ASR endpoint URL (e.g., http://localhost:8000)
        model: ASR model name (default: google/medasr)
    
    Returns:
        Transcribed text or empty string on error
    """
    # Append OpenAI-compatible path
    full_endpoint = f"{endpoint.rstrip('/')}{ASR_PATH}"
    
    try:
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field('file', audio_file, filename='audio.wav', content_type='audio/wav')
            form.add_field('model', model)
            
            async with session.post(full_endpoint, data=form, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("text", "")
                else:
                    error_text = await resp.text()
                    st.error(f"ASR Error: {resp.status} - {error_text}")
                    return ""
    except Exception as e:
        st.error(f"ASR Error: {e}")
        return ""
