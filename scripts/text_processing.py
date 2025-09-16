"""
1 Load spaCy and the English model
2 Read your extracted PDF text
3 Split it into sentences
4 Create metadata for each sentence
5 Save as JSONL format
"""
import spacy
model = spacy.load('en_core_web_sm')
import yaml
import logging
from pathlib import Path
from datetime import datetime

config_path = Path("configs/base.yaml")
with open(config_path, 'r') as file:
    # Converts to dictionary, so can index
    config = yaml.safe_load(file)

# How log messages should look
logging.basicConfig(
    # getattr(...) is same as setting level to logging.<level>
    level=getattr(logging, config['logging']['level']),
    format=config['logging']['format']
)

logger = logging.getLogger(__name__)

logger.info(f"Project: {config['name']}")
logger.info(f"Version: {config['version']}")
logger.info("Text Processing started!")

logger.debug(f"Extracting path to text file")
file_path = Path("data/experiments/pdf_extraction_20250915_173210.md")

if file_path.exists():
    with open(file_path, 'r', encoding='utf-8') as file:
        # Convert file content to string
        content = file.read()
        # Locate start of text in txt file using the -- First Page Text -- indicator which is added to our experiment output
        start = content.find("--- First Page Text ---")
        full_text = content[start + len("--- First Page Text ---")::].strip()
        logger.info(f"Full Text: {full_text}")



