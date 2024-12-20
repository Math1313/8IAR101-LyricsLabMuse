from audiocraft.models import MusicGen
import torch
import logging
import os
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudiocraftGenerator:
    def __init__(self):
        try:
            # Check CUDA availability
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Using device: {self.device}")

            # Initialize the model
            self.music_model = MusicGen.get_pretrained('small')

            # Set the model to the appropriate device
            if hasattr(self.music_model, 'to'):
                self.music_model = self.music_model.to(self.device)

            # Set default parameters
            self.set_generation_params(5)

        except Exception as e:
            logger.error(f"Error initializing MusicGen model: {str(e)}")
            raise

    def set_generation_params(self, duration: int = 30):
        """Set generation parameters"""
        if hasattr(self.music_model, 'set_generation_params'):
            self.music_model.set_generation_params(
                use_sampling=True,
                top_k=250,
                duration=duration  # Duration in seconds
            )

    def generate_full_song(self, composition_data: Dict[str, Any], progress_callback=None) -> Dict[str, str]:
        try:
            print(composition_data)
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Extract metadata for filename
            style = composition_data["music_metadata"]["musical_style"]
            theme = composition_data.get("metadata", {}).get("theme", "no_theme")
            mood = composition_data["music_metadata"]["mood"]
            language = composition_data.get("metadata", {}).get("language", "no_lang")

            # Clean metadata values for safe filename
            def clean_filename(text: str) -> str:
                # Replace spaces and special characters
                return text.lower().replace(" ", "_").replace("/", "_")

            # Create filename with all parameters
            filename = f"{timestamp}_{clean_filename(style)}_{clean_filename(theme)}_{clean_filename(mood)}_{clean_filename(language)}.wav"

            # Create output directory
            output_dir = os.path.join("output", "generated")
            os.makedirs(output_dir, exist_ok=True)

            instrumental_path = os.path.join(output_dir, filename)

            # Generate prompt from composition data
            prompt = self._construct_generation_prompt(
                style=composition_data["music_metadata"]["musical_style"],
                mood=composition_data["music_metadata"]["mood"],
                tempo=composition_data["music_metadata"]["tempo_bpm"],
                key=composition_data["music_metadata"]["primary_key"],
                composition_data=composition_data
            )

            # Generate and save audio
            wav = self.music_model.generate([prompt])
            self.save_audio(wav, instrumental_path)

            logger.info(f"Generated audio file: {filename}")

            if progress_callback:
                progress_callback(100, "Audio generation complete!")

            return {
                "instrumental": instrumental_path
            }

        except Exception as e:
            if progress_callback:
                progress_callback(-1, f"Error: {str(e)}")
            logger.error(f"Error generating full song: {str(e)}")
            raise

    def _construct_generation_prompt(self, style: str, mood: str, tempo: int,
                                     key: str, composition_data: Dict[str, Any]) -> str:
        """
        Construct a detailed prompt using all musical information
        """
        # Extract melody information
        melody_data = composition_data.get('melody_data', '')
        melody_scale = ''
        melody_contour = ''
        if melody_data:
            # Parse melody information
            for line in melody_data.split('\n'):
                if 'Scale:' in line:
                    melody_scale = line.split('Scale:')[1].strip()
                elif 'Contour:' in line:
                    melody_contour = line.split('Contour:')[1].strip()

        # Extract chord progression
        chord_progression = composition_data.get('musical_structure', {}).get(
            'chord_progression', {}).get('raw_progression', '')

        # Get genre-specific feel from musical parameters
        genre_feel = composition_data.get('music_metadata', {}).get('genre_specific_feel', 'standard')

        # Construct detailed prompt
        prompt = (
            f"Generate {style} music "
            f"in {key} at {tempo} BPM. "
        )

        # Add melody information if available
        if melody_scale and melody_contour:
            prompt += (
                f"Use {melody_scale} scale with {melody_contour} melody movement. "
            )

        # Add chord progression if available
        if chord_progression:
            prompt += f"Follow chord progression: {chord_progression}. "

        # Add mood and feel
        prompt += (
            f"Create a {mood} atmosphere with {genre_feel} feel. "
            f"Make it sound professional and well-produced with clear "
            f"transitions between sections."
        )

        return prompt

    def _calculate_song_duration(self, composition_data: Dict[str, Any]) -> int:
        """
        Calculate song duration based on tempo and structure
        Returns duration in seconds
        """
        try:
            # Get tempo
            tempo = composition_data["music_metadata"]["tempo_bpm"]

            # Get structure sections
            sections = composition_data.get("musical_structure", {}).get(
                "song_structure", {}
            ).get("sections", [])

            # Calculate approximate duration based on sections and tempo
            # Assuming each section is typically 8 bars
            total_bars = len(sections) * 8

            # Duration = (bars * beats per bar * 60 seconds) / tempo
            # Assuming 4/4 time signature (4 beats per bar)
            duration = (total_bars * 4 * 60) / tempo

            # Ensure minimum and maximum duration
            duration = max(min(duration, 180), 30)  # Between 30s and 3m

            return int(duration)

        except Exception:
            # Default duration if calculation fails
            return 60

    def save_audio(self, wav: torch.Tensor, output_path: str):
        """Save the generated audio to a file"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # MusicGen returns a 3D tensor [batch, channels, time]
            # We need to squeeze the batch dimension if it's 1
            if wav.dim() == 3:
                wav = wav.squeeze(0)  # Remove batch dimension

            # Save the audio file
            if hasattr(self.music_model, 'save_wav'):
                self.music_model.save_wav(wav, output_path)
            else:
                # Fallback to torchaudio if needed
                import torchaudio
                torchaudio.save(output_path, wav.cpu(), 32000)

        except Exception as e:
            logger.error(f"Error saving audio: {str(e)}")
            raise

    def _estimate_generation_time(self, composition_data: Dict[str, Any]) -> int:
        """
        Estimate generation time based on audio parameters
        Returns estimated time in seconds
        """
        # Get base generation parameters
        duration = self.music_model.generation_params.get('duration', 5)

        # Factor in model size
        # 'small' model is faster than 'medium' or 'large'
        model_multiplier = 1.0  # For 'small' model

        # Base time: roughly 10 seconds per second of audio for 'small' model
        base_time = duration * 10

        # Add overhead for initialization and saving
        overhead = 30  # seconds

        estimated_time = (base_time * model_multiplier) + overhead

        logger.info(f"Estimated generation time: {estimated_time} seconds for {duration}s of audio")
        return int(estimated_time)