import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing import Dict, List, Tuple

current_dir = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(current_dir, "../../chroma/")
DATA_PATH = os.path.join(current_dir, "../../ragData/")


class MusicStructureRAG:
    """Enhanced RAG system for music structure generation"""

    PROMPT_TEMPLATE = """
    Based on the following reference information about music structure: {context}

    Create a structured sequence for {music_style} music.
    Only provide the sections in order, like this example format:
    Intro → Verse → Chorus → Verse → etc.

    Important:
    - Keep it simple and clear
    - Only show the sequence
    - No additional explanations
    - No section lengths or bars
    """

    def __init__(self):
        """Initialize the RAG system"""
        self.embedding_function = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.llm = ChatOpenAI(
            temperature=0.3,
            base_url=os.getenv('MODEL_URL'),
            api_key="not-needed",
            streaming=True
        )

    def _retrieve_context(self, query: str) -> List[Tuple[str, float]]:
        """Retrieve relevant context"""
        db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=self.embedding_function
        )
        results = db.similarity_search_with_relevance_scores(query, k=3)

        # Filter results with relevance threshold
        relevant_results = [
            (doc.page_content, score)
            for doc, score in results
            if score >= 0.45
        ]

        return relevant_results
    

    def query_rag(self, music_style: str) -> str:
        """Main method to query the RAG system with improved error handling"""
        try:
            print(f"Processing genre: {music_style}")

            # Create query and get context
            augmented_query = f"{music_style} Music Typical Structure Intro Outro"
            results = self._retrieve_context(augmented_query)

            if not results:
                # If no results found, use rock structure as fallback
                fallback_structure = "Intro → Verse 1 → Chorus → Verse 2 → Chorus → Bridge → Chorus → Outro"
                print(f"No structure found for {music_style}, using default rock structure")
                return fallback_structure

            # Combine context from matching documents
            context_text = "\n\n---\n\n".join([doc for doc, _score in results])

            print("Generating structured list...")

            # Create and execute prompt
            prompt_template = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)
            prompt = prompt_template.format(
                context=context_text,
                music_style=music_style
            )

            # Generate and clean response
            response = self.llm.invoke(prompt).content
            cleaned_response = self._clean_response(response)

            if not cleaned_response or "→" not in cleaned_response:
                # Return default structure if response is invalid
                return "Intro → Verse 1 → Chorus → Verse 2 → Chorus → Bridge → Chorus → Outro"
            
            return cleaned_response

        except Exception as e:
            print(f"Error in RAG query: {str(e)}")
            # Return a safe fallback structure
            return "Intro → Verse 1 → Chorus → Verse 2 → Chorus → Bridge → Chorus → Outro"

    def _clean_response(self, response: str) -> str:
        """Clean and standardize the response"""
        # Take first line if multiple lines
        if '\n' in response:
            response = response.split('\n')[0]

        # Clean up the response
        response = response.strip()
        response = response.replace(' - ', ' → ')
        response = response.replace('--', '→')
        response = response.replace('-', '→')

        return response


def main():
    """Main function for testing"""
    rag = MusicStructureRAG()
    rag.query_rag("Rhythm and Blues")


if __name__ == "__main__":
    main()