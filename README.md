# LyricsLabMuse

## Get started
### 1. Clone the repository
```bash
git clone https://github.com/Math1313/8IAR101-LyricsLabMuse.git
```
### 2. Create Virtual Environment
You will need to install python 3.9.
First, create a virtual environment:

```bash
# Windows
py -3.9 -m venv .venv

# Unix/MacOS
python3.9 -m venv .venv
```

### 2. Activate Virtual Environment

```bash
# Windows
.\.venv\Scripts\activate 

# Unix/MacOS
source .venv/bin/activate
```

### 3. Install Dependencies

Install all required packages using the requirements file:

```bash
pip install -r requirements.txt
```
### 4. Setup environment variables
- Create a `.env` file in the root directory
- Add the following variables
```bash
MODEL_URL=http://localhost:1234/v1
```
- You can specify the URL you want. In this case, we use localhost as the model is running locally.

### 5. Create ChromaDB with RAG data
``` bash
py src/core/create_rag_data.py
```
<!-- # *********Pour Audiocraft ===>> EXPLOSION de l'environnement:D
### pip fresh start
pip freeze > installed_packages.txt
pip uninstall -r installed_packages.txt -y
### Install Python 3.9
### Delete env
### python 3.9 env
py -3.9 -m venv .venv_audiocraft
.\.venv_audiocraft\Scripts\activate
### install dependencies
pip install wheel setuptools numpy==1.24.3
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu
pip install audiocraft -->
## Project Structure
```bash
8IAR101-LyricsLabMuse/
├── .env
├── .venv
├── docs/
├── ragData/
│   └── commonMusicGenreStructure.pdf
├── src/
│   ├── core/
│   │   ├── audiocraft_generator.py
│   │   ├── create_rag_data.py
│   │   ├── music_composition_experts.py
│   │   ├── music_composition_export_formatter.py
│   │   └── rag_helper.py
│   ├── gui/
│   │   ├── components/
│   │   │   └── ui/
│   │   │       ├── __init__.py
│   │   │       └── audio_controls.py
│   │   ├── __init__.py
│   │   └── LyricsLabMuse.py
│   ├── services/
│   └── utils/
├── .env
├── .gitignore
├── project_structure.md
├── README.md
└── requirements.txt
```

[//]: # (TODO)
## TODO
### Problème avec le output (chords/lyrics/melody) -> on a plustot une analyse de la chanson
### Implémenter le output audiogen
### FIX PROMPT TEMPLATE dans rag_helper:
Give answer based only on the following context: {context}
What is the {music_style} Music Typical Structure?
I want to know the number of verse, chorus, and bridge in a typical {music_style} music.
Do a list that looks like this:
Intro - Verse - Chorus - Verse - etc...
I just want the list.
### FILTRAGE VULGAIRE
### audio_generation.json: modif URL & api key




