# src/mindmapper/pipeline.py
from collections import defaultdict
from pathlib import Path
from mindmapper.cleaning.TextProcessor import TextProcessor, CHUNKING_STRATEGY_FIXED, CHUNKING_STRATEGY_HIERARCHICAL
from mindmapper.embedding.ChunkEmbedder import ChunkEmbedder
from mindmapper.summarizing import ClusterSummarizer
from mindmapper.visualizing.ChunkGraph import ChunkGraph

class TextToGraphPipeline:
    def __init__(self, graph_output_dir: Path | None = None):
        self.text_processor = TextProcessor()
        self.chunk_embedder = ChunkEmbedder()
        self.cluster_summarizer = ClusterSummarizer()
        self.chunk_graph = ChunkGraph(output_dir=graph_output_dir)

    def run_pipeline_from_text(
        self,
        text: str,
        sent_per_chunk: int = 4,
        num_clusters: int = 3,
        output_filename: str = "chunk_map.html",
        chunking_strategy: str = CHUNKING_STRATEGY_FIXED,
        max_chunk_size: int | None = None,
    ) -> Path:
        """
        Run the full text-to-graph pipeline.

        Args:
            text: Raw text to process
            sent_per_chunk: Sentences per chunk for fixed-length strategy (default 4)
            num_clusters: Number of clusters for K-means (default 3)
            output_filename: Output HTML filename (default "chunk_map.html")
            chunking_strategy: Either "fixed" or "hierarchical" (default "fixed")
            max_chunk_size: Max sentences per chunk for hierarchical strategy (1-10, default 10)

        Returns:
            Path to generated graph HTML file
        """
        self.text_processor.text_string = text
        self.text_processor.clean_text()

        # Select chunking strategy
        if chunking_strategy == CHUNKING_STRATEGY_HIERARCHICAL:
            if max_chunk_size is None:
                max_chunk_size = 10
            chunks = self.text_processor.chunk_text_hierarchical(max_chunk_size)
        else:
            chunks = self.text_processor.chunk_text(sent_per_chunk)

        self.chunk_embedder.chunks = chunks
        assignments = self.chunk_embedder.build_cluster_assignments(num_clusters)

        cluster_chunks: dict[int, list[str]] = defaultdict(list)
        for assignment in assignments:
            cluster_chunks[assignment.cluster_id].append(assignment.text)

        cluster_summaries = self.cluster_summarizer.summarize_clusters(dict(cluster_chunks))

        self.chunk_graph.chunk_assignments = assignments
        self.chunk_graph.cluster_summaries = cluster_summaries
        self.chunk_graph.chunk_map = {
            assignment.text: assignment.cluster_id for assignment in assignments
        }
        output_path = self.chunk_graph.create_graph(output_filename=output_filename)
        return output_path