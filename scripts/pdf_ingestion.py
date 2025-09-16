import yaml
import logging
from pathlib import Path
from datetime import datetime
import fitz

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

logger.info("PDF Ingestion started!")
logger.info(f"Project: {config['name']}")
logger.info(f"Version: {config['version']}")

pdf_path = Path("data/raw_pdfs/test.pdf")

# Open pdf as document

if pdf_path.exists():
    logger.info("Opening PDF")
    doc = fitz.open(pdf_path)
    if doc.page_count > 0:
        page1 = doc[0].get_text()
        if len(page1) > 0:
            logger.info(f"Number of PDF Pages: {doc.page_count}")
            logger.info(f"Length of Page 1: {len(page1)}")
            logger.info(f"First 200 Words: {page1[:200]}...")
            # Create Output Directory
            experiment_dir = Path(config['data']['experiments'])
            experiment_dir.mkdir(exist_ok=True)

            # Generate unique filename for script run
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = experiment_dir / f"pdf_extraction_{timestamp}.md"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"PDF Extraction Report\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Source File: {pdf_path}\n")
                f.write(f"Pages: {doc.page_count}\n")
                f.write(f"First Page Text Length: {len(page1)}\n")
                f.write(f"\n--- First Page Text ---\n")
                f.write(page1)
        else:
            logger.warning("First page has no text")
    else:
        logger.warning("PDF Ingestion Failed - PDF is pageless or lacking text")

    # Close PDF
    doc.close()
    logger.info("PDF Closed")
else:
    logger.warning("PDF Ingestion Failed - Path Does Not Exist")

