import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

class MusicCompositionExperts:
    def __init__(self):
        # Initialize the base LLM with streaming capabilities
        self.llm = ChatOpenAI(
            temperature=0.3,  # Slightly higher for creative variation
            base_url="http://localhost:1234/v1/",
            api_key="not-needed",
            streaming=True
        )

    # Expert Prompt Templates
    LYRICS_EXPERT_TEMPLATE = """
    Lyrics Composition Expert:
    Craft compelling lyrics based on the following parameters:

    Musical Style: {musical_style}
    Song Theme: {song_theme}
    Mood: {mood}
    Language: {language}

    Lyric Composition Guidelines:
    1. Capture the emotional essence of the theme
    2. Maintain linguistic authenticity
    3. Create a cohesive narrative
    4. Align with the specified musical style
    5. Reflect the intended mood

    Deliver:
    - Verse lyrics
    - Chorus lyrics
    - Bridge (if applicable)
    - Thematic coherence explanation
    """

    CHORD_PROGRESSION_TEMPLATE = """
    Chord Progression Architect:
    Design a chord progression that complements the lyrical and emotional landscape:

    Derived from Lyrics: {lyrics_context}
    Musical Style: {musical_style}
    Mood: {mood}

    Chord Progression Requirements:
    1. Harmonic support for emotional arc
    2. Genre-specific chord choices
    3. Dynamic tonal variations
    4. Rhythmic compatibility
    5. Melodic potential enhancement

    Deliver:
    - Verse chord progression
    - Chorus chord progression
    - Bridge chord progression
    - Harmonic reasoning
    """

    MELODY_COMPOSITION_TEMPLATE = """
    Melody Composition Specialist:
    Create a melodic structure that interweaves with the lyrics and chord progression:

    Lyrics: {lyrics}
    Chord Progression: {chord_progression}
    Musical Style: {musical_style}
    Mood: {mood}

    Melody Design Principles:
    1. Complement lyrical phrasing
    2. Align with chord harmonic structure
    3. Reflect musical style nuances
    4. Emphasize emotional peaks
    5. Ensure singability and memorability

    Deliver:
    - Verse melody description
    - Chorus melody description
    - Bridge melody concept
    - Melodic development notes
    """

    def generate_song_composition(self, musical_style, song_theme, mood, language):
        """
        Backward-compatible method that mimics the original
        comprehensive song composition process.

        :return: Streaming generator for complete song composition
        """
        # Create prompt templates for each expert
        lyrics_prompt = ChatPromptTemplate.from_template(self.LYRICS_EXPERT_TEMPLATE)
        chord_prompt = ChatPromptTemplate.from_template(self.CHORD_PROGRESSION_TEMPLATE)
        melody_prompt = ChatPromptTemplate.from_template(self.MELODY_COMPOSITION_TEMPLATE)

        # Create chains for each expert
        lyrics_chain = lyrics_prompt | self.llm | StrOutputParser()
        chord_chain = chord_prompt | self.llm | StrOutputParser()
        melody_chain = melody_prompt | self.llm | StrOutputParser()

        # Generate lyrics first
        lyrics_stream = lyrics_chain.stream({
            "musical_style": musical_style,
            "song_theme": song_theme,
            "mood": mood,
            "language": language
        })
        lyrics_text = "".join(list(lyrics_stream))

        # Generate chord progression with lyrics context
        chord_stream = chord_chain.stream({
            "lyrics_context": lyrics_text,
            "musical_style": musical_style,
            "mood": mood
        })
        chord_text = "".join(list(chord_stream))

        # Generate melody with lyrics and chord progression context
        melody_stream = melody_chain.stream({
            "lyrics": lyrics_text,
            "chord_progression": chord_text,
            "musical_style": musical_style,
            "mood": mood
        })
        melody_text = "".join(list(melody_stream))

        # Stream the composition details
        yield "🎵 Concept Analysis:\n"
        yield f"Musical Style: {musical_style}\n"
        yield f"Song Theme: {song_theme}\n"
        yield f"Mood: {mood}\n"
        yield f"Language: {language}\n\n"

        yield "--- Lyrics ---\n"
        yield from lyrics_stream
        yield "\n\n--- Song Structure ---\n"
        yield chord_text
        yield "\n\n--- Chord Progression ---\n"
        yield from chord_stream
        yield "\n\n--- Melodic Structure ---\n"
        yield from melody_stream

    # Maintain existing methods for compatibility
    def generate_lyrics(self, musical_style, song_theme, mood, language):
        song_composition = self.generate_song_composition(musical_style, song_theme, mood, language)
        return (chunk for chunk in song_composition if "Lyrics:" in chunk)

    def generate_song_structure(self, musical_style, song_theme, mood, language):
        song_composition = self.generate_song_composition(musical_style, song_theme, mood, language)
        return (chunk for chunk in song_composition if "Song Structure:" in chunk)

    def generate_chord_progression(self, musical_style, song_theme, mood, language):
        song_composition = self.generate_song_composition(musical_style, song_theme, mood, language)
        return (chunk for chunk in song_composition if "Chord Progression:" in chunk)

    def generate_melody(self, musical_style, song_theme, mood, language):
        song_composition = self.generate_song_composition(musical_style, song_theme, mood, language)
        return (chunk for chunk in song_composition if "Melodic Structure:" in chunk)