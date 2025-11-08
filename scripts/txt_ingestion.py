import yaml
import logging
from pathlib import Path
from datetime import datetime

config_path = Path("configs/base.yaml")
with open(config_path, 'r') as file:
    # Converts to dictionary, so can index
    config = yaml.safe_load(file)

txt_path = Path("document_data/raw_txt/test.txt")

# Open txt file as doc
if txt_path.exists():
    with open(txt_path) as doc:
        doc_as_str = doc.read().replace("\n", "")
        # FURTHER TXT CLEANING HERE

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
                f.write(doc_as_str)

