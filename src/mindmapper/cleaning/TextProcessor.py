from typing import List
from nltk.tokenize import sent_tokenize
from utils import nltk_helpers

# Chunking strategy constants
CHUNKING_STRATEGY_FIXED = "fixed"
CHUNKING_STRATEGY_HIERARCHICAL = "hierarchical"


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
        """Legacy method for fixed-length sentence-based chunking."""
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

    def chunk_text_hierarchical(self, max_chunk_size: int = 10) -> List[str]:
        """
        Hierarchical chunking that respects paragraph boundaries.

        Strategy:
        1. Split on paragraph breaks (\\n\\n)
        2. If a paragraph has < 2 sentences, merge it backward with previous paragraph
        3. If a paragraph has > max_chunk_size sentences, sub-chunk by sentences
        4. If no paragraph breaks exist, fall back to fixed-length chunking

        Args:
            max_chunk_size: Maximum number of sentences per chunk (default 10, max 10)

        Returns:
            List of text chunks preserving semantic boundaries where possible
        """
        if max_chunk_size <= 0 or max_chunk_size > 10:
            raise ValueError("max_chunk_size must be between 1 and 10")

        nltk_helpers.ensure_punkt()

        # Check if text has paragraph breaks
        if "\n\n" not in self.text_string:
            # Fall back to fixed-length chunking with max_chunk_size as sent_per_chunk
            return self.chunk_text(max_chunk_size)

        # Split on paragraph boundaries
        paragraphs = self.text_string.split("\n\n")
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        if not paragraphs:
            return []

        # Tokenize each paragraph into sentences
        paragraph_sentences: List[List[str]] = []
        for para in paragraphs:
            sentences = sent_tokenize(para)
            if sentences:
                paragraph_sentences.append(sentences)

        if not paragraph_sentences:
            return []

        # Merge paragraphs with < 2 sentences backward
        merged_paragraphs: List[List[str]] = []
        for para_sents in paragraph_sentences:
            if len(para_sents) < 2 and merged_paragraphs:
                # Merge backward: append to previous paragraph
                merged_paragraphs[-1].extend(para_sents)
            else:
                merged_paragraphs.append(para_sents)

        # Sub-chunk paragraphs that exceed max_chunk_size
        final_chunks: List[str] = []
        for para_sents in merged_paragraphs:
            if len(para_sents) <= max_chunk_size:
                # Paragraph fits within size limit
                chunk = " ".join(para_sents).strip()
                if chunk:
                    final_chunks.append(chunk)
            else:
                # Sub-chunk the paragraph
                for i in range(0, len(para_sents), max_chunk_size):
                    sub_chunk = " ".join(para_sents[i : i + max_chunk_size]).strip()
                    if sub_chunk:
                        final_chunks.append(sub_chunk)

        return final_chunks