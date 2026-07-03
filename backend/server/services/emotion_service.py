"""
Emotion Service

Loads and performs inference using the English Emotion
Recognition Model (EERM).

CTRL4 Chatbot MK2

Authors:
- Apilado, Jabez Timothy E.
- Quilantang, Grant Mihkael D.
- Lanix, Iligan
- Wylengco, Teyshaun Zell
"""

from dataclasses import dataclass

import torch

from ai_engine.core.models.model_loader import load_model
from ai_engine.core.tokenizers.tokenizer import load_tokenizer


LABELS = {
    0: "Positive",
    1: "Neutral",
    2: "Anger",
    3: "Sadness",
    4: "Fear"
}

NEGATIVE_EMOTIONS = {
    "Anger",
    "Sadness",
    "Fear"
}


@dataclass
class EmotionPrediction:
    emotion: str
    sentiment: str
    confidence: float
    is_negative: bool


class EmotionService:

    def __init__(self):

        self.tokenizer = load_tokenizer("english")
        self.model = load_model("english")

        self.model.eval()

    def predict(self, text: str) -> EmotionPrediction:

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )
        
        # DistilBERT does not use token_type_ids
        inputs.pop("token_type_ids", None)

        with torch.no_grad():
            outputs = self.model(**inputs)

        probabilities = torch.softmax(outputs.logits, dim=1)[0]

        prediction = torch.argmax(probabilities).item()

        emotion = LABELS[prediction]

        confidence = probabilities[prediction].item()

        if emotion in NEGATIVE_EMOTIONS:
            sentiment = "Negative"
            is_negative = True

        elif emotion == "Positive":
            sentiment = "Positive"
            is_negative = False

        else:
            sentiment = "Neutral"
            is_negative = False

        return EmotionPrediction(
            emotion=emotion,
            sentiment=sentiment,
            confidence=confidence,
            is_negative=is_negative
        )