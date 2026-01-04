"""Template Loading Functions"""

from pathlib import Path
from typing import Optional, Dict, List, Any

import streamlit as st


def load_templates() -> List[Dict[str, Any]]:
    """Load templates from templates folder (.txt files)"""
    templates = []
    templates_dir = Path("templates")
    
    if templates_dir.exists() and templates_dir.is_dir():
        for template_file in sorted(templates_dir.glob("*.txt")):
            try:
                with open(template_file, 'r') as f:
                    content = f.read()
                    # Use filename (without extension) as the template name
                    # The file content IS the system prompt
                    template = {
                        'id': template_file.stem,
                        'name': template_file.stem.replace('_', ' ').title(),
                        'system_prompt': content.strip()
                    }
                    templates.append(template)
            except Exception as e:
                st.warning(f"Failed to load template {template_file}: {e}")
    
    return templates


def get_template_names() -> List[str]:
    """Get list of template names"""
    templates = load_templates()
    return [t['name'] for t in templates]


def get_template_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get template by name"""
    templates = load_templates()
    for t in templates:
        if t['name'] == name:
            return t
    return None


def get_fallback_templates() -> List[Dict[str, Any]]:
    """Get fallback templates from config.yaml"""
    from .config import load_config
    config = load_config()
    return config.get('templates', [])
