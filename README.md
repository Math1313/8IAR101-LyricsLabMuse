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

