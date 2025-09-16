import yaml
import logging
from pathlib import Path
from datetime import datetime

config_path = Path("configs/base.yaml")
with open(config_path, 'r') as file:
    # Converts to dictionary, so can index
    config = yaml.safe_load(file)

# Simple test to see if config loaded correctly
print(f"Project: {config['name']}")
print(f"Version: {config['version']}")

# How log messages should look
logging.basicConfig(
    # getattr(...) is same as setting level to logging.<level>
    level=getattr(logging, config['logging']['level']),
    format=config['logging']['format']
)

# Create a logger
logger = logging.getLogger(__name__)

# Test logging
logger.info("Hello Pipeline started!")
logger.info(f"Project: {config['name']}")
logger.info(f"Version: {config['version']}")

# Directory health check --> validate project structure
# Check if directories exist, count files in each, log results
# Check data directories
logger.info("Checking project structure...")

data_dirs = [
    config['data']['raw_pdfs_dir'],
    config['data']['interim_text'],
    config['data']['processed'],
    config['data']['experiments']
]

for dir_path in data_dirs:
    path = Path(dir_path)
    if path.exists():
        file_count = len(list(path.glob('*')))
        logger.info(f"✓ {dir_path}: {file_count} files")
    else:
        logger.warning(f"✗ {dir_path}: Directory not found")

# Create experiment log
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
experiment_dir = Path(config['data']['experiments'])
experiment_dir.mkdir(exist_ok=True)

log_file = experiment_dir / f"hello_pipeline_{timestamp}.log"
logger.info(f"Experiment log: {log_file}")