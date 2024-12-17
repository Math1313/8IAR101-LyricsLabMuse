# src/core/music_composition_experts.py
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from dotenv import load_dotenv


class MusicCompositionExperts:
    load_dotenv()

    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.3,
            base_url=os.getenv('MODEL_URL'),
            api_key="not-needed",
            streaming=True
        )

    MUSICAL_PARAMETERS_TEMPLATE = """
    You are a music producer creating a {musical_style} song with a {mood} mood.

    First, generate a creative title that reflects the style, mood, and theme provided.
    The title should be catchy and memorable.

    Then, define the technical parameters in this exact structured format:

    [Title]
    <Generate a single line with the song title>

    [Musical Parameters]
    Tempo: <specific BPM value between 60-180>
    Key: <specific key, e.g., "C major" or "A minor">
    Time Signature: <specific time signature, e.g., "4/4" or "3/4">
    Genre-Specific Feel: <specific feel, e.g., "Shuffle", "Straight", "Swing">
    Dynamic Level: <specific level, e.g., "Medium-loud", "Soft", "Building">

    [Production Elements]
    Main Instruments:
    - <instrument 1>
    - <instrument 2>
    - <instrument 3>
    (List 3-4 key instruments typical for {musical_style})

    Effects:
    - <effect 1>
    - <effect 2>
    (List 2-3 key effects appropriate for {musical_style})

    [Mix Notes]
    Mix Focus: <specific mix focus, e.g., "Bass-heavy", "Vocal-forward", "Balanced">
    Stereo Space: <specific stereo approach, e.g., "Wide", "Centered", "Dynamic">
    EQ Focus: <specific frequency focus, e.g., "Rich low-end", "Bright highs", "Mid-focused">

    Provide ONLY these parameters exactly as requested, with no additional explanations or variations.
    """

    LYRICS_EXPERT_TEMPLATE = """
        You are a professional lyricist. Create structured lyrics based on:
        Musical Style: {musical_style}
        Structure: {structure}
        Song Theme: {song_theme}
        Mood: {mood}
        Language: {language}
        Musical Parameters: {musical_params}

        Create a song with EXACTLY this structure:
        {structure}

        Format with section labels and exact line counts in brackets:
        [Verse 1] [8 lines]
        (write verse)

        [Chorus] [4-6 lines]
        (write chorus)

        [Verse 2] [8 lines]
        (write verse)

        [Bridge] (optional) [4 lines max]
        (write bridge if appropriate)

        [Final Chorus]
        (same as first chorus)

        Show ONLY the lyrics for each section. Do not include any other content.
        """

    CHORD_PROGRESSION_TEMPLATE = """
        You are a professional music composer. Create chord progressions matching:
        Musical Parameters: {musical_params}
        Key: {key}
        Style: {musical_style}
        Mood: {mood}

        Provide chord progressions in this format:

        [Verse] [{time_signature}]
        Chord sequence: (4-8 chords, using the specified key)
        Duration: (in bars)
        Rhythm: (straight, syncopated, etc.)

        [Chorus] [{time_signature}]
        Chord sequence: (4-8 chords)
        Duration: (in bars)
        Rhythm: (pattern description)

        [Bridge] [{time_signature}]
        Chord sequence: (4 chords max)
        Duration: (in bars)
        Rhythm: (pattern description)

        Use proper chord notation for {key}. Include any specific rhythmic accents.
        """

    MELODY_COMPOSITION_TEMPLATE = """
        You are a melody composer. Create a melody matching:
        Musical Parameters: {musical_params}
        Key: {key}
        Tempo: {tempo}
        Style: {musical_style}

        Provide melody details for each section:

        [Verse Melody]
        Scale: (based on {key})
        Contour: (melodic movement)
        Rhythm: (based on {tempo} BPM)
        Range: (specific note range)
        Syncopation: (yes/no, description)

        [Chorus Melody]
        Scale: (based on {key})
        Contour: (melodic movement)
        Rhythm: (based on {tempo} BPM)
        Range: (specific note range)
        Peak Notes: (climax points)

        [Bridge Melody]
        Scale: (based on {key})
        Contour: (melodic movement)
        Rhythm: (based on {tempo} BPM)
        Range: (specific note range)
        """

    def generate_lyrics(self, musical_style, structure, song_theme, mood, language):
        """Generate only the lyrics section of the song."""
        # First get musical parameters
        params_prompt = ChatPromptTemplate.from_template(
            self.MUSICAL_PARAMETERS_TEMPLATE)
        params_chain = params_prompt | self.llm | StrOutputParser()

        musical_params = ""
        for chunk in params_chain.stream({
            "musical_style": musical_style,
            "mood": mood
        }):
            musical_params += chunk

        # Then generate lyrics with the parameters
        lyrics_prompt = ChatPromptTemplate.from_template(
            self.LYRICS_EXPERT_TEMPLATE)
        lyrics_chain = lyrics_prompt | self.llm | StrOutputParser()

        yield "## LYRICS\n\n"
        for chunk in lyrics_chain.stream({
            "musical_style": musical_style,
            "structure": structure,
            "song_theme": song_theme,
            "mood": mood,
            "language": language,
            "musical_params": musical_params
        }):
            yield chunk

    def generate_chord_progression(self, musical_style, song_theme, mood, language):
        """Generate only the chord progression section."""
        # First get musical parameters
        params_prompt = ChatPromptTemplate.from_template(
            self.MUSICAL_PARAMETERS_TEMPLATE)
        params_chain = params_prompt | self.llm | StrOutputParser()

        musical_params = ""
        for chunk in params_chain.stream({
            "musical_style": musical_style,
            "mood": mood
        }):
            musical_params += chunk

        # Extract key and time signature
        key = "C major"  # Default
        time_signature = "4/4"  # Default
        for line in musical_params.split('\n'):
            if "Key:" in line:
                key = line.split("Key:")[1].strip()
            elif "Time Signature:" in line:
                time_signature = line.split("Time Signature:")[1].strip()

        chord_prompt = ChatPromptTemplate.from_template(
            self.CHORD_PROGRESSION_TEMPLATE)
        chord_chain = chord_prompt | self.llm | StrOutputParser()

        yield "## CHORD PROGRESSION\n\n"
        for chunk in chord_chain.stream({
            "musical_style": musical_style,
            "mood": mood,
            "musical_params": musical_params,
            "key": key,
            "time_signature": time_signature
        }):
            yield chunk

    def generate_melody(self, musical_style, song_theme, mood, language):
        """Generate only the melody section."""
        # First get musical parameters
        params_prompt = ChatPromptTemplate.from_template(
            self.MUSICAL_PARAMETERS_TEMPLATE)
        params_chain = params_prompt | self.llm | StrOutputParser()

        musical_params = ""
        for chunk in params_chain.stream({
            "musical_style": musical_style,
            "mood": mood
        }):
            musical_params += chunk

        # Extract key and tempo
        key = "C major"  # Default
        tempo = "120 BPM"  # Default
        for line in musical_params.split('\n'):
            if "Key:" in line:
                key = line.split("Key:")[1].strip()
            elif "Tempo:" in line:
                tempo = line.split("Tempo:")[1].strip()

        melody_prompt = ChatPromptTemplate.from_template(
            self.MELODY_COMPOSITION_TEMPLATE)
        melody_chain = melody_prompt | self.llm | StrOutputParser()

        yield "## MELODY\n\n"
        for chunk in melody_chain.stream({
            "musical_style": musical_style,
            "mood": mood,
            "musical_params": musical_params,
            "key": key,
            "tempo": tempo
        }):
            yield chunk

    def generate_song_structure(self, musical_style, structure, song_theme, mood, language):
        """Generate the complete song structure with all musical parameters."""
        # We'll use the full song composition and extract the combined view
        composition_generator = self.generate_song_composition(
            musical_style, structure, song_theme, mood, language
        )

        in_complete_structure = False
        for chunk in composition_generator:
            if "## 5. COMPLETE SONG STRUCTURE" in chunk:
                in_complete_structure = True
                yield "## SONG STRUCTURE\n\n"
            elif in_complete_structure:
                yield chunk

    def _format_complete_structure(self, lyrics: str, chord_progression: str, melody: str) -> str:
        """Format the complete song structure with proper section mapping"""

        # Parse sections
        lyrics_sections = self._parse_lyrics_sections(lyrics)
        chord_sections = self._parse_chord_sections(chord_progression)
        melody_sections = self._parse_melody_sections(melody)

        # Build combined structure
        structure = []

        # Add technical parameters
        structure.append("[Song Technical Parameters]")
        for param in ["Key", "Tempo", "Time Signature"]:
            if param.lower() in self.current_parameters:
                structure.append(f"{param}: {self.current_parameters[param.lower()]}")
        structure.append("")

        # Combine sections
        section_order = ["Verse 1", "Chorus", "Verse 2", "Bridge", "Final Chorus"]
        for section in section_order:
            structure.append(f"[{section}]")

            # Add lyrics
            structure.append("Lyrics:")
            if section in lyrics_sections:
                structure.append(lyrics_sections[section])
            else:
                structure.append("(No lyrics for this section)")

            # Add chords
            structure.append("Chords:")
            base_section = section.split()[0]  # "Verse 1" -> "Verse"
            if base_section in chord_sections:
                structure.append(chord_sections[base_section])
            else:
                structure.append("(No chord progression for this section)")

            # Add melody
            structure.append("Melody:")
            if base_section in melody_sections:
                structure.append(melody_sections[base_section])
            else:
                structure.append("(No melody for this section)")

            structure.append("")

        return "\n".join(structure)

    def generate_song_composition(self, musical_style, structure, song_theme, mood, language):
        """Generate a complete song composition with musical parameters."""
        # Create prompt templates
        params_prompt = ChatPromptTemplate.from_template(
            self.MUSICAL_PARAMETERS_TEMPLATE)
        lyrics_prompt = ChatPromptTemplate.from_template(
            self.LYRICS_EXPERT_TEMPLATE)
        chord_prompt = ChatPromptTemplate.from_template(
            self.CHORD_PROGRESSION_TEMPLATE)
        melody_prompt = ChatPromptTemplate.from_template(
            self.MELODY_COMPOSITION_TEMPLATE)

        # Create chains
        params_chain = params_prompt | self.llm | StrOutputParser()
        lyrics_chain = lyrics_prompt | self.llm | StrOutputParser()
        chord_chain = chord_prompt | self.llm | StrOutputParser()
        melody_chain = melody_prompt | self.llm | StrOutputParser()

        # Generate header
        yield f"""# Song Composition
            Musical Style: {musical_style}
            Structure: {structure}
            Theme: {song_theme}
            Mood: {mood}
            Language: {language}
            """
        # 1. Generate Musical Parameters
        yield "## 1. MUSICAL PARAMETERS\n\n"
        musical_params = ""
        for chunk in params_chain.stream({
            "musical_style": musical_style,
            "structure": structure,
            "mood": mood
        }):
            musical_params += chunk
            yield chunk
        yield "\n\n"

        # Extract key parameters for use in other sections
        key = "C major"  # Default values
        tempo = "120 BPM"
        time_signature = "4/4"

        # Parse the musical_params to extract actual values
        for line in musical_params.split('\n'):
            if "Key:" in line:
                key = line.split("Key:")[1].strip()
            elif "Tempo:" in line:
                tempo = line.split("Tempo:")[1].strip()
            elif "Time Signature:" in line:
                time_signature = line.split("Time Signature:")[1].strip()

        # 2. Generate Lyrics with musical parameters
        yield "## 2. LYRICS\n\n"
        lyrics_text = ""
        for chunk in lyrics_chain.stream({
            "musical_style": musical_style,
            "structure": structure,
            "song_theme": song_theme,
            "mood": mood,
            "language": language,
            "musical_params": musical_params
        }):
            lyrics_text += chunk
            yield chunk
        yield "\n\n"

        # 3. Generate Chords with musical parameters
        yield "## 3. CHORD PROGRESSION\n\n"
        chord_text = ""
        for chunk in chord_chain.stream({
            "musical_style": musical_style,
            "mood": mood,
            "musical_params": musical_params,
            "key": key,
            "time_signature": time_signature
        }):
            chord_text += chunk
            yield chunk
        yield "\n\n"

        # 4. Generate Melody with musical parameters
        yield "## 4. MELODY\n\n"
        melody_text = ""
        for chunk in melody_chain.stream({
            "musical_style": musical_style,
            "mood": mood,
            "musical_params": musical_params,
            "key": key,
            "tempo": tempo
        }):
            melody_text += chunk
            yield chunk
        yield "\n\n"

        # 5. Generate Combined View
        yield "## 5. COMPLETE SONG STRUCTURE\n\n"
        yield f"""[Song Technical Parameters]
        Key: {key}
        Tempo: {tempo}
        Time Signature: {time_signature}

        """
        # Store the generated content
        lyrics_sections = self._split_into_sections(lyrics_text)
        chord_sections = self._split_into_sections(chord_text)
        melody_sections = self._split_into_sections(melody_text)

        for section in ["Verse 1", "Chorus", "Verse 2", "Bridge", "Final Chorus"]:
            yield f"[{section}]\n"

            # Extract lyrics
            yield "Lyrics:\n"
            if section in lyrics_sections:
                yield lyrics_sections[section] + "\n"
            else:
                yield "(No lyrics for this section)\n"

            # Extract chords
            yield "Chords:\n"
            base_section = section.split()[0]  # "Verse 1" -> "Verse"
            if base_section in chord_sections:
                yield chord_sections[base_section] + "\n"
            elif section in chord_sections:  # Try exact match
                yield chord_sections[section] + "\n"
            else:
                yield "(No chord progression for this section)\n"

            # Extract melody
            yield "Melody:\n"
            if base_section in melody_sections:
                yield melody_sections[base_section] + "\n"
            elif f"{base_section} Melody" in melody_sections:
                yield melody_sections[f"{base_section} Melody"] + "\n"
            else:
                yield "(No melody for this section)\n"

            yield "\n"

    def _extract_section(self, text: str, section_name: str) -> str:
        """
        Extract a specific section from the text, handling various section formats.
        Args:
            text (str): The full text content
            section_name (str): Name of the section to extract (e.g., "Verse 1", "Chorus")
        Returns:
            str: Extracted section content
        """
        lines = text.split('\n')
        section_content = []
        in_section = False

        # Handle both exact matches and partial matches (e.g., "Verse" in "Verse 1")
        section_identifiers = [
            f"[{section_name}]",
            f"[{section_name} Melody]",
            f"[{section_name}] [",  # Match any time signature format
        ]

        for i, line in enumerate(lines):
            # Check if we've found the section start
            if any(identifier in line for identifier in section_identifiers):
                in_section = True
                continue

            # Check if we've reached the next section
            if in_section and line.strip().startswith('['):
                break

            # Collect content if we're in the right section
            if in_section and line.strip():
                # Remove labels like "Chord sequence:", "Scale:", etc.
                content = line.strip()
                for label in ["Chord sequence:", "Duration:", "Rhythm:", "Scale:", "Contour:", "Range:", "Syncopation:",
                              "Peak Notes:"]:
                    if content.startswith(label):
                        content = content.replace(label, "").strip()
                section_content.append(content)

        return "\n".join(section_content) if section_content else "(Not found in this section)"

    def _split_into_sections(self, text: str) -> dict:
        """
        Split the full text into a dictionary of sections with better section matching.
        Args:
            text (str): The full text content
        Returns:
            dict: Dictionary with section names as keys and content as values
        """
        sections = {}
        current_section = None
        current_content = []
        in_section = False

        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check for section headers
            if line.startswith('[') and ']' in line:
                # Save previous section if it exists
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)

                # Extract new section name, handling time signatures
                section_parts = line[1:].split(']')[0].split('[')
                current_section = section_parts[0].strip()
                if "Melody" in current_section:
                    current_section = current_section.replace(" Melody", "")
                current_content = []
                in_section = True
                i += 1
                continue

            # If we're in a section, collect content
            if in_section and line:
                # Skip labels and collect the actual content
                if any(label in line for label in
                       ["Chord sequence:", "Duration:", "Rhythm:", "Scale:", "Contour:", "Range:", "Syncopation:",
                        "Peak Notes:"]):
                    content = lines[i + 1].strip() if i + \
                        1 < len(lines) else ""
                    if content and not content.startswith('['):
                        current_content.append(content)
                    i += 2
                    continue
                elif not line.startswith('['):
                    current_content.append(line)

            i += 1

        # Save the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections