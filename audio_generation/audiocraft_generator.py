from audiocraft.models import MusicGen
import torch
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudiocraftGenerator:
    def __init__(self):
        try:
            # Check CUDA availability
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Using device: {self.device}")

            # Initialize the model properly
            self.music_model = MusicGen.get_pretrained('small')

            # Set the model to the appropriate device
            if hasattr(self.music_model, 'to'):
                self.music_model = self.music_model.to(self.device)

            # Set default parameters
            self.set_generation_params()

        except Exception as e:
            logger.error(f"Error loading MusicGen model: {str(e)}")
            raise

    def set_generation_params(self):
        """Set default generation parameters"""
        if hasattr(self.music_model, 'set_generation_params'):
            self.music_model.set_generation_params(
                use_sampling=True,
                top_k=250,
                duration=10  # Default duration in seconds
            )

    def generate_audio(self, prompt: str, duration: int = 10) -> torch.Tensor:
        """Generate audio from text prompt"""
        try:
            # Update duration if different from default
            if hasattr(self.music_model, 'set_generation_params'):
                self.music_model.set_generation_params(duration=duration)

            # Generate the audio
            wav = self.music_model.generate([prompt])

            return wav

        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise

    def save_audio(self, wav: torch.Tensor, output_path: str):
        """Save the generated audio to a file"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

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