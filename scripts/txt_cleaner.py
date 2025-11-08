import nltk
from nltk.tokenize import sent_tokenize
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
import re
import yaml
import logging
from pathlib import Path
from datetime import datetime


class TextProcessor:

    def __init__(self, text):
        self.text = text

    def clean_text(self):
        self.text = self.text.replace("\n", " ")

    def chunk_text(self, sent_per_chunk):
        chunks = []
        sentences = sent_tokenize(self.text)
        for i in range(0, len(sentences) - 1, sent_per_chunk):
            chunk = " ".join(sentences[i:i+sent_per_chunk]).strip()
            chunks.append(chunk)
        return chunks

if __name__ == "__main__":

    config_path = Path("configs/base.yaml")
    with open(config_path, 'r') as file:
        # Converts to dictionary, so can index
        config = yaml.safe_load(file)

    txt_path = Path("document_data/raw_txt/test.txt")

    # Open txt file as doc
    if txt_path.exists():
        with open(txt_path) as doc:
            doc = doc.read()
            tp = TextProcessor(doc)
            tp.clean_text()
            chunks = tp.chunk_text(1)

            # Write clean text to clean text directory
            clean_txt_dir = Path(config['data']['clean_txt_dir'])
            clean_txt_dir.mkdir(exist_ok=True)

            # Generate unique filename for script run
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = clean_txt_dir / f"clean_txt_{timestamp}.md"

            # Write clean text to new file
            with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Text Cleaning Report\n")
                    f.write(f"Timestamp: {timestamp}\n")
                    f.write(f"Source File: {txt_path}\n")
                    f.write("\n\n\n".join(chunks))
                    f.write(str(len(chunks)))