import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

CHROMA_PATH = "../../chroma/"
DATA_PATH = "../../ragData/"
# TODO test + modif cette partie semble problématique
PROMPT_TEMPLATE = """
Give answer based only on the following context: {context}
What is the {music_style} Music Typical Structure?
I want to know the number of verse, chorus, and bridge in a typical {music_style} music.
Do a list that looks like this:
Intro - Verse - Chorus - Verse - etc...
I just want the list.
"""

llm = ChatOpenAI(
    temperature=0.3,  # Slightly higher for creative variation
    base_url=os.getenv('MODEL_URL'),
    api_key="not-needed",
    streaming=True
)
embedding_function = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2")


def query_rag(llm, query_text):
    """
    Query a Retrieval-Augmented Generation (RAG) system using Chroma database and OpenAI.
    Args:
      - query_text (str): The text to query the RAG system with.
    Returns:
      - formatted_response (str): Formatted response including the generated text and sources.
      - response_text (str): The generated response text.
    """

    augmented_query = query_text + " Music Typical Structure Intro Outro"
    print(query_text)

    # Prepare the database
    db = Chroma(persist_directory=CHROMA_PATH,
                embedding_function=embedding_function)

    # Retrieving the context from the DB using similarity search
    results = db.similarity_search_with_relevance_scores(augmented_query, k=3)
    print("Generating structured list...")

    # Check if there are any matching results or if the relevance score is too low
    if len(results) == 0 or results[0][1] < 0.55:
        print("Unable to find matching results.")

    # Combine context from matching documents
    context_text = "\n\n - -\n\n".join(
        [doc.page_content for doc, _score in results])

    # Create prompt template using context and query text
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(
        context=context_text, music_style=query_text)

    # Generate response text based on the prompt
    response_text = llm.invoke(prompt).content

    # Get sources of the matching documents
    # sources = [doc.metadata.get("source", None) for doc, _score in results]

    # Format and return response including generated text and sources
    # formatted_response = f"Response: {response_text}\nSources: {sources}"
    # return formatted_response, response_text
    print(response_text)
    return response_text


def main():
    query_rag(llm, "Rhythm and Blues")


if __name__ == "__main__":
    main()
