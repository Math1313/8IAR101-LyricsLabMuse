import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser


class LLMIntegration2:
    def __init__(self):
        # Initialize the base LLM with streaming capabilities
        self.llm = ChatOpenAI(
            temperature=0.2,  # Slightly increased for creative variation
            base_url="http://localhost:1234/v1/",
            api_key="not-needed",
            streaming=True
        )

    # Expert Prompt Templates
    SONG_CONCEPT_TEMPLATE = """
    Song Concept Expert:
    Analyze the musical project brief and provide a comprehensive conceptual breakdown:

    Musical Style: {musical_style}
    Song Theme: {song_theme}
    Mood: {mood}
    Language: {language}

    Deliverables:
    1. Emotional Landscape Analysis
    2. Narrative Potential
    3. Genre-Specific Characteristics
    4. Cultural Context Insights
    5. Potential Lyrical Themes
    6. Emotional Tone Recommendations
    """

    SONG_STRUCTURE_TEMPLATE = """
    Song Structure Architect:
    Design a comprehensive song structure based on the concept analysis:

    Concept Analysis: {concept_analysis}
    Musical Style: {musical_style}
    Mood: {mood}

    Develop:
    1. Detailed Song Structure Breakdown
    2. Recommended Section Transitions
    3. Emotional Arc of the Composition
    4. Potential Instrumental Arrangements
    5. Rhythmic and Tonal Suggestions
    """

    LYRICS_COMPOSITION_TEMPLATE = """
    Lyric Composition Expert:
    Generate lyrics that embody the song's conceptual and structural design:

    Concept Analysis: {concept_analysis}
    Song Structure: {song_structure}
    Musical Style: {musical_style}
    Mood: {mood}
    Language: {language}

    Lyric Creation Guidelines:
    1. Maintain linguistic authenticity
    2. Align with emotional landscape
    3. Reflect narrative potential
    4. Adhere to genre characteristics
    5. Create cohesive storytelling
    """

    CHORD_PROGRESSION_TEMPLATE = """
    Chord Progression Specialist:
    Design a chord progression that complements the song's emotional and structural design:

    Concept Analysis: {concept_analysis}
    Song Structure: {song_structure}
    Musical Style: {musical_style}
    Mood: {mood}

    Chord Progression Requirements:
    1. Harmonic support for emotional arc
    2. Genre-appropriate chord choices
    3. Dynamic tonal variations
    4. Rhythmic compatibility
    5. Melodic enhancement potential
    """

    SONG_REVIEW_TEMPLATE = """
    Composition Review Expert:
    Comprehensively review the generated musical composition:

    Lyrics: {lyrics}
    Song Structure: {song_structure}
    Chord Progression: {chord_progression}
    Musical Style: {musical_style}
    Mood: {mood}

    Review Criteria:
    1. Emotional Coherence
    2. Thematic Consistency
    3. Linguistic Quality
    4. Musical Authenticity
    5. Potential Performance Interpretation
    """

    def generate_song_composition(self, musical_style, song_theme, mood, language):
        """
        Orchestrate a comprehensive song composition process
        using multiple expert perspectives.

        :return: Streaming generator for complete song composition
        """
        # Create prompt templates for each stage
        concept_prompt = ChatPromptTemplate.from_template(self.SONG_CONCEPT_TEMPLATE)
        structure_prompt = ChatPromptTemplate.from_template(self.SONG_STRUCTURE_TEMPLATE)
        lyrics_prompt = ChatPromptTemplate.from_template(self.LYRICS_COMPOSITION_TEMPLATE)
        chord_prompt = ChatPromptTemplate.from_template(self.CHORD_PROGRESSION_TEMPLATE)
        review_prompt = ChatPromptTemplate.from_template(self.SONG_REVIEW_TEMPLATE)

        # Create chains for each stage
        concept_chain = concept_prompt | self.llm | StrOutputParser()
        structure_chain = structure_prompt | self.llm | StrOutputParser()
        lyrics_chain = lyrics_prompt | self.llm | StrOutputParser()
        chord_chain = chord_prompt | self.llm | StrOutputParser()
        review_chain = review_prompt | self.llm | StrOutputParser()

        # Generate composition stages
        concept_analysis = concept_chain.stream({
            "musical_style": musical_style,
            "song_theme": song_theme,
            "mood": mood,
            "language": language
        })

        # Convert streaming generator to string for next stages
        concept_str = "".join(list(concept_analysis))

        song_structure = structure_chain.stream({
            "concept_analysis": concept_str,
            "musical_style": musical_style,
            "mood": mood
        })

        # Convert streaming generator to string for next stages
        structure_str = "".join(list(song_structure))

        lyrics = lyrics_chain.stream({
            "concept_analysis": concept_str,
            "song_structure": structure_str,
            "musical_style": musical_style,
            "mood": mood,
            "language": language
        })

        lyrics_str = "".join(list(lyrics))

        chord_progression = chord_chain.stream({
            "concept_analysis": concept_str,
            "song_structure": structure_str,
            "musical_style": musical_style,
            "mood": mood
        })

        chord_str = "".join(list(chord_progression))

        # Final review of the composition
        composition_review = review_chain.stream({
            "lyrics": lyrics_str,
            "song_structure": structure_str,
            "chord_progression": chord_str,
            "musical_style": musical_style,
            "mood": mood
        })

        # Stream the final composition details
        yield "Concept Analysis:\n"
        yield from concept_analysis
        yield "\n\nSong Structure:\n"
        yield from song_structure
        yield "\n\nLyrics:\n"
        yield from lyrics
        yield "\n\nChord Progression:\n"
        yield from chord_progression
        yield "\n\nComposition Review:\n"
        yield from composition_review

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