# src/mindmapper/pipeline.py
from pathlib import Path
from mindmapper.cleaning.TextProcessor import TextProcessor
from mindmapper.embedding.ChunkEmbedder import ChunkEmbedder
from mindmapper.visualizing.ChunkGraph import ChunkGraph

class TextToGraphPipeline:
    def __init__(self, graph_output_dir: Path | None = None):
        self.text_processor = TextProcessor()
        self.chunk_embedder = ChunkEmbedder()
        self.chunk_graph = ChunkGraph(output_dir=graph_output_dir)

    def run_pipeline_from_text(
        self,
        text: str,
        sent_per_chunk: int,
        num_clusters: int,
        output_filename: str = "chunk_map.html",
    ) -> Path:
        self.text_processor.text_string = text
        self.text_processor.clean_text()
        chunks = self.text_processor.chunk_text(sent_per_chunk)

        self.chunk_embedder.chunks = chunks
        graph_map = self.chunk_embedder.build_cluster_map(num_clusters)

        self.chunk_graph.chunk_map = graph_map
        output_path = self.chunk_graph.create_graph(output_filename=output_filename)
        return output_path