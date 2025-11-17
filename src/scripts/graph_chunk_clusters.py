from cProfile import label
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
from pyvis.network import Network
from chunk_embed_map import ChunkEmbedder
from txt_cleaner import TextProcessor


net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

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

        embedder = ChunkEmbedder(chunks)
        chunk_map = embedder.ECM_chunks(4)

        for index, (key, value) in enumerate(chunk_map.items()):
            net.add_node(
                n_id=index, 
                group=f"Cluster {value}",
                title=key[:200] if len(key) > 200 else key
            )
        
        net.toggle_physics(True)
        net.repulsion(
            node_distance=300,
            central_gravity=0.1,
            spring_length=150,
            spring_strength=0.05,
            damping=0.9
        )
        net.show("chunk_map.html", notebook=False)