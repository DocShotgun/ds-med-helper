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

Respond only with the complete note in plain text, adhering to the NOTE TEMPLATE. Do not provide chain of thought.
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

Respond only with the complete edited note in plain text, adhering to the NOTE TEMPLATE. Do not provide chain of thought.
"""


def format_note_synthesis_prompt(
    instructions: str,
    template_prompt: str,
    hp: str = "",
    consults: str = "",
    studies: str = "",
    progress: str = ""
) -> str:
    """
    Format prompt for synthesizing information from multiple sources into a clinical note.
    
    Args:
        instructions: Synthesis instructions
        hp: History and Physical information (optional)
        consults: Consult note(s) information (optional)
        studies: Studies and procedures information (optional)
        progress: Progress note(s) information (optional)
        template_prompt: Template instructions
    
    Returns:
        Formatted prompt for note synthesis
    """
    # Build the synthesis input section
    synthesis_parts = []
    
    if hp.strip():
        synthesis_parts.append(f"<HISTORY_AND_PHYSICAL>\n{hp}\n</HISTORY_AND_PHYSICAL>")
    
    if consults.strip():
        synthesis_parts.append(f"<CONSULT_NOTES>\n{consults}\n</CONSULT_NOTES>")
    
    if studies.strip():
        synthesis_parts.append(f"<STUDIES_AND_PROCEDURES>\n{studies}\n</STUDIES_AND_PROCEDURES>")
    
    if progress.strip():
        synthesis_parts.append(f"<PROGRESS_NOTES>\n{progress}\n</PROGRESS_NOTES>")
    
    synthesis_section = "\n".join(synthesis_parts)
    
    return f"""Synthesize the following information into a clinical note:

SOURCE INFORMATION:
---
{synthesis_section}
---

NOTE TEMPLATE:
---
{template_prompt}
---

INSTRUCTIONS FOR SYNTHESIS:
---
{instructions}
---

Respond only with the complete synthesized note in plain text, adhering to the NOTE TEMPLATE. Do not provide chain of thought.
"""
