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
        """Parse the full composition text into a structured format."""
        try:
            sections = self._parse_composition_sections(composition_text)

            # Extract and validate metadata
            metadata = self._extract_metadata(composition_text, sections)
            if not metadata:
                raise ValueError("No valid metadata found in composition")

            # Extract and validate musical parameters
            musical_params = self._extract_musical_parameters(
                sections.get("MUSICAL PARAMETERS", "")
            )

            # Build the composition structure
            composition_data = {}

            # Only add metadata if it exists
            if metadata:
                composition_data["metadata"] = metadata

            # Add music_metadata if required fields exist
            if all(key in metadata for key in ["style", "mood"]) and musical_params:
                composition_data["music_metadata"] = {
                    "musical_style": metadata["style"],
                    "mood": metadata["mood"],
                    "tempo_bpm": musical_params.get("tempo", self.default_parameters["tempo"]),
                    "primary_key": musical_params.get("key", self.default_parameters["key"]),
                    "time_signature": musical_params.get("time_signature", self.default_parameters["time_signature"]),
                    "genre_specific_feel": musical_params.get("genre_specific_feel",
                                                              self.default_parameters["genre_specific_feel"])
                }

            # Process main composition sections
            composition_content = {}

            # Add title if it exists
            if "title" in metadata:
                composition_content["title"] = metadata["title"]

            # Process and add other sections only if they contain data
            lyrics = self._clean_lyrics(sections.get("LYRICS", ""))
            if lyrics:
                composition_content["lyrics"] = lyrics

            chord_progression = self._process_chord_progression(sections.get("CHORD PROGRESSION", ""))
            if chord_progression:
                composition_content["chord_progression"] = chord_progression

            melody = self._extract_melody_data(sections.get("MELODY", ""))
            if melody:
                composition_content["melody"] = melody

            structure = self._parse_song_structure(sections.get("COMPLETE SONG STRUCTURE", ""))
            if structure and (structure.get("technical_parameters") or structure.get("sections")):
                composition_content["structure"] = structure

            if composition_content:
                composition_data["composition"] = composition_content

            # Add technical parameters if they exist and aren't empty
            if musical_params:
                composition_data["technical_parameters"] = musical_params
            composition_data["lyrics"] = "test"
            composition_data["chord_progression"] = "test"
            composition_data["full_structure"] = "test"
            print(musical_params)
            print(composition_content)
            # print(composition_data)
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
        """Parse the complete song structure.

        Args:
            structure_text (str): Raw structure text

        Returns:
            Dict[str, Any]: Structured song data with only populated sections
        """
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
                section_content = {}
            elif line.startswith('[') and ']' in line:
                # If we have a previous section with content, add it
                if section_content:
                    structure['sections'].append(section_content)

                section_name = line.strip('[]')
                section_content = {'name': section_name}
            elif current_section == 'technical_parameters' and ':' in line:
                key, value = line.split(':', 1)
                value = value.strip()
                if value:  # Only add non-empty values
                    structure['technical_parameters'][key.strip()] = value
            elif ':' in line:
                content_type = line.split(':', 1)[0].lower().strip()
                if content_type in ['lyrics', 'chords', 'melody']:
                    # Look ahead for content after this line
                    content = self._extract_section_content(structure_text, line)
                    if content:  # Only add if we have content
                        section_content[content_type] = content

        # Add the last section if it has content
        if section_content:
            structure['sections'].append(section_content)

        # Clean up the structure
        if not structure['technical_parameters']:
            del structure['technical_parameters']

        return structure if structure.get('sections') or structure.get('technical_parameters') else {}

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
                if current_section and current_lines:
                    content = '\n'.join(current_lines)
                    if content:  # Only add section if it has content
                        sections[current_section] = content
                current_section = line.strip('[]').split('[')[0].strip()
                current_lines = []
            elif line and not line.startswith('(') and ':' not in line:
                current_lines.append(line)

        # Handle last section
        if current_section and current_lines:
            content = '\n'.join(current_lines)
            if content:  # Only add section if it has content
                sections[current_section] = content

        return sections if sections else {}

    def _process_chord_progression(self, chord_text: str) -> Dict[str, Any]:
        """Process and structure chord progressions."""
        sections: Dict[str, Dict[str, Any]] = {}
        current_section = None

        for line in chord_text.split('\n'):
            line = line.strip()
            if line.startswith('**') and not line.startswith('**Production'):
                current_section = line.strip('*').strip()
                sections[current_section] = {
                    'progression': [],
                    'time_signature': None,
                    'rhythm': []
                }
            elif current_section:
                if '[' in line and ']' in line:
                    time_sig = line.strip('[]').strip()
                    if time_sig:
                        sections[current_section]['time_signature'] = time_sig
                elif '-' in line and ('Major' in line or 'Minor' in line):
                    chords = [c.strip() for c in line.split('-') if c.strip()]
                    if chords:
                        sections[current_section]['progression'].extend(chords)
                elif 'beat:' in line.lower():
                    sections[current_section]['rhythm'].append(line)

        # Clean up empty sections and fields
        return {
            section: {
                k: v for k, v in data.items()
                if v and (not isinstance(v, list) or len(v) > 0)
            }
            for section, data in sections.items()
            if any(v and (not isinstance(v, list) or len(v) > 0)
                   for v in data.values())
        }

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

    def generate_audio_export_metadata(self, lyrics: str, chord_progression: str,
                                       song_structure: str, musical_style: str,
                                       mood: str) -> Dict[str, Any]:
        """
        Generate metadata for audio generation, maintaining backward compatibility.
        """
        try:
            # Parse the song structure for technical parameters
            params = self._extract_musical_parameters(song_structure)

            # Build the metadata structure with only populated fields
            metadata = {
                "metadata": {
                    "style": musical_style,
                    "mood": mood
                }
            }

            # Add music metadata if we have valid parameters
            music_metadata = {
                "musical_style": musical_style,
                "mood": mood
            }

            # Only add parameters that exist
            if params.get("tempo"):
                music_metadata["tempo_bpm"] = params["tempo"]
            if params.get("key"):
                music_metadata["primary_key"] = params["key"]
            if params.get("time_signature"):
                music_metadata["time_signature"] = params["time_signature"]
            if params.get("genre_specific_feel"):
                music_metadata["genre_specific_feel"] = params["genre_specific_feel"]

            metadata["music_metadata"] = music_metadata

            # Process structure and add only if valid
            structure = self._parse_song_structure(song_structure)
            if structure:
                metadata["musical_structure"] = dict(song_structure=structure)
                # metadata["musical_structure"] = {
                #     "song_structure": structure
                # }

            # Process chord progression and add if valid
            chords = self._process_chord_progression(chord_progression)
            if chords:
                if "musical_structure" not in metadata:
                    metadata["musical_structure"] = {}
                metadata["musical_structure"]["chord_progression"] = chords

            # Process lyrics and add if valid
            clean_lyrics = self._clean_lyrics(lyrics)
            if clean_lyrics:
                metadata["lyrics_data"] = clean_lyrics

            # Process melody data if present in structure
            melody = self._extract_melody_data(song_structure)
            if melody:
                metadata["melody_data"] = melody

            return metadata

        except Exception as e:
            logger.error(f"Error generating audio metadata: {str(e)}")
            raise