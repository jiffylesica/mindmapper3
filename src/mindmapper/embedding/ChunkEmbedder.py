import cohere
import numpy as np
from dataclasses import dataclass
from sklearn.cluster import KMeans
from utils.env_get_helper import get_env_var

COHERE_API_KEY_ENV = "COHERE_API_KEY"
BATCH_SIZE = 96
MODEL_NAME = "embed-v4.0"
OUTPUT_DIM = 1024
EMBED_TYPES = ["float"]


@dataclass(frozen=True)
class ChunkAssignment:
    chunk_id: int
    text: str
    cluster_id: int

class ChunkEmbedder:
    
    def __init__(self):
        self._chunks: list[str] = []
        self.co = cohere.ClientV2(api_key=get_env_var(COHERE_API_KEY_ENV))
    
    @property
    def chunks(self) -> list[str]:
        return self._chunks

    @chunks.setter
    def chunks(self, value: list[str]) -> None:
        if not isinstance(value, list):
            raise TypeError("chunks must be a list")
        # Ensure every chunk is a string before storing
        if any(not isinstance(c, str) for c in value):
            raise TypeError("elements of chunk list must be strings")
        self._chunks = value

    def embed_chunks(self):
        # Guard against embedding with no data
        if not self.chunks:
            raise ValueError("Chunks must not be empty before embedding")

        chunk_key_array: list[str] = []
        embedding_value_list: list[list[float]] = []

        for i in range(0, len(self.chunks), BATCH_SIZE):
            batch = self.chunks[i:i+BATCH_SIZE]
            res = self.co.embed(
                texts=batch,
                model=MODEL_NAME,
                input_type="clustering",
                output_dimension=OUTPUT_DIM,
                embedding_types=EMBED_TYPES,
            )
            # Validating embedding results
            vectors = res.embeddings.float
            # Confirm the API returned vectors for this batch
            if not vectors:
                raise RuntimeError("Cohere returned no embeddings")

            for chunk, embedding in zip(batch, res.embeddings.float):
                # Verify each embedding matches the expected dimensionality
                if len(embedding) != OUTPUT_DIM:
                    raise ValueError(
                        f"Expected embedding length {OUTPUT_DIM}, got {len(embedding)}"
                    )
                chunk_key_array.append(chunk)
                embedding_value_list.append(embedding)

        matrix = np.array(embedding_value_list)
        # Fail fast if no vectors made it into the matrix
        if matrix.size == 0:
            raise RuntimeError("No embeddings were produced across all batches")
        # Double-check the final matrix has the desired width
        if matrix.shape[1] != OUTPUT_DIM:
            raise ValueError(f"Expected dimension {OUTPUT_DIM}, got {matrix.shape[1]}")

        return chunk_key_array, matrix
    
    def cluster_chunks(self, embeddings, num_cluster):
        # Ensure requested cluster count is within valid bounds
        if num_cluster <= 0 or num_cluster > len(self.chunks):
            raise ValueError(
                "num_cluster must be a positive integer not exceeding the number of chunks"
            )
        # Confirm embeddings form a 2-D matrix
        if embeddings.ndim != 2:
            raise ValueError(f"Embeddings must be 2-D; got ndim={embeddings.ndim}")
        # Guarantee we have one embedding per chunk
        if embeddings.shape[0] != len(self.chunks):
            raise ValueError(
                "Number of embedding vectors must match number of chunks "
                f"({embeddings.shape[0]} vs {len(self.chunks)})"
            )

        return KMeans(n_clusters=num_cluster, random_state=0, n_init="auto").fit(embeddings).labels_
    
    def map_chunk_clusters(self, clusters, chunks) -> list[ChunkAssignment]:
        # Chunks and labels must align before mapping
        if len(clusters) != len(chunks):
            raise ValueError("Clusters and chunks must align 1:1")

        assignments: list[ChunkAssignment] = []
        for chunk_id, (chunk, cluster_id) in enumerate(zip(chunks, clusters)):
            assignments.append(
                ChunkAssignment(
                    chunk_id=chunk_id,
                    text=chunk,
                    cluster_id=int(cluster_id),
                )
            )
        return assignments

    def build_cluster_assignments(self, num_cluster: int) -> list[ChunkAssignment]:
        chunks, embeddings = self.embed_chunks()
        clusters = self.cluster_chunks(embeddings, num_cluster)
        return self.map_chunk_clusters(clusters, chunks)

    def build_cluster_map(self, num_cluster):
        assignments = self.build_cluster_assignments(num_cluster)
        return {assignment.text: assignment.cluster_id for assignment in assignments}