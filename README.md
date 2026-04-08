# MindMapper

An AI-powered tool to accelerate research workflows by transforming text documents into interactive knowledge maps. The application uses natural language processing (NLP) and machine learning to extract semantic relationships from text, creating visual graph representations that help users explore and understand document structure and key concepts.

**Technologies & Implementation**: Built with **Flask** REST API and **Gunicorn** WSGI server for web interface and processing orchestration. Implemented **Cohere Embed API** (embed-v4.0) for generating 1024-dimensional vector embeddings, **scikit-learn K-Means clustering** for semantic grouping, and **PyVis** for interactive network visualization. Utilized **NLTK** for sentence tokenization and **NumPy** for vector operations. Designed modular pipeline architecture with sequential processing stages (text cleaning → chunking → embedding → clustering → visualization).

**Containerization & Deployment**: Implemented **Docker multi-stage builds** (Python 3.11-slim) with non-root user security practices, reducing image size and optimizing production deployment. Orchestrated with **Kubernetes** manifests including Deployment (2 replicas with resource limits), LoadBalancer Service, ConfigMap for application configuration, and Secrets for API key management. Configured horizontal scaling and resource management for production workloads.

## Overview

MindMapper processes text documents through a multi-stage pipeline that:
1. **Cleans and chunks** text into semantically meaningful segments
2. **Embeds** text chunks using Cohere's embedding API to create vector representations
3. **Clusters** similar chunks using K-Means clustering
4. **Visualizes** the results as an interactive network graph using PyVis

The application provides a Flask-based web interface for uploading text files and viewing the generated knowledge maps, with support for containerized deployment using Docker and Kubernetes.

## Key Technologies & Dependencies

### Core Dependencies
- **Flask**: Web framework for the REST API and user interface
- **Cohere**: AI embedding service for generating semantic vector representations
- **scikit-learn**: Machine learning library for K-Means clustering
- **PyVis**: Interactive network visualization library
- **NLTK**: Natural language processing for sentence tokenization
- **NumPy**: Numerical computing for vector operations
- **Gunicorn**: Production WSGI server
- **python-dotenv**: Environment variable management

### Architecture Patterns
- **Pipeline Pattern**: Modular processing stages (cleaning → embedding → clustering → visualization)
- **REST API**: Flask-based endpoints for file upload and graph generation
- **Containerization**: Docker multi-stage builds for optimized image size
- **Orchestration**: Kubernetes manifests for scalable deployment

## Pipeline Processing Logic

The text-to-graph transformation follows a sequential pipeline architecture:

### Stage 1: Text Processing (`TextProcessor`)
- **Input**: Raw text string
- **Process**:
  - Normalizes whitespace (replaces newlines with spaces)
  - Tokenizes text into sentences using NLTK's `sent_tokenize`
  - Groups sentences into chunks based on `sent_per_chunk` parameter
- **Output**: List of text chunks (each chunk contains N sentences)

### Stage 2: Chunk Embedding (`ChunkEmbedder`)
- **Input**: List of text chunks
- **Process**:
  - Batches chunks (96 chunks per batch) for efficient API calls
  - Calls Cohere Embed API (`embed-v4.0` model) with:
    - `input_type="clustering"` for optimized clustering embeddings
    - `output_dimension=1024` for high-dimensional vectors
  - Validates embedding dimensions and batch consistency
  - Converts embeddings to NumPy matrix format
- **Output**: Embedding matrix (N chunks × 1024 dimensions)

### Stage 3: Clustering (`ChunkEmbedder.cluster_chunks`)
- **Input**: Embedding matrix, number of clusters
- **Process**:
  - Applies K-Means clustering algorithm (scikit-learn)
  - Validates cluster count against chunk count
  - Assigns each chunk to a cluster label
- **Output**: Cluster labels array (one label per chunk)

### Stage 4: Graph Visualization (`ChunkGraph`)
- **Input**: Dictionary mapping chunks to cluster IDs
- **Process**:
  - Creates network graph using PyVis
  - Implements cluster hub architecture:
    - Each cluster has a central "hub" node (diamond shape)
    - Chunk nodes connect to their cluster hub
  - Applies force-directed layout (ForceAtlas2) for optimal positioning
  - Color-codes nodes by cluster membership
  - Injects interactive modal for viewing full chunk text on click
- **Output**: Interactive HTML graph file

