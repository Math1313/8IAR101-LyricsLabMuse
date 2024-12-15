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

    def generate_audio_export_metadata(self, lyrics: str, chord_progression: str, song_structure: str,
                                       musical_style: str, mood: str) -> dict:
        """
        Format composition data for audio generation.

        Args:
            lyrics (str): Full lyrics text
            chord_progression (str): Chord progression text
            song_structure (str): Complete song structure text
            musical_style (str): Style of music
            mood (str): Mood of the song

        Returns:
            dict: Formatted metadata for audio generation
        """
        try:
            # Extract musical parameters from song structure with safer parsing
            musical_params = {}
            if "[Song Technical Parameters]" in song_structure:
                try:
                    params_section = song_structure.split("[Song Technical Parameters]")[1]
                    # Find the end of the parameters section (next section or end of text)
                    if "[" in params_section:
                        params_section = params_section.split("[")[0]

                    for line in params_section.split('\n'):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            musical_params[key.strip()] = value.strip()
                except Exception as e:
                    logger.warning(f"Error parsing musical parameters: {str(e)}")

            # Safely get tempo with fallback
            try:
                tempo_str = musical_params.get("Tempo", "120 BPM")
                tempo = "".join(filter(str.isdigit, tempo_str)) or "120"
            except Exception:
                tempo = "120"

            # Safely get key with fallback
            try:
                primary_key = musical_params.get("Key", self._determine_primary_key(chord_progression))
                if not primary_key or primary_key.isspace():
                    primary_key = "C major"
            except Exception:
                primary_key = "C major"

            # Parse chord progression safely
            try:
                chord_data = self._process_chord_progression(chord_progression)
            except Exception as e:
                logger.warning(f"Error processing chord progression: {str(e)}")
                chord_data = {"default": {"raw_progression": ""}}

            # Structure the output
            return {
                "metadata": {
                    "style": musical_style,
                    "mood": mood,
                    "theme": "Generated composition"
                },
                "music_metadata": {
                    "musical_style": musical_style,
                    "mood": mood,
                    "tempo_bpm": tempo,
                    "primary_key": primary_key,
                    "time_signature": musical_params.get("Time Signature", "4/4"),
                    "genre_specific_feel": "standard"
                },
                "musical_structure": {
                    "song_structure": self._parse_song_structure(song_structure),
                    "chord_progression": chord_data
                },
                "lyrics_data": self._parse_lyrics(lyrics),
                "melody_data": self._extract_melody_data(song_structure),
                "audio_generation_hints": {
                    "recommended_instruments": self._suggest_instruments(musical_style),
                    "emotional_intensity_map": self._create_emotion_intensity_map(mood)
                }
            }
        except Exception as e:
            logger.error(f"Error formatting audio metadata: {str(e)}")
            # Return a minimal valid structure instead of raising an error
            return {
                "metadata": {"style": musical_style, "mood": mood},
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
                    "chord_progression": {"default": {"raw_progression": ""}}
                },
                "lyrics_data": "",
                "melody_data": "",
                "audio_generation_hints": {
                    "recommended_instruments": ["Piano"],
                    "emotional_intensity_map": {"neutral": 0.5}
                }
            }

    def _determine_primary_key(self, chord_progression: str) -> str:
        """Determine the primary musical key based on chord progression"""
        for key_type, keys in self.musical_key_mappings.items():
            for key, chord_set in keys.items():
                if any(chord in chord_progression for chord in chord_set):
                    return key
        return 'C'  # Default fallback key

    def _suggest_tempo_from_style_and_mood(self, musical_style: str, mood: str) -> int:
        """Suggest tempo based on musical style and mood"""
        tempo_mapping = {
            'Ballad': {'Sad': 60, 'Melancholic': 65, 'Romantic': 70},
            'Rock': {'Energetic': 120, 'Intense': 130, 'Angry': 135},
            'Pop': {'Happy': 100, 'Upbeat': 110, 'Neutral': 90},
            'Jazz': {'Contemplative': 80, 'Smooth': 75, 'Relaxed': 70},
            'Electronic': {'Intense': 128, 'Energetic': 135, 'Neutral': 110}
        }
        return tempo_mapping.get(musical_style, {}).get(mood, 90)

    def _process_chord_progression(self, chord_progression: str) -> Dict[str, Any]:
        """Process and structure chord progression"""
        current_section = None
        sections = {}

        for line in chord_progression.split('\n'):
            if line.startswith('['):
                current_section = line.strip('[]').split()[0]
                sections[current_section] = {'raw_progression': ''}
            elif current_section and 'Chord sequence:' in line:
                progression = line.split(':', 1)[1].strip()
                sections[current_section]['raw_progression'] = progression
                sections[current_section]['unique_chords'] = list(set(progression.split()))
                sections[current_section]['complexity'] = self._analyze_chord_pattern(progression.split())

        return sections

    def _analyze_chord_pattern(self, chords: list) -> str:
        """Analyze chord progression pattern"""
        if len(chords) <= 3:
            return "Simple"
        elif len(chords) <= 6:
            return "Moderate Complexity"
        else:
            return "Complex"

    def _parse_song_structure(self, structure_text: str) -> dict:
        """Parse the song structure into a structured format"""
        sections = []
        current_section = None

        for line in structure_text.split('\n'):
            if line.startswith('[') and ']' in line and not "Technical Parameters" in line:
                section_name = line.strip('[]')
                current_section = {
                    "name": section_name,
                    "type": section_name.split()[0].lower(),
                    "lyrics": "",
                    "chords": "",
                    "melody": ""
                }
                sections.append(current_section)
            elif current_section:
                if line.startswith('Lyrics:'):
                    current_section["lyrics"] = True
                elif line.startswith('Chords:'):
                    current_section["chords"] = True
                elif line.startswith('Melody:'):
                    current_section["melody"] = True

        return {"sections": sections}

    def _parse_lyrics(self, lyrics_text: str) -> str:
        """Clean and format lyrics text"""
        cleaned_lyrics = []
        for line in lyrics_text.split('\n'):
            if not line.startswith('[') and line.strip():
                cleaned_lyrics.append(line.strip())
        return '\n'.join(cleaned_lyrics)

    def _extract_melody_data(self, structure_text: str) -> str:
        """Extract melody information from the structure"""
        melody_info = []
        in_melody_section = False

        for line in structure_text.split('\n'):
            if 'Melody:' in line:
                in_melody_section = True
                continue
            elif in_melody_section and line.strip() and not line.startswith('['):
                if 'Scale:' in line or 'Contour:' in line:
                    melody_info.append(line.strip())
            elif line.startswith('[') and in_melody_section:
                in_melody_section = False

        return '\n'.join(melody_info)

    def _suggest_instruments(self, musical_style: str) -> list:
        """Suggest instruments based on musical style"""
        instrument_suggestions = {
            'Rock': ['Electric Guitar', 'Drums', 'Bass Guitar', 'Keyboard'],
            'Jazz': ['Saxophone', 'Piano', 'Double Bass', 'Trumpet'],
            'Pop': ['Synthesizer', 'Electronic Drums', 'Bass', 'Acoustic Guitar'],
            'Electronic': ['Synthesizer', 'Drum Machine', 'Digital Keyboard'],
            'Classical': ['Violin', 'Piano', 'Cello', 'Flute']
        }
        return instrument_suggestions.get(musical_style, ['Piano', 'Guitar'])

    def _create_emotion_intensity_map(self, mood: str) -> Dict[str, float]:
        """Create an emotional intensity map for audio generation"""
        emotion_intensity = {
            'Sad': {'melancholy': 0.8, 'intensity': 0.6, 'energy': 0.3},
            'Happy': {'joy': 0.9, 'intensity': 0.7, 'energy': 0.8},
            'Angry': {'anger': 0.9, 'intensity': 0.9, 'energy': 0.9},
            'Calm': {'serenity': 0.7, 'intensity': 0.4, 'energy': 0.2},
            'Romantic': {'love': 0.8, 'intensity': 0.6, 'energy': 0.5}
        }
        return emotion_intensity.get(mood, {'neutral': 0.5})

    def format_composition_for_export(self, composition_text: str) -> Dict[str, Any]:
        """Format the full composition text into a structured dictionary"""
        try:
            # Parse composition sections
            sections = self._parse_composition_sections(composition_text)

            # Extract title from Musical Parameters section
            title = self._extract_title(sections.get("MUSICAL PARAMETERS", ""))

            # Parse musical parameters into structured format
            musical_params = self._parse_musical_parameters(sections.get("MUSICAL PARAMETERS", ""))

            # Parse production elements
            production_elements = self._parse_production_elements(sections.get("MUSICAL PARAMETERS", ""))

            # Parse mix notes
            mix_notes = self._parse_mix_notes(sections.get("MUSICAL PARAMETERS", ""))

            return {
                "metadata": {
                    "title": title,
                    "musical_style": self._extract_style(composition_text),
                    "theme": self._extract_theme(composition_text),
                    "mood": self._extract_mood(composition_text),
                    "language": self._extract_language(composition_text)
                },
                "musical_parameters": musical_params,
                "production": production_elements,
                "mix_settings": mix_notes,
                "sections": {
                    "lyrics": sections.get("LYRICS", ""),
                    "chord_progression": self._parse_chord_progression(sections.get("CHORD PROGRESSION", "")),
                    "melody": self._parse_melody(sections.get("MELODY", "")),
                },
                "structure": self._extract_structure(composition_text)
            }
        except Exception as e:
            logger.error(f"Error formatting composition: {str(e)}")
            raise

    def _extract_title(self, params_text: str) -> str:
        """Extract title from musical parameters section"""
        try:
            title_section = params_text.split("[Title]")[1].split("[")[0].strip()
            return title_section if title_section else "Untitled Composition"
        except Exception:
            return "Untitled Composition"

    def _parse_musical_parameters(self, params_text: str) -> Dict[str, Any]:
        """Parse musical parameters section into structured dictionary"""
        params = {}
        try:
            params_section = params_text.split("[Musical Parameters]")[1].split("[")[0]
            for line in params_section.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    params[key] = value.strip()
        except Exception:
            params = {
                "tempo": "120 BPM",
                "key": "C major",
                "time_signature": "4/4",
                "genre_specific_feel": "Straight",
                "dynamic_level": "Medium"
            }
        return params

    def _parse_production_elements(self, params_text: str) -> Dict[str, List[str]]:
        """Parse production elements section into structured dictionary"""
        elements = {"main_instruments": [], "effects": []}
        try:
            prod_section = params_text.split("[Production Elements]")[1].split("[")[0]
            current_category = None

            for line in prod_section.split('\n'):
                line = line.strip()
                if line.startswith("Main Instruments:"):
                    current_category = "main_instruments"
                elif line.startswith("Effects:"):
                    current_category = "effects"
                elif line.startswith("-") and current_category:
                    elements[current_category].append(line[1:].strip())
        except Exception:
            elements = {
                "main_instruments": ["Piano", "Bass", "Drums"],
                "effects": ["Reverb"]
            }
        return elements

    def _parse_mix_notes(self, params_text: str) -> Dict[str, str]:
        """Parse mix notes section into structured dictionary"""
        mix_notes = {}
        try:
            mix_section = params_text.split("[Mix Notes]")[1].split("[")[0]
            for line in mix_section.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    mix_notes[key] = value.strip()
        except Exception:
            mix_notes = {
                "mix_focus": "Balanced",
                "stereo_space": "Centered",
                "eq_focus": "Full range"
            }
        return mix_notes

    def export_to_json(self, composition_text: str, filepath: str) -> None:
        """Export composition to JSON file"""
        try:
            formatted_data = self.format_composition_for_export(composition_text)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, indent=2)
            logger.info(f"Successfully exported JSON to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export to JSON: {str(e)}")
            raise

    def export_to_txt(self, composition_text: str, filepath: str) -> None:
        """Export composition to formatted text file"""
        try:
            formatted_text = self._format_txt_export(composition_text)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_text)
            logger.info(f"Successfully exported TXT to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export to TXT: {str(e)}")
            raise

    def _parse_composition_sections(self, text: str) -> Dict[str, Any]:
        """Parse composition text into sections"""
        sections = {}
        current_section = None
        current_content = []

        for line in text.split('\n'):
            if line.strip().startswith('##'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                    current_content = []
                current_section = line.replace('#', '').strip()
            elif current_section:
                current_content.append(line)

        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def _format_txt_export(self, text: str) -> str:
        """Format text export with additional metadata"""
        header = [
            "=" * 80,
            "AI Generated Music Composition",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            ""
        ]
        return '\n'.join(header + [text])

    def _extract_metadata_field(self, text: str, field: str) -> str:
        """Extract metadata field from composition text"""
        for line in text.split('\n'):
            if field.lower() in line.lower():
                return line.split(':', 1)[1].strip() if ':' in line else ""
        return ""

    def _extract_style(self, text: str) -> str:
        return self._extract_metadata_field(text, "Musical Style")

    def _extract_theme(self, text: str) -> str:
        return self._extract_metadata_field(text, "Theme")

    def _extract_mood(self, text: str) -> str:
        return self._extract_metadata_field(text, "Mood")

    def _extract_language(self, text: str) -> str:
        return self._extract_metadata_field(text, "Language")