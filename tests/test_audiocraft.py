# test/test_audiocraft.py
from audiocraft.models import MusicGen
import torch


def test_audiocraft():
    print("Testing Audiocraft setup...")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    try:
        model = MusicGen.get_pretrained('small')
        print("Successfully loaded MusicGen model")
    except Exception as e:
        print(f"Error loading model: {e}")


if __name__ == "__main__":
    test_audiocraft()