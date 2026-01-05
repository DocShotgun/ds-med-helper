"""Prompt Formatting Functions"""


def format_note_writing_prompt(transcript: str, template_prompt: str, context: str = "") -> str:
    """
    Format prompt for writing a new clinical note from transcript.
    
    Args:
        transcript: Audio transcription text
        template_prompt: Template instructions
        context: Additional context/instructions (optional)
    
    Returns:
        Formatted prompt for note writing
    """
    context_section = f"\n\nADDITIONAL CONTEXT/INSTRUCTIONS:\n---\n{context}\n---" if context.strip() else ""
    
    return f"""Based on the following transcript, create a clinical note, correcting for any transcription errors:

TRANSCRIPT:
---
{transcript}
---

NOTE TEMPLATE:
---
{template_prompt}
---
{context_section}

Respond only with the complete note adhering to the NOTE TEMPLATE. Do not provide chain of thought.
"""


def format_note_edit_prompt(original_note: str, instructions: str, template_prompt: str) -> str:
    """
    Format prompt for editing/revising an existing clinical note.
    
    Args:
        original_note: The original clinical note
        instructions: Edit instructions
        template_prompt: Template instructions
    
    Returns:
        Formatted prompt for note editing
    """
    return f"""Edit the following clinical note according to these instructions:

ORIGINAL NOTE:
---
{original_note}
---

NOTE TEMPLATE:
---
{template_prompt}
---

INSTRUCTIONS FOR EDIT:
---
{instructions}
---

Respond only with the complete edited note adhering to the NOTE TEMPLATE. Do not provide chain of thought.
"""