### Pipeline Flow Diagram
```
Text File → TextProcessor → Chunks → ChunkEmbedder → Embeddings → 
K-Means Clustering → Cluster Map → ChunkGraph → Interactive HTML Graph
```

## Containerization Framework

### Docker Implementation

The project uses a **multi-stage Docker build** to optimize image size and security:

#### Stage 1: Builder
- Base image: `python:3.11-slim`
- Installs dependencies from `pyproject.toml`
- Builds the package in editable mode (`pip install -e .`)

#### Stage 2: Runtime
- Base image: `python:3.11-slim` (fresh, minimal)
- Copies only installed packages from builder stage
- Sets up non-root user (`appuser`) for security
- Configures Flask application via environment variables
- Exposes port 5000
- Runs Gunicorn with 2 workers for production

#### Key Docker Features
- **Multi-stage build**: Reduces final image size by excluding build tools
- **Non-root user**: Enhances security by running as unprivileged user
- **Production server**: Uses Gunicorn instead of Flask's development server
- **Environment configuration**: Supports environment-based configuration

### Kubernetes Deployment

The Kubernetes manifests provide a complete deployment setup:

#### Components

1. **Deployment** (`k8s/deployment.yaml`)
   - Runs 2 replicas for high availability
   - Container image: `jiffylesica/mindmapper:latest`
   - Resource limits: 1Gi memory, 500m CPU
   - Resource requests: 512Mi memory, 250m CPU
   - Environment variables:
     - `COHERE_API_KEY`: Injected from Kubernetes Secret
   - Port: 8080 (container)

2. **Service** (`k8s/service.yaml`)
   - Type: `LoadBalancer` (exposes to internet)
   - Maps external port 80 to container port 8080
   - Load balances traffic across pod replicas

3. **ConfigMap** (`k8s/configmap.yaml`)
   - Stores non-sensitive configuration:
     - `FLASK_ENV`: Production mode
     - `SENT_PER_CHUNK`: Sentences per chunk (4)
     - `NUM_CLUSTERS`: Number of clusters (3)

4. **Secret** (`k8s/secret.yaml`)
   - Stores sensitive data (Cohere API key)
   - Referenced by Deployment via `secretKeyRef`

#### Deployment Strategy
- **Horizontal scaling**: Multiple replicas for load distribution
- **Resource management**: CPU and memory limits prevent resource exhaustion
- **Configuration separation**: Secrets vs. ConfigMaps for security best practices
- **Service discovery**: Kubernetes Service provides stable endpoint

## Getting Started

### Prerequisites
- Python 3.10+
- Cohere API key
- Docker (for containerized deployment)
- Kubernetes cluster (for orchestration)

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -e .
   ```

2. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```
   COHERE_API_KEY=your_api_key_here
   ```

3. **Run the Flask application**:
   ```bash
   cd src/mindmapper/web
   python app.py
   ```

4. **Access the web interface**:
   Navigate to `http://localhost:8080` and upload a `.txt` file

### Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t mindmapper:latest .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8080:8080 -e COHERE_API_KEY=your_key mindmapper:latest
   ```

### Kubernetes Deployment

1. **Create the secret**:
   ```bash
   kubectl create secret generic mindmapper-secrets \
     --from-literal=cohere-api-key=your_api_key
   ```

2. **Apply manifests**:
   ```bash
   kubectl apply -f k8s/
   ```

3. **Access the service**:
   - For LoadBalancer: Get external IP from `kubectl get svc`
   - For ClusterIP: Use port-forward: `kubectl port-forward svc/mindmapper-service 8080:80`

## Project Structure

```
mindmapper3/
├── src/
│   └── mindmapper/
│       ├── cleaning/          # Text processing and chunking
│       ├── embedding/         # Cohere API integration and clustering
│       ├── visualizing/       # Graph generation with PyVis
│       └── web/               # Flask application
├── k8s/                       # Kubernetes manifests
├── Dockerfile                 # Multi-stage Docker build
├── pyproject.toml             # Python package configuration
└── README.md                  # This file
```

## Configuration

### Environment Variables
- `COHERE_API_KEY`: Required. Your Cohere API key for embeddings
- `FLASK_ENV`: Flask environment (development/production)
- `SENT_PER_CHUNK`: Number of sentences per chunk (default: 4)
- `NUM_CLUSTERS`: Number of clusters for K-Means (default: 3)

### Pipeline Parameters
- `sent_per_chunk`: Controls chunk granularity (higher = larger chunks)
- `num_clusters`: Controls graph structure (higher = more distinct groups)

