# src/core/music_composition_export_formatter.py
import json
from typing import Dict, Any


class MusicCompositionExportFormatter:
    def __init__(self):
        self.musical_key_mappings = {
            'Major Keys': {
                'C': ['C', 'E', 'G'],
                'G': ['G', 'B', 'D'],
                'D': ['D', 'F#', 'A'],
                'A': ['A', 'C#', 'E'],
                'E': ['E', 'G#', 'B']
            },
            'Minor Keys': {
                'Am': ['A', 'C', 'E'],
                'Em': ['E', 'G', 'B'],
                'Dm': ['D', 'F', 'A']
            }
        }

    def generate_audio_export_metadata(self,
                                       lyrics: str,
                                       chord_progression: str,
                                       song_structure: str,
                                       musical_style: str,
                                       mood: str) -> Dict[str, Any]:
        """
        Prepare comprehensive metadata for audio generation

        Args:
            lyrics (str): Generated song lyrics
            chord_progression (str): Chord sequence
            song_structure (str): Song's structural breakdown
            musical_style (str): Genre or musical style
            mood (str): Emotional character of the song

        Returns:
            Dict containing structured musical metadata
        """
        # Analyze chord progression for key and harmonic characteristics
        primary_key = self._determine_primary_key(chord_progression)

        # Extract tempo and rhythm suggestions
        tempo_bpm = self._suggest_tempo_from_style_and_mood(musical_style, mood)

        # Prepare structured chord information
        structured_chords = self._process_chord_progression(chord_progression)

        # Generate audio generation metadata
        audio_export_metadata = {
            "music_metadata": {
                "title": "AI Generated Composition",
                "musical_style": musical_style,
                "mood": mood,
                "primary_key": primary_key,
                "tempo_bpm": tempo_bpm
            },
            "musical_structure": {
                "song_structure": self._parse_song_structure(song_structure),
                "chord_progression": structured_chords
            },
            "lyrical_content": {
                "full_lyrics": lyrics,
                "lyric_segments": self._segment_lyrics(lyrics)
            },
            "audio_generation_hints": {
                "recommended_instruments": self._suggest_instruments(musical_style),
                "emotional_intensity_map": self._create_emotion_intensity_map(mood)
            }
        }

        return audio_export_metadata

    def _determine_primary_key(self, chord_progression: str) -> str:
        """
        Determine the primary musical key based on chord progression

        Args:
            chord_progression (str): Chord sequence

        Returns:
            str: Detected or suggested primary key
        """
        # Simple key detection logic (can be expanded)
        for key_type, keys in self.musical_key_mappings.items():
            for key, chord_set in keys.items():
                if any(chord in chord_progression for chord in chord_set):
                    return key
        return 'C'  # Default fallback key

    def _suggest_tempo_from_style_and_mood(self, musical_style: str, mood: str) -> int:
        """
        Suggest tempo based on musical style and mood

        Args:
            musical_style (str): Genre of music
            mood (str): Emotional character

        Returns:
            int: Recommended tempo in beats per minute
        """
        tempo_mapping = {
            'Ballad': {'Sad': 60, 'Melancholic': 65, 'Romantic': 70},
            'Rock': {'Energetic': 120, 'Intense': 130, 'Angry': 135},
            'Pop': {'Happy': 100, 'Upbeat': 110, 'Neutral': 90},
            'Jazz': {'Contemplative': 80, 'Smooth': 75, 'Relaxed': 70},
            'Electronic': {'Intense': 128, 'Energetic': 135, 'Neutral': 110}
        }

        return tempo_mapping.get(
            musical_style,
            tempo_mapping.get('Pop', {})
        ).get(mood, 90)

    def _process_chord_progression(self, chord_progression: str) -> Dict[str, Any]:
        """
        Process and structure chord progression

        Args:
            chord_progression (str): Raw chord progression text

        Returns:
            Dict with structured chord information
        """
        # Extract unique chords
        unique_chords = list(set(chord_progression.split()))

        return {
            "raw_progression": chord_progression,
            "unique_chords": unique_chords,
            "chord_count": len(unique_chords),
            "progression_pattern": self._analyze_chord_pattern(unique_chords)
        }

    def _analyze_chord_pattern(self, chords: list) -> str:
        """
        Analyze chord progression pattern

        Args:
            chords (list): List of chords

        Returns:
            str: Pattern description
        """
        if len(chords) <= 3:
            return "Simple"
        elif len(chords) <= 6:
            return "Moderate Complexity"
        else:
            return "Complex"

    def _parse_song_structure(self, song_structure: str) -> Dict[str, Any]:
        """
        Parse and structure song sections

        Args:
            song_structure (str): Raw song structure text

        Returns:
            Dict with structured song sections
        """
        # Basic parsing of song structure
        sections = song_structure.split('\n')
        return {
            "sections": sections,
            "section_count": len(sections)
        }

    def _segment_lyrics(self, lyrics: str, segment_size: int = 4) -> list:
        """
        Segment lyrics into manageable chunks

        Args:
            lyrics (str): Full lyrics text
            segment_size (int): Number of lines per segment

        Returns:
            List of lyric segments
        """
        lines = lyrics.split('\n')
        return [
            '\n'.join(lines[i:i + segment_size])
            for i in range(0, len(lines), segment_size)
        ]

    def _suggest_instruments(self, musical_style: str) -> list:
        """
        Suggest instruments based on musical style

        Args:
            musical_style (str): Genre of music

        Returns:
            List of recommended instruments
        """
        instrument_suggestions = {
            'Rock': ['Electric Guitar', 'Drums', 'Bass Guitar', 'Keyboard'],
            'Jazz': ['Saxophone', 'Piano', 'Double Bass', 'Trumpet'],
            'Pop': ['Synthesizer', 'Electronic Drums', 'Bass', 'Acoustic Guitar'],
            'Electronic': ['Synthesizer', 'Drum Machine', 'Digital Keyboard'],
            'Classical': ['Violin', 'Piano', 'Cello', 'Flute']
        }

        return instrument_suggestions.get(musical_style, ['Piano', 'Guitar'])

    def _create_emotion_intensity_map(self, mood: str) -> Dict[str, float]:
        """
        Create an emotional intensity map for audio generation

        Args:
            mood (str): Emotional character of the song

        Returns:
            Dict with emotion intensity values
        """
        emotion_intensity = {
            'Sad': {'melancholy': 0.8, 'intensity': 0.6, 'energy': 0.3},
            'Happy': {'joy': 0.9, 'intensity': 0.7, 'energy': 0.8},
            'Angry': {'anger': 0.9, 'intensity': 0.9, 'energy': 0.9},
            'Calm': {'serenity': 0.7, 'intensity': 0.4, 'energy': 0.2},
            'Romantic': {'love': 0.8, 'intensity': 0.6, 'energy': 0.5}
        }

        return emotion_intensity.get(mood, {'neutral': 0.5})

    def export_to_json(self, metadata: Dict[str, Any]) -> str:
        """
        Export metadata to JSON format

        Args:
            metadata (Dict): Metadata dictionary

        Returns:
            str: JSON formatted string
        """
        return json.dumps(metadata, indent=2)

    #Key Features for Audio Generation

    # Comprehensive Metadata Generation
    #
    # Musical style and mood analysis
    # Chord progression structuring
    # Tempo suggestions
    # Primary key detection
    # Lyric segmentation
    #
    #
    # Audio Generation Hints
    #
    # Recommended instruments
    # Emotional intensity mapping
    # Structural breakdown
    #
    #
    # Flexible Export Options
    #
    # JSON export for easy integration
    # Structured metadata for various audio generation tools

    # Usage Example
    # # Assuming you have generated lyrics, chords, etc.
    # formatter = MusicCompositionExportFormatter()
    #
    # audio_metadata = formatter.generate_audio_export_metadata(
    #     lyrics="Your generated lyrics here",
    #     chord_progression="C Am F G",
    #     song_structure="Verse Chorus Verse Chorus Bridge Chorus",
    #     musical_style="Pop",
    #     mood="Happy"
    # )
    #
    # # Export to JSON for AudioGen or other audio generation tools
    # json_export = formatter.export_to_json(audio_metadata)
    # print(json_export)

    # Benefits
    # for Audio Generation
    #
    # Provides
    # rich, structured
    # metadata
    # Offers
    # contextual
    # hints
    # for audio synthesis
    #     Adaptable
    #     to
    #     different
    #     musical
    #     styles and moods
    # Easy
    # integration
    # with various audio generation platforms
    #
    # The
    # metadata
    # can
    # be
    # directly
    # used
    # by
    # tools
    # like
    # AudioGen, providing
    # comprehensive
    # information
    # about
    # the
    # musical
    # composition
    # 's structure, emotional character, and technical details.