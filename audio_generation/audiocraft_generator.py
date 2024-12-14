# audio_generation/audiocraft_generator.py
from audiocraft.models import MusicGen, AudioGen
from audiocraft.data.audio import audio_write
import torch
import numpy as np
import os
from typing import Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudiocraftGenerator:
    """Handles audio generation using Audiocraft's MusicGen and AudioGen models"""

    def __init__(self, model_path: str = "facebook/musicgen-small"):
        # Check CUDA availability and set appropriate device
        self.device = self._setup_device()
        logger.info(f"Using device: {self.device}")

        # Initialize models with appropriate device settings
        try:
            self.music_model = MusicGen.get_pretrained(model_path)
            self.music_model.to(self.device)
            self.music_model.set_generation_params(duration=8)
            logger.info("MusicGen model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading MusicGen model: {e}")
            raise

    def _setup_device(self) -> str:
        """Setup and return the appropriate device with detailed logging"""
        if torch.cuda.is_available():
            device = 'cuda'
            logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            device = 'cpu'
            logger.info("CUDA not available, using CPU")
        return device

    def generate_music(self,
                       composition_data: Dict,
                       output_path: str = "output",
                       duration: int = 30) -> str:
        """
        Generate music based on composition data

        Args:
            composition_data: Dictionary containing composition details
            output_path: Directory to save generated audio
            duration: Duration in seconds

        Returns:
            Path to generated audio file
        """
        try:
            # Create prompt from composition data
            prompt = self._create_music_prompt(composition_data)
            logger.info(f"Generated prompt: {prompt}")

            # Set generation parameters
            self.music_model.set_generation_params(
                duration=duration,
                temperature=0.8,
                top_k=250,
                top_p=0.0
            )

            # Generate music
            wav = self.music_model.generate([prompt])

            # Ensure output directory exists
            os.makedirs(output_path, exist_ok=True)

            # Save generated audio
            output_file = os.path.join(output_path, "generated_music.wav")
            self._save_audio(wav[0], output_file)

            logger.info(f"Successfully generated music: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error generating music: {e}")
            raise

    def _create_music_prompt(self, composition_data: Dict) -> str:
        """Create a prompt for music generation from composition data"""
        music_metadata = composition_data.get("music_metadata", {})

        prompt = (
            f"{music_metadata.get('musical_style', '')} music "
            f"with tempo {music_metadata.get('tempo_bpm', '120')} BPM "
            f"in {music_metadata.get('primary_key', 'C major')}, "
            f"{music_metadata.get('mood', 'neutral')} mood"
        )

        return prompt.strip()

    def _save_audio(self,
                    wav_data: torch.Tensor,
                    output_file: str,
                    sample_rate: int = 44100) -> None:
        """Save audio data to file"""
        audio_write(
            output_file.split('.')[0],  # filename without extension
            wav_data.cpu(),
            sample_rate,
            strategy="loudness",
            loudness_compressor=True
        )


class FullSongGenerator:
    """Handles the generation of complete songs with music and vocals"""

    def __init__(self):
        self.audio_generator = AudiocraftGenerator()

    def generate_full_song(self,
                           composition_data: Dict,
                           output_path: str = "output") -> Dict[str, str]:
        """
        Generate a complete song including music and structure

        Args:
            composition_data: Dictionary containing song composition details
            output_path: Directory to save generated audio

        Returns:
            Dictionary with paths to generated audio files
        """
        try:
            # Calculate total duration based on structure
            duration = self._calculate_duration(composition_data)

            # Generate instrumental track
            instrumental_path = self.audio_generator.generate_music(
                composition_data,
                output_path,
                duration
            )

            return {
                "instrumental": instrumental_path,
                "duration": duration
            }

        except Exception as e:
            logger.error(f"Error generating full song: {e}")
            raise

    def _calculate_duration(self, composition_data: Dict) -> int:
        """Calculate total duration based on song structure"""
        # Get tempo and structure
        tempo = composition_data.get("music_metadata", {}).get("tempo_bpm", 120)
        structure = composition_data.get("musical_structure", {}).get("song_structure", {})

        # Basic duration calculation (can be made more sophisticated)
        sections = structure.get("sections", [])
        total_bars = len(sections) * 16  # Assuming 16 bars per section

        # Convert bars to seconds
        duration = (total_bars * 4 * 60) / tempo  # 4 beats per bar

        # Round up to nearest 5 seconds
        return min(int(np.ceil(duration / 5) * 5), 180)  # Max 3 minutes