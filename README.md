# DS Med Helper

A Streamlit-based web UI for physician medical documentation assistance using OpenAI API compatible LLM and ASR endpoints.

## Features

- **Scribe Mode**: Record patient encounters or dictations and generate clinical notes automatically
- **Note Edit Mode**: Edit physician notes with AI assistance
- **Synthesize Mode**: Combine information from multiple sources (H&P, Consults, Studies, Progress Notes) to write comprehensive notes
- **Session Persistence**: Sessions are saved automatically and can be restored
- **Configurable Endpoints**: Connect to your custom OpenAI API compatible LLM and ASR endpoints
- **Template System**: Customizable note templates (H&P, Progress Note, Consultation, Discharge Summary)
- **Sampling Controls**: Adjust temperature, top_k, top_p, and min_p for LLM output
- **Editable System Prompt**: Customize LLM behavior through the Settings UI

## Requirements

- Python 3.9+
- Streamlit
- PyYAML
- aiohttp

## Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to configure your endpoints and LLM parameters:

```yaml
server:
  host: "0.0.0.0"  # Listen on all interfaces
  port: 8501

llm:
  endpoint: "http://localhost:8080"
  model: "google/medgemma-27b-text-it"
  system_prompt: "You are a medical documentation assistant..."
  max_tokens: -1         # -1 for unlimited
  temperature: 0.8
  top_k: 40
  top_p: 0.95
  min_p: 0.05

stt:
  endpoint: "http://localhost:8000"
  model: "google/medasr"

session:
  max_history: 100
  storage_file: "sessions/session_data.json"
```

### Runtime Settings

Many settings can be adjusted through the Settings UI:
- Endpoints (LLM and STT)
- System prompt for the LLM
- Model names
- Sampling parameters (temperature, top_k, top_p, min_p)
- Session management

## Running

```bash
# Run the app
streamlit run app.py

# Or with custom host/port
streamlit run app.py --server.host 0.0.0.0 --server.port 8501
```

## Templates

Note templates are stored as `.txt` files in the `templates/` folder. Edit these files to customize the system prompts for each note type.

## Usage

### Scribe Mode
1. Select a note template from the dropdown
2. Record audio using the browser's audio input OR upload a file
3. Click "Transcribe Audio" to convert speech to text
4. Review/edit the transcript if needed
5. Optionally add context/instructions
6. Click "Generate Note" to create the clinical note
7. Download the recording if needed

### Note Edit Mode
1. Paste your original clinical note in the left panel
2. Optionally select a template for context
3. Enter revision instructions (e.g., "Summarize to 3 bullet points")
4. Click "Generate Edited Note"

### Synthesize Mode
1. Enter synthesis instructions (optional)
2. Fill in source information fields:
   - History and Physical
   - Consult Note(s)
   - Studies and Procedures
   - Progress Note(s)
3. Select a note template
4. Click "Generate Synthesized Note" to create a comprehensive clinical note from multiple sources

### Settings
- Configure endpoints for LLM and STT servers
- Edit system prompt for LLM behavior
- Adjust sampling parameters (temperature, top_k, top_p, min_p)
- View, create, or clear sessions

### Session Management
- Each browser maintains its own selected session via URL parameters (`?session_id=xxx`)
- Use the session picker dropdown at the top to switch between sessions
- Bookmark the URL to return to your active session after closing the browser
- "New Session" button creates a fresh session for the current browser
- Session history shows all sessions with ability to switch or delete

## Access

When running on your home server:
- Local: `http://localhost:8501`
- Remote (VPN): `http://<server-ip>:8501`
