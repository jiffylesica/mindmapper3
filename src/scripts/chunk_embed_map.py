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
from txt_cleaner import TextProcessor
import cohere
import numpy as np
from sklearn.cluster import KMeans

co = cohere.ClientV2(api_key="VAGHyilKcZ3iUmJjtaxoH8fKcg80Fr3PECROjjBO")


class ChunkEmbedder:

    def __init__(self, chunks):
        self.chunks = chunks

    def embed_chunks(self):
        chunk_key_array = []
        embedding_value_list = []
        for i in range(0, len(self.chunks), 96):
            batch = self.chunks[i:i+96]
            res = co.embed(
                texts=batch,
                model="embed-v4.0",
                input_type="clustering",
                output_dimension=1024,
                embedding_types=["float"],
            )
            for chunk, embedding in zip(batch, res.embeddings.float):
                chunk_key_array.append(chunk)
                embedding_value_list.append(embedding)
        return chunk_key_array, np.array(embedding_value_list)
    
    def cluster_chunks(self, embeddings, num_cluster):
        return KMeans(n_clusters=num_cluster, random_state=0, n_init="auto").fit(embeddings).labels_
    
    def map_chunk_clusters(self, clusters, chunks):
        chunk_cluster_map = {}
        for i, chunk in enumerate(chunks):
            chunk_cluster_map[chunk] = clusters[i]
        
        return chunk_cluster_map

    def ECM_chunks(self, num_cluster):
        chunks, embeddings = self.embed_chunks()
        clusters = self.cluster_chunks(embeddings, num_cluster)
        return self.map_chunk_clusters(clusters, chunks)

        
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
                for key, value in chunk_map.items():
                    f.write(f"Chunk: {key[:150]} \nValue: {str(value)}\n\n")