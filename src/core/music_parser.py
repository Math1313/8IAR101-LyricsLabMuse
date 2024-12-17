# src/core/music_parser.py

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SongSection:
    """Represents a section of a song (verse, chorus, etc.)"""
    name: str
    lyrics: Optional[str] = None
    chords: Optional[str] = None
    melody: Optional[str] = None


@dataclass
class MusicParameters:
    """Musical parameters and technical specifications"""
    title: Optional[str] = None
    tempo: str = "120"
    key: str = "C major"
    time_signature: str = "4/4"
    genre_specific_feel: str = "standard"
    dynamic_level: Optional[str] = None


@dataclass
class ProductionElements:
    """Production and mixing specifications"""
    instruments: List[str] = None
    effects: List[str] = None
    mix_focus: Optional[str] = None
    stereo_space: Optional[str] = None
    eq_focus: Optional[str] = None

    def __post_init__(self):
        if self.instruments is None:
            self.instruments = []
        if self.effects is None:
            self.effects = []


class MusicParser:
    """Parser for music composition data"""

    @staticmethod
    def parse_composition(composition_text: str) -> Dict[str, Any]:
        """
        Parse the complete composition text into structured format.

        Args:
            composition_text (str): Raw composition text to parse

        Returns:
            Dict[str, Any]: Structured composition data
        """
        if not composition_text.strip():
            return {
                "metadata": {"generated_at": datetime.now().isoformat()},
                "musical_parameters": MusicParameters(),
                "production": ProductionElements(),
                "sections": {}
            }

        # Split into major sections
        sections = MusicParser._split_major_sections(composition_text)

        # Parse each component
        metadata = MusicParser._extract_metadata(composition_text)
        parameters = MusicParser._parse_musical_parameters(sections.get("MUSICAL PARAMETERS", ""))
        production = MusicParser._parse_production_elements(sections.get("MUSICAL PARAMETERS", ""))
        song_sections = MusicParser._parse_song_sections(sections)

        return {
            "metadata": metadata,
            "musical_parameters": parameters,
            "production": production,
            "sections": song_sections
        }

    @staticmethod
    def _split_major_sections(text: str) -> Dict[str, str]:
        """Split text into major sections (PARAMETERS, LYRICS, etc.)"""
        sections = {}
        current_section = None
        current_content = []

        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('##'):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.replace('#', '').strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        # Handle last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    @staticmethod
    def _parse_musical_parameters(params_text: str) -> MusicParameters:
        """Parse musical parameters section"""
        params = MusicParameters()
        current_section = None

        for line in params_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            if '[Title]' in line:
                current_section = 'title'
                continue
            elif '[Musical Parameters]' in line:
                current_section = 'parameters'
                continue

            if current_section == 'title':
                if line and not line.startswith('['):
                    params.title = line
            elif current_section == 'parameters' and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if 'tempo' in key:
                    params.tempo = value.split()[0]  # Extract BPM number
                elif 'key' in key:
                    params.key = value
                elif 'time signature' in key:
                    params.time_signature = value
                elif 'genre-specific feel' in key:
                    params.genre_specific_feel = value
                elif 'dynamic level' in key:
                    params.dynamic_level = value

        return params

    @staticmethod
    def _parse_production_elements(params_text: str) -> ProductionElements:
        """Parse production elements section"""
        elements = ProductionElements()
        current_section = None

        for line in params_text.split('\n'):
            line = line.strip()

            if '[Production Elements]' in line:
                current_section = 'instruments'
            elif '[Mix Notes]' in line:
                current_section = 'mix'
            elif 'Effects:' in line:
                current_section = 'effects'
            elif line.startswith('-'):
                item = line.replace('-', '').strip()
                if current_section == 'instruments':
                    elements.instruments.append(item)
                elif current_section == 'effects':
                    elements.effects.append(item)
            elif ':' in line and current_section == 'mix':
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if 'mix focus' in key:
                    elements.mix_focus = value
                elif 'stereo space' in key:
                    elements.stereo_space = value
                elif 'eq focus' in key:
                    elements.eq_focus = value

        return elements

    @staticmethod
    def _extract_metadata(text: str) -> Dict[str, str]:
        """Extract metadata from composition text"""
        metadata = {
            "generated_at": datetime.now().isoformat()
        }

        for line in text.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if key in ["musical style", "theme", "mood", "language"]:
                    metadata[key.replace(" ", "_")] = value

        return metadata

    @staticmethod
    def _parse_song_sections(sections: Dict[str, str]) -> Dict[str, SongSection]:
        """Parse individual song sections"""
        song_sections = {}

        # Parse each section type
        lyrics_sections = MusicParser._parse_lyrics_sections(sections.get("LYRICS", ""))
        chord_sections = MusicParser._parse_chord_sections(sections.get("CHORD PROGRESSION", ""))
        melody_sections = MusicParser._parse_melody_sections(sections.get("MELODY", ""))

        # Combine all sections
        all_section_names = set().union(
            lyrics_sections.keys(),
            chord_sections.keys(),
            melody_sections.keys()
        )

        for name in all_section_names:
            song_sections[name] = SongSection(
                name=name,
                lyrics=lyrics_sections.get(name),
                chords=chord_sections.get(name),
                melody=melody_sections.get(name)
            )

        return song_sections

    @staticmethod
    def _parse_lyrics_sections(lyrics_text: str) -> Dict[str, str]:
        """Parse lyrics into sections"""
        sections = {}
        current_section = None
        current_lines = []

        for line in lyrics_text.split('\n'):
            line = line.strip()
            if line.startswith('[') and ']' in line:
                if current_section and current_lines:
                    sections[current_section] = '\n'.join(current_lines).strip()
                current_section = line.strip('[]')
                current_lines = []
            elif line and not line.startswith('('):
                current_lines.append(line)

        # Handle last section
        if current_section and current_lines:
            sections[current_section] = '\n'.join(current_lines).strip()

        return sections

    @staticmethod
    def _parse_chord_sections(chord_text: str) -> Dict[str, str]:
        """Parse chord progressions into sections"""
        sections = {}
        current_section = None
        current_content = []

        for line in chord_text.split('\n'):
            line = line.strip()
            if line.startswith('[') and ']' in line:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.split(']')[0].strip('[')
                current_content = []
            elif line and not line.startswith('('):
                if any(key in line for key in ['Chord sequence:', 'Duration:', 'Rhythm:']):
                    current_content.append(line)

        # Handle last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    @staticmethod
    def _parse_melody_sections(melody_text: str) -> Dict[str, str]:
        """Parse melody information into sections"""
        sections = {}
        current_section = None
        current_content = []

        for line in melody_text.split('\n'):
            line = line.strip()
            if line.startswith('[') and ']' in line:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line.strip('[]').replace(' Melody', '')
                current_content = []
            elif line and ':' in line:
                key, value = line.split(':', 1)
                if value.strip():
                    current_content.append(f"{key.strip()}: {value.strip()}")

        # Handle last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections