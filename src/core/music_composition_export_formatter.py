# src/core/music_composition_export_formatter.py
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MusicCompositionExportFormatter:
    """
    A comprehensive formatter for music composition data that handles:
    - JSON and TXT export
    - Audio generation metadata formatting
    - Parsing of composition sections
    - Cleaning and structuring of musical data
    """

    def __init__(self):
        self.default_parameters = {
            "tempo": "120",
            "key": "C major",
            "time_signature": "4/4",
            "genre_specific_feel": "standard"
        }

    def parse_composition(self, composition_text: str) -> Dict[str, Any]:
        """
        Parse the full composition text into a structured format.

        Args:
            composition_text (str): Raw composition text to parse

        Returns:
            Dict[str, Any]: Structured composition data
        """
        try:
            # Split into sections
            sections = self._parse_composition_sections(composition_text)

            # Extract and validate metadata
            metadata = self._extract_metadata(composition_text, sections)
            if not metadata:
                raise ValueError("No valid metadata found in composition")

            # Build the composition structure
            composition_data = {
                "metadata": metadata
            }

            # Extract musical parameters
            musical_params = self._extract_musical_parameters(
                sections.get("MUSICAL PARAMETERS", "")
            )

            # Add music_metadata if required fields exist
            if all(key in metadata for key in ["style", "mood"]) and musical_params:
                composition_data["music_metadata"] = {
                    "musical_style": metadata["style"],
                    "mood": metadata["mood"],
                    "tempo_bpm": musical_params.get("tempo", self.default_parameters["tempo"]),
                    "primary_key": musical_params.get("key", self.default_parameters["key"]),
                    "time_signature": musical_params.get("time_signature",
                                                         self.default_parameters["time_signature"]),
                    "genre_specific_feel": musical_params.get("genre_specific_feel",
                                                              self.default_parameters["genre_specific_feel"])
                }

            # Extract main composition content
            lyrics = self._clean_lyrics(sections.get("LYRICS", ""))
            chord_progression = self._process_chord_progression(
                sections.get("CHORD PROGRESSION", ""))
            melody = self._extract_melody_data(sections.get("MELODY", ""))
            structure = self._parse_song_structure(
                sections.get("COMPLETE SONG STRUCTURE", ""))

            # Add composition content
            composition_data.update({
                "lyrics": lyrics if lyrics else {},
                "chord_progression": chord_progression if chord_progression else {},
                "melody": melody if melody else {},
                "full_structure": structure if structure else {},
            })

            # Add technical parameters if they exist
            if musical_params:
                composition_data["technical_parameters"] = musical_params

                # composition_data["lyrics"] = "test"
                # composition_data["chord_progression"] = "test"
                # composition_data["full_structure"] = "test"
                print(musical_params)
                print(composition_data)

            return composition_data

        except Exception as e:
            logger.error(f"Error parsing composition: {str(e)}")
            raise

    def _parse_composition_sections(self, text: str) -> Dict[str, str]:
        """Parse composition text into main sections."""
        sections = {}
        current_section = None
        current_content = []

        for line in text.split('\n'):
            if line.strip().startswith('##'):
                if current_section and current_content:
                    content = '\n'.join(current_content).strip()
                    if content:  # Only add section if it has content
                        sections[current_section] = content
                    current_content = []
                current_section = line.replace('#', '').strip()
            elif current_section:
                current_content.append(line)

        # Handle last section
        if current_section and current_content:
            content = '\n'.join(current_content).strip()
            if content:  # Only add section if it has content
                sections[current_section] = content

        return sections

    def _parse_song_structure(self, structure_text: str) -> Dict[str, Any]:
        """Parse the complete song structure."""
        structure = {
            'technical_parameters': {},
            'sections': []
        }

        current_section = None
        section_content = {}

        for line in structure_text.split('\n'):
            line = line.strip()

            if line.startswith('[Song Technical Parameters]'):
                current_section = 'technical_parameters'
            elif line.startswith('[') and ']' in line:
                # Save previous section content
                if section_content:
                    structure['sections'].append(section_content)

                # Start new section
                section_name = line.strip('[]')
                section_content = {'name': section_name}
            elif current_section == 'technical_parameters' and ':' in line:
                key, value = line.split(':', 1)
                value = value.strip()
                if value:
                    structure['technical_parameters'][key.strip()] = value
            elif ':' in line:
                key = line.split(':', 1)[0].lower().strip()
                if key in ['lyrics', 'chords', 'melody']:
                    content = self._extract_section_content(structure_text, line)
                    if content:
                        section_content[key] = content

        # Add final section
        if section_content:
            structure['sections'].append(section_content)

        # Remove empty sections
        if not structure['technical_parameters']:
            del structure['technical_parameters']
        if not structure['sections']:
            del structure['sections']

        return structure

    def _extract_metadata(self, composition_text: str, sections: Dict[str, str]) -> Dict[str, str]:
        """Extract and validate all metadata fields."""
        metadata = {
            "title": self._extract_title(sections.get("MUSICAL PARAMETERS", "")),
            "style": self._extract_metadata_field(composition_text, "Musical Style"),
            "theme": self._extract_metadata_field(composition_text, "Theme"),
            "mood": self._extract_metadata_field(composition_text, "Mood"),
            "language": self._extract_metadata_field(composition_text, "Language"),
            "generated_at": datetime.now().isoformat()
        }

        # Remove empty fields
        return {k: v for k, v in metadata.items() if v}

    def _extract_title(self, params_text: str) -> str:
        """Extract title from parameters section."""
        for line in params_text.split('\n'):
            if 'Title' in line:
                next_lines = params_text.split(line)[1].split('\n')
                for next_line in next_lines:
                    if next_line.strip() and not next_line.strip().startswith('**'):
                        return next_line.strip().strip('"')
        return ""

    def _extract_metadata_field(self, text: str, field: str) -> str:
        """Extract specific metadata field from text."""
        for line in text.split('\n'):
            if f"{field}:" in line:
                value = line.split(':', 1)[1].strip()
                if value:  # Only return non-empty values
                    return value
        return ""

    def _extract_musical_parameters(self, text: str) -> Dict[str, str]:
        """Extract all musical parameters from text."""
        params = {}
        current_section = None

        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('**'):
                current_section = line.strip('*').strip().lower()
            elif ':' in line and current_section == "musical parameters":
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if value:  # Only add parameter if it has a value
                    if 'tempo' in key:
                        params['tempo'] = value.split()[0]  # Extract just the number
                    elif 'key' in key:
                        params['key'] = value
                    elif 'time signature' in key:
                        params['time_signature'] = value
                    elif 'genre-specific feel' in key:
                        params['genre_specific_feel'] = value

        # Only return params that have values
        return {k: v for k, v in params.items() if v}

    def _extract_section_content(self, text: str, start_line: str) -> str:
        """Extract content for a section starting from a specific line."""
        lines = text.split('\n')
        start_idx = lines.index(start_line) + 1
        content_lines = []

        for line in lines[start_idx:]:
            line = line.strip()
            if not line:
                continue
            if line.startswith('[') or line.startswith('Lyrics:') or \
                    line.startswith('Chords:') or line.startswith('Melody:'):
                break
            if not line.startswith('('):  # Skip comments/instructions
                content_lines.append(line)

        return '\n'.join(content_lines).strip()

    def _clean_lyrics(self, lyrics_text: str) -> Dict[str, str]:
        """Clean and structure lyrics by section."""
        sections = {}
        current_section = None
        current_lines = []

        for line in lyrics_text.split('\n'):
            line = line.strip()
            if line.startswith('[') and ']' in line:
                # Save previous section if exists
                if current_section and current_lines:
                    content = '\n'.join(current_lines).strip()
                    if content:  # Only add non-empty sections
                        sections[current_section] = content
                    current_lines = []
                # Extract new section name
                current_section = line.strip('[]').split('[')[0].strip()
            elif line and not line.startswith('(') and ':' not in line:
                current_lines.append(line)

        # Handle last section
        if current_section and current_lines:
            content = '\n'.join(current_lines).strip()
            if content:
                sections[current_section] = content

        return sections

    def _process_chord_progression(self, chord_text: str) -> Dict[str, Any]:
        """Process and structure chord progressions."""
        sections = {}
        current_section = None
        current_content = {
            'progression': [],
            'time_signature': None,
            'rhythm': []
        }

        for line in chord_text.split('\n'):
            line = line.strip()

            # Handle section headers
            if line.startswith('[') and ']' in line:
                # Save previous section if exists
                if current_section and any(current_content.values()):
                    sections[current_section] = {
                        k: v for k, v in current_content.items()
                        if v and (not isinstance(v, list) or len(v) > 0)
                    }

                # Start new section
                current_section = line.strip('[]').split('[')[0].strip()
                current_content = {
                    'progression': [],
                    'time_signature': None,
                    'rhythm': []
                }

                # Extract time signature if present
                if '[' in line and ']' in line:
                    time_sig = line.split('[')[1].split(']')[0].strip()
                    if time_sig:
                        current_content['time_signature'] = time_sig

            # Handle chord sequences
            elif 'Chord sequence:' in line:
                chords = line.split(':', 1)[1].strip()
                if chords:
                    current_content['progression'].extend(
                        [c.strip() for c in chords.split(',') if c.strip()]
                    )

            # Handle rhythm patterns
            elif 'Rhythm:' in line:
                rhythm = line.split(':', 1)[1].strip()
                if rhythm:
                    current_content['rhythm'].append(rhythm)

        # Add final section
        if current_section and any(current_content.values()):
            sections[current_section] = {
                k: v for k, v in current_content.items()
                if v and (not isinstance(v, list) or len(v) > 0)
            }

        return sections

    def _extract_melody_data(self, melody_text: str) -> Dict[str, Any]:
        """Extract and structure melody information."""
        sections = {}
        current_section = None

        for line in melody_text.split('\n'):
            line = line.strip()
            if line.startswith('###'):
                current_section = line.strip('#').strip('[]').strip()
                if current_section:
                    sections[current_section] = {}
            elif current_section and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key in ['Scale', 'Contour', 'Range', 'Syncopation'] and value:
                    sections[current_section][key.lower()] = value

        # Remove empty sections
        return {k: v for k, v in sections.items() if v}

    def export_to_json(self, composition_text: str, filepath: str) -> None:
        """Export composition to JSON file."""
        try:
            formatted_data = self.parse_composition(composition_text)
            print("export_to_json", formatted_data)
            if not formatted_data:
                raise ValueError("No valid data to export")

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully exported JSON to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export to JSON: {str(e)}")
            raise

    def export_to_txt(self, composition_text: str, filepath: str) -> None:
        """Export composition to formatted text file."""
        try:
            if not composition_text.strip():
                raise ValueError("No content to export")

            header = [
                "=" * 80,
                "AI Generated Music Composition",
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 80,
                ""
            ]

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(header + [composition_text]))
            logger.info(f"Successfully exported TXT to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export to TXT: {str(e)}")
            raise

    def generate_audio_export_metadata(self, lyrics: Dict[str, Any], chord_progression: Dict[str, Any],
                                       song_structure: Dict[str, Any], musical_style: str,
                                       mood: str) -> Dict[str, Any]:
        """
        Generate metadata for audio generation, handling dictionary inputs properly.

        Args:
            lyrics (Dict[str, Any]): Dictionary containing lyrics sections
            chord_progression (Dict[str, Any]): Dictionary containing chord progression data
            song_structure (Dict[str, Any]): Dictionary containing song structure data
            musical_style (str): Style of the music
            mood (str): Mood of the song

        Returns:
            Dict[str, Any]: Formatted metadata for audio generation
        """
        try:
            # Build the base metadata structure
            metadata = {
                "metadata": {
                    "style": musical_style,
                    "mood": mood
                }
            }

            # Add music metadata with default values
            music_metadata = {
                "musical_style": musical_style,
                "mood": mood,
                "tempo_bpm": "120",  # Default tempo
                "primary_key": "C major",  # Default key
                "time_signature": "4/4",  # Default time signature
                "genre_specific_feel": "standard"  # Default feel
            }

            # Extract and add technical parameters if available
            if song_structure and 'technical_parameters' in song_structure:
                tech_params = song_structure['technical_parameters']
                for param_name, param_value in tech_params.items():
                    param_name_lower = param_name.lower()
                    if 'tempo' in param_name_lower:
                        # Extract just the number from tempo
                        tempo_value = ''.join(filter(str.isdigit, param_value))
                        if tempo_value:
                            music_metadata["tempo_bpm"] = tempo_value
                    elif 'key' in param_name_lower:
                        music_metadata["primary_key"] = param_value
                    elif 'time signature' in param_name_lower:
                        music_metadata["time_signature"] = param_value
                    elif 'feel' in param_name_lower:
                        music_metadata["genre_specific_feel"] = param_value

            metadata["music_metadata"] = music_metadata

            # Process song structure
            if song_structure and 'sections' in song_structure:
                metadata["musical_structure"] = {
                    "song_structure": {
                        "sections": song_structure['sections']
                    }
                }

            # Process chord progression
            if chord_progression:
                chord_text = ""
                for section, data in chord_progression.items():
                    chord_text += f"[{section}]\n"
                    if 'progression' in data:
                        chord_text += f"Chord sequence: {', '.join(data['progression'])}\n"
                    if 'time_signature' in data:
                        chord_text += f"Time signature: {data['time_signature']}\n"
                    if 'rhythm' in data:
                        chord_text += f"Rhythm: {', '.join(data['rhythm'])}\n"

                if "musical_structure" not in metadata:
                    metadata["musical_structure"] = {}
                metadata["musical_structure"]["chord_progression"] = {"raw_progression": chord_text}

            # Process lyrics
            if lyrics:
                lyrics_text = ""
                for section, content in lyrics.items():
                    lyrics_text += f"[{section}]\n{content}\n\n"

                metadata["lyrics_data"] = lyrics_text.strip()

            # Log the final metadata for debugging
            logging.debug(f"Generated audio metadata: {metadata}")

            return metadata

        except Exception as e:
            logger.error(f"Error generating audio metadata: {str(e)}")
            raise