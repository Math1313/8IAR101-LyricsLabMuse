# LyricsLabMuse

## Project Structure
```bash
8IAR101-LyricsLabMuse/
├── .env
├── .venv/
├── chroma/
├── docs/
├── output/
├── ragData/
│   └── commonMusicGenreStructure.pdf
├── src/
│   ├── core/
│   │   ├── audiocraft_generator.py
│   │   ├── create_rag_data.py
│   │   ├── music_composition_experts.py
│   │   ├── music_composition_export_formatter.py
│   │   └── obscene_filter.py
│   │   └── rag_helper.py
│   ├── gui/
│   │   ├── components/
│   │   │   └── audio_controls.py
│   │   │   └── audio_threads.py
│   │   │   └── stream_thread.py
│   │   │   └── themes.py
├── .gitignore
├── README.md
├── LyricsLabMuse.py
└── requirements.txt
```

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
Install the required packages using the 3 bash cmd first and then requirements file:

```bash
pip install wheel setuptools numpy==1.24.3
```
```bash
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu
```
```bash
pip install audiocraft
```
```bash
pip install -r requirements.txt
```
### 4. Setup environment variables
- Create a `.env` file in the root directory
- Add the following variables
```bash
MODEL_URL="http://localhost:1234/v1"
```
- You can specify the URL you want. In this case, we use localhost as the model is running locally.

### 5. Create ChromaDB with RAG data
``` bash
py src/core/create_rag_data.py
```

### 6. Run the app
``` bash
py .\LyricsLabMuse.py
```

## Issues
- [x] Problème avec le output chords/lyrics/melody -> on a plutôt une analyse de la chanson
- [x] Fix PROMPT_TEMPLATE rag_helper
- [ ] Problème avec le nom de fichier audio généré
## Improvements
- [X] Implémenter le output audiogen
- [x] Filtrage vulgaire
- [ ] Créer une procédure pour rendre le projet exécutable (.exe)
- [ ] Implémenter la modification de prompt
- [ ] Générer des songs avec des longueurs différentes
- [ ] Générer des paroles à partir des lyrics (synthèse vocale)




