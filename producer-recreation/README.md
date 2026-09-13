# Producer Recreation Pipeline

A clean, isolated workspace for recreating music production references using:
- **Serum 2.0.21** (VST3 synthesis)
- **Ableton Live 12.3** (MIDI/session control)
- **DawDreamer 0.9.0** (Serum host/control)
- **Structured Knowledge Extraction** (from YouTube transcripts)

## Architecture

```
YouTube URL
    ↓
source/fetch_youtube.py (external)
    ↓
data/transcripts/<source_id>.json (on-disk artifact)
    ↓
source/extract_knowledge.py (external)
    ↓
data/knowledge/<source_id>.json (structured KnowledgeItems)
    ↓
ProducerBrain (reasoning only on structured knowledge)
    ↓
Serum 2 + Ableton MCP (real execution)
    ↓
Verification & Episode Persistence
```

**Key Rule:** Raw transcript stays on disk. Claude Code reasoning context contains only structured KnowledgeItems.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Fetch transcript for a YouTube URL
python source/fetch_youtube.py "https://www.youtube.com/shorts/QqYlEc_6E6A"

# Extract structured knowledge
python source/extract_knowledge.py data/transcripts/yt_QqYlEc_6E6A.json

# Recreate the reference
python scripts/recreate_reference.py --url "https://www.youtube.com/shorts/QqYlEc_6E6A"
```

## Project Structure

- `producer/` - Core producer brain, authority, routing, execution
- `source/` - External transcript fetch & knowledge extraction
- `data/` - On-disk artifacts (transcripts, knowledge, episodes, references)
- `tests/` - Test suite
- `scripts/` - Entry points and utilities
