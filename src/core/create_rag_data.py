import os
import sqlite3
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_chroma import Chroma

CHROMA_PATH = "../../chroma/"
DATA_PATH = "../../ragData/"

embedding_function = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2")


def split_text(documents: list[Document]):
    """
    Split the text content of the given list of Document objects into smaller chunks.
    Args:
      documents (list[Document]): List of Document objects containing text content to split.
    Returns:
      list[Document]: List of Document objects representing the split text chunks.
    """
    # Initialize text splitter with specified parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,  # Size of each chunk in characters
        chunk_overlap=150,  # Overlap between consecutive chunks
        length_function=len,  # Function to compute the length of the text
        add_start_index=True,  # Flag to add start index to each chunk
    )

    # Split documents into smaller chunks using text splitter
    chunks = text_splitter.split_documents(documents)

    return chunks  # Return the list of split text chunks


def save_to_chroma(chunks: list[Document]):
    """
    Save the given list of Document objects to a Chroma database.
    Args:
    chunks (list[Document]): List of Document objects representing text chunks to save.
    append (bool): Flag to indicate whether to append to the existing database or recreate it.
    Returns:
    None
    """

    db = Chroma.from_documents(
        chunks,
        embedding_function,
        persist_directory=CHROMA_PATH
    )
    # Print the number of chunks saved to the database
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


def check_database(db_path):
    """
    Try to connect to the database and check if it is empty or not.
    Args:
    db_path (str): Path to the database file.
    Returns:
    str: "empty" if the database is empty, "not-empty" if it is not empty, or "not-created" if the database does not exist.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT count(name) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]

        conn.close()
        if table_count == 0:
            return "empty"
        else:
            return "not-empty"
    except Exception as e:
        print("Database is not created ", e)
        return "not-created"


def validate_files_in_db(data_path, db_path):
    # List all files in DATA_PATH avec le chemin complet
    files_in_data_path = set(os.path.join(data_path, fichier)
                             for fichier in os.listdir(data_path))

    database_state = check_database(db_path)

    if database_state == "empty" or database_state == "not-created":
        files_not_in_db = files_in_data_path
    else:
        # Connect to the chroma.sqlite3 database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Query the embedding_metadata table to get the source elements
        cursor.execute(
            "SELECT string_value FROM embedding_metadata WHERE key = 'source'")
        sources_in_db = set(row[0] for row in cursor.fetchall())

        # Close the database connection
        conn.close()

        # Find files that are not in the database
        files_not_in_db = files_in_data_path - sources_in_db

    return files_not_in_db


def load_specific_documents(files):
    """
    Load documents from a specific list of files.
    Args:
    file_list (list[str]): List of filenames to load.
    Returns:
    list[Document]: List of loaded Document objects.
    """
    documents = []
    for file_name in files:
        file_path = file_name
        document = PyPDFLoader(file_path)
        loaded = document.load()
        for doc in loaded:
            documents.append(doc)
    return documents


def update_data_store():
    """
    Update the vector database in Chroma with missing files.
    """
    missing_files = validate_files_in_db(
        DATA_PATH, os.path.join(CHROMA_PATH, "chroma.sqlite3"))
    if not missing_files:
        print("No missing files to process.")
        return
    print(len(missing_files), " missing documents in database")

    # Load missing documents
    missing_documents = load_specific_documents(missing_files)
    # Split documents into manageable chunks
    chunks = split_text(missing_documents)
    # Save the processed data to the data store, appending to the existing DB
    save_to_chroma(chunks)
    # print(chunks)


def main():
    update_data_store()


if __name__ == "__main__":
    main()
