import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

class LLMIntegration:
    def __init__(self):
        # Assurez-vous de définir votre clé API OpenAI comme variable d'environnement
        # self.api_key = os.getenv('OPENAI_API_KEY')
        # if not self.api_key:
        #     raise ValueError("Veuillez définir la variable d'environnement OPENAI_API_KEY")
        
        self.llm = ChatOpenAI(
            temperature=0.001, 
            base_url="http://localhost:1234/v1/", #TODO: Modifier l'adresse IP si on change de place
            api_key="not-needed",
            streaming=True  # Activer le streaming pour voir les mots un à un
        )
    
    def generate_description(self, nom, prenom):
        """Génère une description basée sur le nom et prénom"""
        prompt = ChatPromptTemplate.from_template(
            "Crée une courte description imaginative et amusante pour {prenom} {nom}"
        )
        
        chain = prompt | self.llm | StrOutputParser()
        # Utiliser stream au lieu de invoke pour activer le streaming
        return chain.stream({"nom": nom, "prenom": prenom})
    
    def generate_lyrics(self, musicalStyle, songTheme, mood, language):
        prompt = ChatPromptTemplate.from_template(
            """
                You are a talented songwriter capable of crafting lyrics and melodies across genres.
                Your songs adapt to the {musicalStyle}, embracing its unique characteristics and rhythms.
                Each composition captures the essence of the {songTheme}, weaving it seamlessly into the words and music.
                The {mood} sets the emotional tone, ensuring the song resonates deeply with its audience.
                All lyrics are written in {language}, maintaining linguistic and cultural authenticity while staying true to the song's core identity.
            """
        )

        chain = prompt | self.llm | StrOutputParser()
        # Utiliser stream au lieu de invoke pour activer le streaming
        return chain.stream({"musicalStyle": musicalStyle, "songTheme": songTheme, "mood": mood, "language": language})

    def generate_song_structure(self, musicalStyle, songTheme, mood, language):
        prompt = ChatPromptTemplate.from_template(
            """
                You are a skilled music composer capable of creating song structures across various genres.
                Your structures adapt to the {musicalStyle}, embracing its unique characteristics and rhythms.
                Each composition captures the essence of the {songTheme}, weaving it seamlessly into the structure.
                The {mood} sets the emotional tone, ensuring the song resonates deeply with its audience.
                The structure should be described in {language}, maintaining linguistic and cultural authenticity while staying true to the song's core identity.
                Provide the structure as a list of section names.
            """
        )

        chain = prompt | self.llm | StrOutputParser()
        # Utiliser stream au lieu de invoke pour activer le streaming
        return chain.stream({"musicalStyle": musicalStyle, "songTheme": songTheme, "mood": mood, "language": language})

    def generate_chord_progression(self, musicalStyle, songTheme, mood, language):
        prompt = ChatPromptTemplate.from_template(
            """
                You are a skilled musician capable of creating chord progressions across various genres.
                Your progressions adapt to the {musicalStyle}, embracing its unique characteristics and rhythms.
                Each composition captures the essence of the {songTheme}, weaving it seamlessly into the chords.
                The {mood} sets the emotional tone, ensuring the song resonates deeply with its audience.
                The chord progression should be described in {language}, maintaining linguistic and cultural authenticity while staying true to the song's core identity.
                Provide the chord progression as a list of chords.
            """
        )

        chain = prompt | self.llm | StrOutputParser()
        # Utiliser stream au lieu de invoke pour activer le streaming
        return chain.stream({"musicalStyle": musicalStyle, "songTheme": songTheme, "mood": mood, "language": language})