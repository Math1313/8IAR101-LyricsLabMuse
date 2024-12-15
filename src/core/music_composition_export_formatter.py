# src/core/music_composition_export_formatter.py
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


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

    # core data processing methods
    def generate_audio_export_metadata(self, lyrics: str, chord_progression: str,
                                       song_structure: str, musical_style: str, mood: str) -> dict:
        """
        Format composition data for audio generation in a consolidated format.
        """
        try:
            # Extract musical parameters from song structure
            musical_params = self._parse_musical_parameters(song_structure)

            # Get core parameters with fallbacks
            tempo = musical_params.get("Tempo", "120 BPM")
            tempo_value = "".join(filter(str.isdigit, tempo)) or "120"
            primary_key = musical_params.get("Key", "C major")
            time_signature = musical_params.get("Time Signature", "4/4")

            return {
                "metadata": {
                    "style": musical_style,
                    "mood": mood,
                    "theme": "Generated composition"
                },
                "music_metadata": {
                    "musical_style": musical_style,
                    "mood": mood,
                    "tempo_bpm": tempo_value,
                    "primary_key": primary_key,
                    "time_signature": time_signature,
                    "genre_specific_feel": musical_params.get("Genre-Specific Feel", "standard")
                },
                "musical_structure": {
                    "song_structure": self._parse_song_structure(song_structure),
                    "chord_progression": self._parse_chord_data(chord_progression)
                },
                "lyrics_data": self._parse_lyrics(lyrics),
                "melody_data": self._parse_melody_data(song_structure),
                "audio_generation_hints": {
                    "recommended_instruments": self._suggest_instruments(musical_style),
                    "emotional_intensity": self._create_emotion_map(mood)
                }
            }
        except Exception as e:
            logger.error(f"Error formatting audio metadata: {str(e)}")
            return self._generate_fallback_metadata(musical_style, mood)

    def _parse_musical_parameters(self, params_text: str) -> Dict[str, str]:
        """
        Enhanced parsing of musical parameters with better structure handling.
        """
        params = {}
        try:
            current_section = None
            for line in params_text.split('\n'):
                line = line.strip()
                if line.startswith('**') and line.endswith('**'):
                    current_section = line.strip('*')
                elif line and ':' in line and not line.startswith('*'):
                    key, value = line.split(':', 1)
                    params[key.strip()] = value.strip()
                elif line and line.startswith('*') and ':' in line:
                    key, value = line.split(':', 1)
                    params[key.strip('* ')] = value.strip()
            return params
        except Exception as e:
            logger.error(f"Error parsing musical parameters: {str(e)}")
            return {}
    # structure parsing and chord progression handling
    def _parse_song_structure(self, structure_text: str) -> Dict[str, Any]:
        """
        Parse song structure with all musical elements.
        """
        sections = []
        current_section = None
        title = self._extract_title(structure_text)

        try:
            lines = structure_text.split('\n')
            technical_params = {}

            # First pass: Extract technical parameters
            for i, line in enumerate(lines):
                if "[Song Technical Parameters]" in line:
                    j = i + 1
                    while j < len(lines) and not lines[j].strip().startswith('['):
                        if ':' in lines[j]:
                            key, value = lines[j].split(':', 1)
                            technical_params[key.strip()] = value.strip()
                        j += 1

            # Second pass: Process sections
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('[') and ']' in line and "Technical Parameters" not in line:
                    section_name = line.strip('[]')
                    current_section = {
                        "name": section_name,
                        "type": section_name.split()[0].lower(),
                        "content": {
                            "lyrics": [],
                            "chords": {},
                            "melody": {},
                            "performance_notes": []
                        }
                    }
                    sections.append(current_section)

                elif current_section:
                    if line.startswith('('):
                        # Performance notes
                        current_section["content"]["performance_notes"].append(
                            line.strip('()').strip())
                    elif ':' in line:
                        content_type, content = line.split(':', 1)
                        content_type = content_type.strip().lower()

                        if content_type == 'lyrics':
                            # Collect lyrics until next section or content type
                            current_section["content"]["lyrics"] = [
                                l.strip() for l in content.split('\n') if l.strip()
                                                                          and not l.strip().startswith('(')
                            ]
                        elif content_type == 'chords':
                            # Parse chord progression from section 3
                            section_type = current_section["type"]
                            chord_data = self._parse_chord_progression(structure_text, section_type)
                            current_section["content"]["chords"] = chord_data
                        elif content_type == 'melody':
                            # Parse melody from section 4
                            section_type = current_section["type"]
                            melody_data = self._parse_melody(structure_text, section_type)
                            current_section["content"]["melody"] = melody_data

            return {
                "title": title,
                "technical_parameters": technical_params,
                "sections": sections
            }

        except Exception as e:
            logger.error(f"Error parsing song structure: {str(e)}")
            return {
                "title": "Untitled",
                "technical_parameters": {},
                "sections": []
            }

    def _parse_chord_progression(self, chord_text: str) -> Dict[str, Dict[str, Any]]:
        """
        Enhanced chord progression parsing with complete information.
        """
        chords = {}
        try:
            current_section = None
            current_data = {}

            for line in chord_text.split('\n'):
                line = line.strip()
                if line.startswith('**') and line.endswith('**'):
                    if current_section and current_data:
                        chords[current_section] = current_data
                    current_section = line.strip('*')
                    current_data = {'progression': [], 'rhythm': '', 'time_signature': ''}
                elif line.startswith('[') and ']' in line:
                    current_data['time_signature'] = line.strip('[]')
                elif ' - ' in line and not ':' in line:
                    current_data['progression'] = [c.strip() for c in line.split(' - ')]
                elif 'Rhythm:' in line:
                    current_data['rhythm'] = line.split(':', 1)[1].strip()

            # Add the last section
            if current_section and current_data:
                chords[current_section] = current_data

            return chords
        except Exception as e:
            logger.error(f"Error parsing chord progression: {str(e)}")
            return {}

    def _parse_melody(self, melody_text: str) -> Dict[str, Dict[str, Any]]:
        """
        Enhanced melody parsing with complete information.
        """
        melody = {}
        try:
            current_section = None
            current_data = {}

            for line in melody_text.split('\n'):
                line = line.strip()
                if line.startswith('**') and 'Melody' in line:
                    if current_section and current_data:
                        melody[current_section] = current_data
                    current_section = line.strip('*')
                    current_data = {
                        'scale': '',
                        'contour': '',
                        'range': '',
                        'syncopation': '',
                        'peak_notes': []
                    }
                elif 'Scale:' in line:
                    current_data['scale'] = line.split(':', 1)[1].strip()
                elif 'Contour:' in line:
                    current_data['contour'] = line.split(':', 1)[1].strip()
                elif 'Range:' in line:
                    current_data['range'] = line.split(':', 1)[1].strip()
                elif 'Syncopation:' in line:
                    current_data['syncopation'] = line.split(':', 1)[1].strip()
                elif 'Peak Notes:' in line:
                    current_data['peak_notes'].append(line.split(':', 1)[1].strip())

            # Add the last section
            if current_section and current_data:
                melody[current_section] = current_data

            return melody
        except Exception as e:
            logger.error(f"Error parsing melody: {str(e)}")
            return {}

    def _analyze_chord_complexity(self, chords: List[str]) -> str:
        """
        Analyze chord progression complexity.
        """
        if not chords:
            return "Simple"

        unique_chords = len(set(chords))
        extended_chords = sum(1 for chord in chords
                              if any(ext in chord for ext in ['maj7', 'min7', 'dim7', 'aug7', '7']))

        if unique_chords <= 3:
            base_complexity = "Simple"
        elif unique_chords <= 6:
            base_complexity = "Moderate"
        else:
            base_complexity = "Complex"

        if extended_chords > len(chords) * 0.5:
            return f"{base_complexity} with Extended Harmony"
        return base_complexity
    # melody parsing and data export methods
    def _parse_melody_data(self, structure_text: str) -> Dict[str, Any]:
        """
        Consolidated method to parse melody information from structure text.
        """
        melody_data = {}
        current_section = None

        try:
            for line in structure_text.split('\n'):
                line = line.strip()

                if line.startswith('[') and 'Melody' in line:
                    current_section = line.strip('[]').split()[0].lower()
                    melody_data[current_section] = {
                        'scale': '',
                        'contour': '',
                        'range': '',
                        'notes': [],
                        'technical_notes': []
                    }
                elif current_section and ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if 'scale' in key:
                        melody_data[current_section]['scale'] = value
                    elif 'contour' in key:
                        melody_data[current_section]['contour'] = value
                    elif 'range' in key:
                        melody_data[current_section]['range'] = value
                    elif value:
                        melody_data[current_section]['technical_notes'].append(f"{key}: {value}")

            # Add analysis for each section
            for section in melody_data.values():
                section['complexity'] = self._analyze_melody_complexity(section)

            return melody_data
        except Exception as e:
            logger.error(f"Error parsing melody data: {str(e)}")
            return {'verse': {'scale': 'C major', 'contour': 'Ascending', 'range': 'C3-C4'}}

    def _analyze_melody_complexity(self, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze melodic complexity based on various factors.
        """
        complexity = {'level': 'Simple', 'factors': []}

        try:
            # Analyze range
            if section_data.get('range'):
                try:
                    range_parts = section_data['range'].split('-')
                    if len(range_parts) == 2 and abs(ord(range_parts[1][0]) - ord(range_parts[0][0])) > 4:
                        complexity['level'] = 'Complex'
                        complexity['factors'].append('Wide range')
                except:
                    pass

            # Analyze contour
            if 'varied' in section_data.get('contour', '').lower():
                complexity['factors'].append('Varied contour')
                if complexity['level'] == 'Simple':
                    complexity['level'] = 'Moderate'

            return complexity
        except Exception as e:
            logger.error(f"Error analyzing melody complexity: {str(e)}")
            return {'level': 'Simple', 'factors': []}

    def export_to_json(self, composition_text: str, filepath: str) -> None:
        """
        Export composition data to JSON with complete structure.
        """
        try:
            # Parse all sections
            sections = self._parse_sections(composition_text)

            # Extract title
            title = self._extract_title(composition_text)

            # Parse metadata from header
            metadata = self._extract_metadata(composition_text)

            # Parse musical parameters
            musical_params = self._parse_musical_parameters(sections.get('1. MUSICAL PARAMETERS', ''))

            # Parse lyrics
            lyrics = self._parse_lyrics(sections.get('2. LYRICS', ''))

            # Parse chord progression
            chord_progression = self._parse_chord_progression(sections.get('3. CHORD PROGRESSION', ''))

            # Parse melody
            melody = self._parse_melody(sections.get('4. MELODY', ''))

            # Create formatted data structure
            formatted_data = {
                "metadata": metadata,
                "title": title,
                "musical_parameters": musical_params,
                "sections": {
                    "lyrics": lyrics,
                    "chord_progression": chord_progression,
                    "melody": melody
                }
            }

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, indent=2)

            logger.info(f"Successfully exported composition to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export to JSON: {str(e)}")
            raise

    def export_to_txt(self, composition_text: str, filepath: str) -> None:
        """
        Export composition to formatted text with complete structure.
        """
        try:
            sections = self._parse_sections(composition_text)

            # Format the complete structure section
            complete_structure = self._format_complete_structure(
                title=self._extract_title(composition_text),
                params=self._parse_musical_parameters(sections.get('1. MUSICAL PARAMETERS', '')),
                lyrics=self._parse_lyrics(sections.get('2. LYRICS', '')),
                chords=self._parse_chord_progression(sections.get('3. CHORD PROGRESSION', '')),
                melody=self._parse_melody(sections.get('4. MELODY', ''))
            )

            # Create the output text
            output = [
                "=" * 80,
                "AI Generated Music Composition",
                f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 80,
                "",
                composition_text.replace("## 5. COMPLETE SONG STRUCTURE\n\n",
                                         f"## 5. COMPLETE SONG STRUCTURE\n\n{complete_structure}")
            ]

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output))

            logger.info(f"Successfully exported composition to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export to TXT: {str(e)}")
            raise

    def _format_complete_structure(self, title: str, params: Dict, lyrics: Dict,
                                   chords: Dict, melody: Dict) -> str:
        """
        Format the complete structure section with all musical elements.
        """
        lines = []

        # Add title
        if title:
            lines.append(f"Title: {title}\n")

        # Add technical parameters
        lines.append("[Song Technical Parameters]")
        for key in ['Key', 'Tempo', 'Time Signature']:
            if key in params:
                lines.append(f"{key}: {params[key]}")
        lines.append("")

        # Add sections
        for section in ['Verse 1', 'Chorus', 'Verse 2', 'Bridge', 'Final Chorus']:
            lines.append(f"[{section}]")

            # Add lyrics
            lines.append("Lyrics:")
            if section in lyrics:
                lines.extend(lyrics[section])
            else:
                lines.append("(No lyrics for this section)")

            # Add chords
            lines.append("Chords:")
            section_type = section.split()[0]
            if section_type in chords:
                chord_data = chords[section_type]
                lines.append(f"Progression: {' - '.join(chord_data['progression'])}")
                lines.append(f"Rhythm: {chord_data['rhythm']}")
            else:
                lines.append("(No chord progression for this section)")

            # Add melody
            lines.append("Melody:")
            melody_section = f"{section_type} Melody"
            if melody_section in melody:
                melody_data = melody[melody_section]
                lines.append(f"Scale: {melody_data['scale']}")
                lines.append(f"Contour: {melody_data['contour']}")
                lines.append(f"Range: {melody_data['range']}")
            else:
                lines.append("(No melody for this section)")

            lines.append("")

        return '\n'.join(lines)
    # utility methods and helper functions
    def _parse_sections(self, text: str) -> Dict[str, str]:
        """
        Parse composition text into distinct sections with improved accuracy.
        """
        sections = {}
        current_section = None
        current_content = []

        try:
            in_section = False
            for line in text.split('\n'):
                if line.strip().startswith('## '):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                        current_content = []
                    current_section = line.replace('#', '').strip()
                    in_section = True
                elif in_section:
                    current_content.append(line)

            # Add the last section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()

            return sections
        except Exception as e:
            logger.error(f"Error parsing sections: {str(e)}")
            return {}

    def _extract_metadata(self, text: str) -> Dict[str, str]:
        """
        Extract metadata fields from composition text.
        """
        metadata = {}
        metadata_fields = ['Musical Style', 'Theme', 'Mood', 'Language']

        try:
            for line in text.split('\n'):
                for field in metadata_fields:
                    if field in line and ':' in line:
                        key = field.lower().replace(' ', '_')
                        metadata[key] = line.split(':', 1)[1].strip()
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {}

    def _extract_title(self, text: str) -> str:
        """Extract title from composition text"""
        try:
            if "**Title**" in text:
                lines = text.split("**Title**")[1].split("\n")
                for line in lines:
                    if line.strip():
                        return line.strip().strip('"')
            return "Untitled"
        except Exception as e:
            logger.error(f"Error extracting title: {str(e)}")
            return "Untitled"

    def _parse_lyrics(self, lyrics_text: str) -> Dict[str, List[str]]:
        """
        Enhanced lyrics parsing with section handling.
        """
        lyrics = {}
        try:
            current_section = None
            current_lines = []

            for line in lyrics_text.split('\n'):
                line = line.strip()
                if line.startswith('[') and ']' in line:
                    if current_section:
                        lyrics[current_section] = current_lines
                    current_section = line.strip('[]')
                    current_lines = []
                elif line and not line.startswith('('):
                    current_lines.append(line)

            # Add the last section
            if current_section:
                lyrics[current_section] = current_lines

            return lyrics
        except Exception as e:
            logger.error(f"Error parsing lyrics: {str(e)}")
            return {}

    def _suggest_instruments(self, musical_style: str) -> List[str]:
        """
        Suggest appropriate instruments based on musical style.
        """
        instrument_suggestions = {
            'Rock': ['Electric Guitar', 'Bass Guitar', 'Drums', 'Keyboard'],
            'Jazz': ['Piano', 'Double Bass', 'Drums', 'Saxophone'],
            'Pop': ['Synthesizer', 'Electric Guitar', 'Bass', 'Drums'],
            'Electronic': ['Synthesizer', 'Drum Machine', 'Digital Bass', 'Effects'],
            'Classical': ['Piano', 'Violin', 'Cello', 'Woodwinds'],
            'Blues': ['Electric Guitar', 'Bass', 'Drums', 'Hammond Organ'],
            'Country': ['Acoustic Guitar', 'Pedal Steel', 'Bass', 'Drums']
        }
        return instrument_suggestions.get(musical_style, ['Piano', 'Guitar', 'Bass', 'Drums'])

    def _create_emotion_map(self, mood: str) -> Dict[str, float]:
        """
        Create emotional intensity mapping for the given mood.
        """
        emotion_mappings = {
            'Happy': {'joy': 0.8, 'energy': 0.7, 'brightness': 0.8},
            'Sad': {'melancholy': 0.7, 'intensity': 0.4, 'darkness': 0.6},
            'Energetic': {'intensity': 0.9, 'energy': 0.9, 'excitement': 0.8},
            'Calm': {'serenity': 0.7, 'softness': 0.6, 'warmth': 0.5},
            'Angry': {'intensity': 0.9, 'aggression': 0.8, 'power': 0.9}
        }
        return emotion_mappings.get(mood, {'neutral': 0.5, 'intensity': 0.5})

    def _generate_fallback_metadata(self, musical_style: str, mood: str) -> Dict[str, Any]:
        """
        Generate fallback metadata structure in case of processing errors.
        """
        return {
            "metadata": {
                "style": musical_style,
                "mood": mood
            },
            "music_metadata": {
                "musical_style": musical_style,
                "mood": mood,
                "tempo_bpm": "120",
                "primary_key": "C major",
                "time_signature": "4/4",
                "genre_specific_feel": "standard"
            },
            "musical_structure": {
                "song_structure": {"sections": []},
                "chord_progression": {"verse": {"progression": ["C", "G", "Am", "F"]}}
            },
            "lyrics_data": "",
            "melody_data": {"verse": {"scale": "C major", "contour": "Simple"}},
            "audio_generation_hints": {
                "recommended_instruments": self._suggest_instruments(musical_style),
                "emotional_intensity": self._create_emotion_map(mood)
            }
        }

    def _extract_chord_sequence(self, text: str) -> List[str]:
        """Extract chord sequence from text"""
        for line in text.split('\n'):
            if '[' in line and ']' in line:
                chords = line.split('[')[1].split(']')[0]
                return [c.strip() for c in chords.split('-')]
        return []

    def _extract_rhythm_info(self, text: str) -> str:
        """Extract rhythm information from text"""
        for line in text.split('\n'):
            if 'Rhythm:' in line:
                return line.split('Rhythm:')[1].strip()
        return ""

    def _extract_duration_info(self, text: str) -> str:
        """Extract duration information from text"""
        for line in text.split('\n'):
            if 'Duration:' in line:
                return line.split('Duration:')[1].strip()
        return ""

    def _extract_scale_info(self, text: str) -> str:
        """Extract scale information from text"""
        for line in text.split('\n'):
            if 'Scale:' in line:
                return line.split('Scale:')[1].strip()
        return ""

    def _extract_range_info(self, text: str) -> str:
        """Extract range information from text"""
        for line in text.split('\n'):
            if 'Range:' in line:
                return line.split('Range:')[1].strip()
        return ""

    def _extract_contour_info(self, text: str) -> str:
        """Extract contour information from text"""
        for line in text.split('\n'):
            if 'Contour:' in line:
                return line.split('Contour:')[1].strip()
        return ""

    def _extract_melody_pattern(self, text: str) -> List[str]:
        """Extract melody pattern from text"""
        pattern = []
        in_pattern = False
        for line in text.split('\n'):
            if '*' in line and ':' not in line:  # Pattern typically starts after a bullet point
                in_pattern = True
                continue
            if in_pattern and line.strip():
                if '-' in line:
                    notes = [n.strip() for n in line.split('-')]
                    pattern.extend(notes)
        return pattern