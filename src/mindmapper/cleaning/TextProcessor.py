from typing import List
from nltk.tokenize import sent_tokenize
from utils import nltk_helpers


class TextProcessor:
    def __init__(self) -> None:
        self._text_string = ""

    @property
    def text_string(self) -> str:
        return self._text_string

    @text_string.setter
    def text_string(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Text must be a string")
        self._text_string = value

    def clean_text(self) -> str:
        """Normalize whitespace and return the cleaned text."""
        self.text_string = self.text_string.replace("\n", " ")
        return self.text_string

    def chunk_text(self, sent_per_chunk: int) -> List[str]:
        if sent_per_chunk <= 0:
            raise ValueError("sent_per_chunk must be a positive integer")

        nltk_helpers.ensure_punkt()
        sentences = sent_tokenize(self.text_string)

        chunks: List[str] = []
        for i in range(0, len(sentences), sent_per_chunk):
            chunk = " ".join(sentences[i : i + sent_per_chunk]).strip()
            if chunk:
                chunks.append(chunk)
        return chunks