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
    py create_chroma_db.py
    ```

## TODO

### Problème avec le output (chords/lyrics/melody) -> on a plustot une analyse de la chanson
### Implémenter le output audiogen
### 
