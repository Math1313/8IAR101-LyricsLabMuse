from transformers import pipeline

class ObsceneFilter:
    def __init__(self):
        self.model = pipeline("text-classification", model="unitary/toxic-bert")

    def is_obscene(self, text) -> bool:
        result = self.model(text)
        threshold = 0.75
        if result[0]['score'] < threshold:
            return False
        else:
            return True