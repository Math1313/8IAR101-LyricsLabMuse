# LyricsLabMuse Project Structure

## Environment
- `.venv/` - Main virtual environment
- `.venv_audiocraft/` - Audiocraft-specific virtual environment

## Core Modules
- `audio_generation/`
  - `__init__.py`
  - `audiocraft_generator.py`
  - `utils.py`

## Data
- `chroma/`
  - `eb041ab6-2347-49c3-af9a-d28b1cc273fc/`
  - `chroma.sqlite3`
- `ragData/`
  - `commonMusicGenreStructure.pdf`

## Documentation
- `docs/`

## Resources
- `resources/`

## Source
- `src/`
  - `config/`
    - `audio_generation.json`
    - `core/`
    - `gui/`
    - `services/`
    - `utils/`

## Testing
- `tests/`

## User Interface
- `ui/`
  - `__init__.py`
  - `audio_controls.py`
  - `.env`

## Root Files
- `.gitignore`
- `audio_generator_adapter.py`
- `create_rag_data.py`
- `LyricsLabMuse.py`
- `music_composition_experts.py`
- `music_composition_export_formatter.py`
- `pIAno_man.py`
- `rag_helper.py`
- `README.md`
- `requirements.txt`
- `test_audiocraft.py`