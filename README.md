# LyricsLabMuse
## Get started
- Clone the repository
- Setup environment variables
    - Create a `.env` file in the root directory
    - Add the following variables
        ```
        MODEL_URL=http://localhost:1234/v1
        ```
    - You can specify the URL you want. In this case, we use localhost as the model is running locally.
- Install requiered libraries
    ```
    pip install -r requirements.txt
    ```
- Create ChromaDB with RAG data
    ```
    py create_rag_data.py
    ```

## *********Pour Audiocraft ===>> EXPLOSION de l'environnement:D
### Install Python 3.10
### Clean or delete requirements:
#### clean:
pip uninstall -y -r requirements.txt     
pip uninstall -y -r requirements_audiocraft.txt
#### delete
- delete :D
### Recréer env:
#### ```deactivate```
#### ```rmdir /s /q .venv_audiocraft``` ou  ```rm -rf .venv_audiocraft```
#### pour savoir le path de python:
##### ```where python```
##### ```py -0```

#### Command pour créer l'env
##### ```py -3.10 -m venv .venv_audiocraft```
##### ou ```C:\Path\To\Python310\python.exe -m venv .venv_audiocraft```
### Install requirements:

#### ```python -m venv .venv_audiocraft --clear```

#### ```.\.venv_audiocraft\Scripts\activate```
#### ```python install_audiocraft_requirements.py```


### Switch env 
- to see which env :
  ```
  where python
  ```
- to exit env:
  ```
  deactivate
  ```
- to activate env
  ```
  .\venv_name\Scripts\activate
  ``` 
- current environements
  ``` 
  .\venv\Scripts\activate
  .\venv_audiocraft\Scripts\activate
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




# REQUIREMENT NEW PROCEDURE TEST
# 1. Clean environment
deactivate
delete .venv

# 2. Create new environment
py -3.10 -m venv .venv_audiocraft --clear --system-site-packages
.\.venv_audiocraft\Scripts\activate

# 3. Upgrade pip
python -m pip install --upgrade pip

# Install build tools
pip install --upgrade setuptools wheel

Install Visual C++ Build Tools:
Download and install Visual Studio Build Tools 2019 from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
During installation, select "Desktop development with C++"


# Install base requirements first
pip install -r base-requirements.txt

# Install scikit-learn separately
pip install scikit-learn==1.3.0

# Install RAG requirements
pip install -r base-rag-requirements.txt

# Install PyTorch and related packages
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu

# Install audiocraft
pip install audiocraft

# Install GUI requirements
pip install -r gui-requirements.txt

REDO
# Make sure you're in your virtual environment
.\venv\Scripts\activate

# Clear any existing packages (optional, but recommended if you're having conflicts)
pip uninstall -y numpy langchain langchain-community langchain-chroma
pip cache purge

# Install base requirements with fixed numpy version
pip install wheel>=0.42.0 setuptools>=65.5.1 python-dotenv==1.0.1 pydantic>=2.7.4 requests>=2.32.3
pip install numpy==1.24.3

# Install RAG requirements
pip install langchain==0.3.11 langchain-community==0.3.11 langchain-core>=0.3.18 langchain-chroma==0.1.4
pip install langchain-openai>=0.2.8 openai>=1.54.0
pip install sentence-transformers>=2.2.2 chromadb==0.5.23 tokenizers==0.20.3 pypdf>=3.17.1

# Install audiocraft requirements
pip install scipy==1.11.4 scikit-learn==1.3.0
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu
pip install audiocraft

# Install GUI requirements
pip install PyQt5==5.15.11