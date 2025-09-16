# MindMapper 2.0 — ML-Powered Concept Hierarchies + Summaries

*A tutorial-style roadmap for building an end-to-end, learning-focused ML/NLP system on top of your existing MindMapper project (PDF → interactive mind map). This guide is written for you to upload to Cursor AI. It emphasizes hands-on learning of each layer of the stack. It **intentionally avoids code** and instead provides step-by-step instructions, decisions, and checkpoints. Ask for code snippets only when you want them.*

---

## How to Use This Guide
- **Audience:** You, the developer, who wants to learn by implementing every layer: parsing, NLP, embeddings, clustering, summarization, graph modeling, serving, and UI.
- **Style:** Tutorial-style, step-by-step. Each phase includes: *what you'll build*, *what you'll learn*, *key design decisions*, *deliverables*, and *checkpoints*.
- **No code unless requested:** This guide describes implementation steps precisely but leaves out code so you can practice and build muscle memory. When you want code, ask for it specifically.
- **Tooling-agnostic:** Concrete tool names are suggested (e.g., PyMuPDF, spaCy, Hugging Face), but you're encouraged to compare alternatives and document your choices.

## Development Environment & Status

**Current Setup (Updated: September 15, 2025)**
- **Conda Environment:** `mindmapper2` (Python 3.9+)
- **Development Approach:** Agile, tutorial-style learning with incremental builds
- **Current Phase:** Phase 2 (Text Normalization & Metadata) - In Progress

**Installed Dependencies:**
- **PyMuPDF (fitz)** - PDF text extraction and processing
- **spaCy** - NLP processing and sentence segmentation
- **en_core_web_sm** - spaCy English language model
- **PyYAML** - Configuration file handling
- **pathlib** - Modern file path handling

**Completed Tasks:**
- ✅ **Phase 0:** Environment setup, project structure, configuration system, logging
- ✅ **Phase 1:** PDF ingestion pipeline with PyMuPDF, text extraction, metadata tracking
- 🔄 **Phase 2:** Text processing with spaCy (currently working on sentence segmentation)

**Project Structure (Implemented):**
```
mindmapper2/
├── configs/
│   └── base.yaml                 # ✅ Complete - logging, paths, metadata
├── data/
│   ├── raw_pdfs/                 # ✅ Ready for PDF files
│   ├── interim_text/             # ✅ Ready for processed text
│   ├── processed_graphs/         # ✅ Ready for final outputs
│   └── experiments/              # ✅ Active - contains extraction results
├── scripts/
│   ├── hello_pipeline.py         # ✅ Complete - validates setup
│   ├── pdf_ingestion.py          # ✅ Complete - extracts PDF text
│   └── text_processing.py        # 🔄 In Progress - sentence segmentation
└── docs/                         # ✅ Structure ready
```

**Current Sprint Goal:** Complete text processing pipeline to convert extracted PDF text into clean, segmented sentences with metadata for ML processing.

---

## Project Overview

**Goal:** Upgrade MindMapper from “extract concepts and draw a flat graph” to a **machine-learning system** that:
1. Builds **semantic embeddings** for text spans.
2. **Clusters** related spans into **topics** and organizes them into a **hierarchy** (parent/child).
3. Generates **summary nodes** for clusters and subclusters (extractive and/or abstractive).
4. Merges multiple PDFs into a **cross-document knowledge graph**.
5. Serves results via an **API** and visualizes them in **Cytoscape.js**.

**Why this is valuable:** You’ll cover the key competencies of modern ML systems—data processing, representation learning (embeddings), unsupervised structure discovery (clustering, topic modeling), summarization, graph modeling, evaluation, and deployment.

---

## Learning Objectives
- **NLP preprocessing:** tokenization, sentence/section segmentation, metadata management.
- **Embeddings:** sentence-level embeddings, dimensionality reduction, vector indexing.
- **Unsupervised learning:** hierarchical clustering, topic modeling, selection of cluster representatives.
- **Summarization:** extractive (graph/ranking) and abstractive (seq2seq) approaches.
- **Graph thinking:** schema for nodes/edges, graph storage, and traversal.
- **MLOps-lite:** experiment logging, configs, dataset/version control, reproducibility.
- **Productization:** clean data contracts, minimal API, and a usable frontend.

---

## High-Level System Diagram (Conceptual)
1. **Ingestion:** PDFs → pages → sections → sentences (+ metadata).
2. **Representation:** text spans → embeddings.
3. **Structure:** clustering → topic hierarchy (parent/child) → label generation.
4. **Summaries:** extractive + abstractive summaries for each cluster.
5. **Graph:** build nodes/edges; store results.
6. **Serving & UI:** FastAPI (or similar) → React/Cytoscape.js visualization and controls.

---

## Suggested Repository Structure
*(Use this as a guide—adjust as needed.)*
```
mindmapper2/
  README.md
  LICENSE
  pyproject.toml / requirements.txt
  configs/
    base.yaml
    embeddings.yaml
    clustering.yaml
    summarization.yaml
  data/
    raw_pdfs/
    interim_text/
    processed_graphs/
    experiments/
  docs/
    design/
    decisions/
    glossary.md
  src/
    ingestion/            # PDF parsing, segmentation
    nlp/                  # tokenization, cleaning, NER
    embeddings/           # sentence/paragraph encoders
    clustering/           # hierarchical, topic models
    summarization/        # extractive & abstractive
    graph/                # schema, builders, exporters
    api/                  # FastAPI endpoints
    ui/                   # integration helpers for frontend
    utils/                # logging, configs, metrics
  tests/
  scripts/                # run pipelines, evals
```

---

# Phase 0 — Environment & Project Scaffolding ✅ COMPLETE

**What you built**
- A clean Python environment with reproducible dependency management.
- Config-driven project (centralized settings for models, hyperparameters, paths).
- Basic logging and experiment tracking.

**What you learned**
- Why reproducibility matters: same inputs → same outputs.
- How configs decouple code from settings.
- Agile development approach with incremental builds.

**Decisions Made**
- **Environment manager:** conda (mindmapper2 environment)
- **Config system:** simple YAML files with PyYAML
- **Experiment tracking:** Markdown files with timestamps
- **Development approach:** Tutorial-style, step-by-step learning

**Deliverables Completed**
- ✅ `configs/base.yaml` with logging, paths, and metadata settings
- ✅ Project structure with organized directories
- ✅ `scripts/hello_pipeline.py` - validates setup, loads configs, checks directories

**Checkpoints Passed**
- ✅ Environment setup and validation working
- ✅ Config loading and logging system functional
- ✅ Project structure validated and organized

---

# Phase 1 — PDF Ingestion & Parsing ✅ COMPLETE

**What you built**
- A robust PDF processing pipeline that converts PDFs into structured text with metadata.

**What you learned**
- PDF text extraction with PyMuPDF; handling complex academic documents
- Error handling and resource management for file processing
- Metadata tracking and experiment logging

**Steps Completed**
1. ✅ **PDF Library Selection:** PyMuPDF (fitz) for robust text extraction
2. ✅ **Text Extraction:** Successfully extracts text from PDF pages
3. ✅ **Error Handling:** Handles missing files, empty pages, no text scenarios
4. ✅ **Metadata Tracking:** Logs page count, text length, extraction details
5. ✅ **Output Generation:** Creates timestamped experiment reports

**Decisions Made**
- **PDF Library:** PyMuPDF for accuracy and reliability across content types
- **Output Format:** Markdown reports with structured metadata
- **Error Handling:** Comprehensive validation and logging
- **Resource Management:** Proper file closing and memory management

**Deliverables Completed**
- ✅ `scripts/pdf_ingestion.py` - complete PDF processing pipeline
- ✅ `data/experiments/pdf_extraction_*.md` - timestamped extraction reports
- ✅ Successfully processed 49-page academic paper on Christian mysticism

**Checkpoints Passed**
- ✅ PDF text extraction working reliably
- ✅ Error handling covers edge cases
- ✅ Metadata tracking provides useful information
- ✅ Experiment logging creates reproducible records

---

# Phase 2 — Text Normalization & Metadata 🔄 IN PROGRESS

**What you're building**
- A text processing pipeline that converts raw PDF text into clean, segmented sentences with metadata.

**What you're learning**
- spaCy for sentence segmentation and NLP processing
- JSONL format for ML data storage
- Metadata management for tracking text sources

**Steps Completed**
1. ✅ **spaCy Setup:** Installed spaCy and en_core_web_sm language model
2. ✅ **Text Extraction:** Successfully reads extracted PDF text from experiment files
3. ✅ **File Processing:** Handles file reading, text extraction, and error cases
4. 🔄 **Sentence Segmentation:** Currently implementing spaCy text processing
5. ⏳ **Metadata Creation:** Next - create structured metadata for each sentence
6. ⏳ **JSONL Output:** Next - save processed data in JSONL format

**Current Progress**
- **Script:** `scripts/text_processing.py` - foundation complete, working on spaCy integration
- **Input:** Successfully extracts text from `pdf_extraction_20250915_173210.md`
- **Next:** Process text with spaCy to get individual sentences with metadata

**Decisions Made**
- **NLP Library:** spaCy for production-ready sentence segmentation
- **Input Source:** PDF extraction files from Phase 1 experiments
- **Development Approach:** Tutorial-style learning with incremental implementation

**Deliverables (In Progress)**
- 🔄 `scripts/text_processing.py` - text processing pipeline
- ⏳ `data/interim_text/*.jsonl` - segmented sentences with metadata
- ⏳ Processing report with sentence counts and quality metrics

**Next Steps**
- Complete spaCy text processing integration
- Implement sentence metadata creation
- Output structured JSONL format
- Test with extracted academic paper text

---

# Phase 3 — Concept Candidates (Optional but Useful)

**What you’ll build**
- A first pass at surface-level “concept candidates” (keyphrases).

**What you’ll learn**
- Keyword/keyphrase extraction as a complement to embeddings-based clustering.

**Steps**
1. Use noun-phrase chunks or statistical keyphrase candidates.
2. Keep a mapping: span_id → {text, keyphrases[], POS info}.

**Decisions**
- Whether to use keyphrases later to label clusters and to assist summarization prompts/extractive ranking.

**Deliverables**
- `concept_candidates.jsonl` per document.
- Doc notes on precision vs. recall of candidates.

**Checkpoints**
- Manual inspection: are candidates sensible? Too generic? Too noisy?

---

# Phase 4 — Embeddings (Representation Learning)

**What you’ll build**
- Sentence/paragraph embeddings for your text spans.

**What you’ll learn**
- How embedding models convert text into dense vectors capturing semantic similarity.

**Steps**
1. Choose a sentence-transformer (baseline first). Document the model name and version.
2. Batch-encode spans (deterministic order). Save vectors with IDs.
3. Optionally reduce dimensionality for visualization (e.g., UMAP) while keeping full vectors for clustering.

**Decisions**
- Model family (general-purpose vs. scientific domain).
- Storage format for vectors (NumPy arrays + index, or a vector DB).

**Deliverables**
- `embeddings/{doc_id}.npy` (or similar) + index mapping (span_id → row).
- `docs/decisions/embeddings.md` justifying your choice and any normalization (L2, mean-centering).

**Checkpoints**
- Quick nearest-neighbor sanity tests: similar sentences should be close.

---

# Phase 5 — Clustering (Discovering Topics)

**What you’ll build**
- Groups of semantically similar spans that represent latent topics.

**What you’ll learn**
- Differences between flat clustering (k-means, HDBSCAN) and hierarchical clustering (agglomerative).

**Steps**
1. Start with a **flat** method (e.g., k-means or HDBSCAN) to gauge clusterability.
2. Move to **hierarchical agglomerative clustering** to build dendrograms.
3. Decide how to cut the dendrogram into levels to form a **topic hierarchy** (see Phase 6).

**Decisions**
- Distance metric (cosine distance is standard for embeddings).
- Whether to use density-based clustering (HDBSCAN) to handle noise/outliers.
- Cluster size constraints and min_samples (to avoid singletons dominating).

**Deliverables**
- `clustering/{doc_id}/clusters.json` containing cluster assignments for all spans.
- Visual diagnostics (cluster size distribution, silhouette scores where applicable).

**Checkpoints**
- Manual review of clusters: do grouped spans feel topically coherent?

---

# Phase 6 — Hierarchy Construction (Parent/Child Topics)

**What you’ll build**
- A **multi-level topic hierarchy** (root → major themes → subthemes).

**What you’ll learn**
- How to convert a dendrogram or hierarchical linkage into a usable tree.

**Steps**
1. From agglomerative clustering, obtain a linkage matrix (conceptual artifact).
2. Define **cut thresholds** to create multiple levels (e.g., 2–4 depths).
3. For each node (cluster), compute **representatives** (top spans or keyphrases) for labeling.
4. Build deterministic parent/child relationships; store as a tree structure.

**Decisions**
- How many levels to expose in the UI.
- Labeling strategy: keyphrases, TF‑IDF terms from the cluster, or centroid-nearest spans.
- Handling orphans/outliers (assign to “Misc/Other” or keep as leaves).

**Deliverables**
- `hierarchy/{doc_id}/tree.json` with nodes including: id, level, label, member span_ids, parent_id.
- A short document explaining your cut strategy and alternatives.

**Checkpoints**
- Inspect a few branches end-to-end: do children feel like specializations of their parent?

---

# Phase 7 — Summarization Nodes (Extractive + Abstractive)

**What you’ll build**
- Summaries for each cluster/hierarchy node; optionally both extractive and abstractive.

**What you’ll learn**
- How to produce and evaluate summaries; trade-offs between speed and quality.

**Steps**
1. **Extractive baseline:** rank member spans (e.g., graph-based centrality) and select the top N sentences.
2. **Abstractive upgrade:** fine-tune or prompt a seq2seq model to generate concise summaries from the cluster’s spans.
3. Store both forms; allow toggling in the UI.

**Decisions**
- Target length (sentences/words).
- Whether to use keyphrases as guidance in prompts (if applicable).
- Domain specificity of the summarizer (general vs. scientific).

**Deliverables**
- `summaries/{doc_id}/node_{id}.json` containing extractive, abstractive, and metadata (input tokens count, etc.).
- `docs/decisions/summarization.md` detailing choices and constraints (latency, context window).

**Checkpoints**
- Human spot checks: faithfulness (no hallucinations), coverage of key points, redundancy levels.

---

# Phase 8 — Cross-Document Merging & Entity Linking

**What you’ll build**
- A unified knowledge graph across multiple PDFs, with shared topics and entities merged.

**What you’ll learn**
- Entity linking, cross-document co-reference, and graph consolidation.

**Steps**
1. Run NER/entity linking (general or scientific) to canonicalize entities (e.g., “BERT,” “Bidirectional Encoder…”).
2. Pool embeddings across documents; align clusters across docs via centroid similarity.
3. Create **cross-doc edges** for shared concepts/topics; optionally compute overlap metrics.

**Decisions**
- Thresholds for considering two clusters “the same concept.”
- Disambiguation strategies for near-duplicates.

**Deliverables**
- `crossdoc/graph.json` with merged nodes and cross-document edges.
- A report describing merge criteria and examples (true merges vs. false merges).

**Checkpoints**
- Validate a handful of merges manually; adjust thresholds as needed.

---

# Phase 9 — Graph Construction & Storage

**What you’ll build**
- A graph representation you can query and render.

**What you’ll learn**
- Schema design for graph data: node/edge types and attributes.

**Steps**
1. Define **node types:** `Document`, `Section`, `Span`, `ConceptCluster`, `Summary`.
2. Define **edge types:** `MENTIONS`, `BELONGS_TO`, `PARENT_OF`, `SIMILAR_TO`, `ALIGNED_WITH` (cross-doc).
3. Choose storage: JSON files + indices, a property graph (e.g., Neo4j), or relational (Postgres with JSONB).
4. Implement exporters that write consistent, versioned artifacts.

**Decisions**
- Trade-offs: simplicity (JSON) vs. query power (graph DB) vs. familiarity (Postgres).

**Deliverables**
- `graph/graph_export.json` (and/or DB load scripts you create later).
- `docs/design/graph_schema.md` with schema diagrams and examples.

**Checkpoints**
- Load a small sample into your UI and verify nodes/edges are consistent and navigable.

---

# Phase 10 — Evaluation & Experiments

**What you’ll build**
- A structured evaluation plan with both quantitative and qualitative metrics.

**What you’ll learn**
- How to evaluate unsupervised NLP and summarization meaningfully.

**Clustering/Hierarchy Metrics (quantitative)**
- **Internal:** silhouette coefficient (if applicable), cluster size variance, cohesion (avg intra-cluster distance).
- **Stability:** how cluster assignments change with small perturbations.
- **Coverage:** fraction of spans assigned to non-noise clusters.

**Summarization Metrics (automated)**
- **Extractive:** redundancy %, coverage % of keyphrases.
- **Abstractive:** ROUGE/BERTScore (interpret cautiously).

**Human Evaluation (qualitative)**
- **Coherence:** do cluster members belong together?
- **Label Fit:** does the node label accurately name the topic?
- **Summary Faithfulness and Usefulness:** concise, non-hallucinated, covers the main idea.

**Deliverables**
- `experiments/{date}/metrics.json` and a short Markdown write-up with findings and next steps.

**Checkpoints**
- Use small ablation studies: model A vs. B, with clear winner criteria you define.

---

# Phase 11 — Minimal API (Serving Layer)

**What you’ll build**
- A small service that exposes the graph and summaries.

**What you’ll learn**
- Data contracts, pagination, filtering, and reproducibility of served artifacts.

**Steps**
1. Define response schemas (e.g., `/documents`, `/graph?doc_id=…`, `/node?id=…`).
2. Serve precomputed artifacts (no on-the-fly heavy compute for v1).
3. Add versioning (e.g., `artifact_version`) to responses.

**Decisions**
- Authentication (optional for local dev).
- Caching strategy for frequently accessed nodes.

**Deliverables**
- API specification in `docs/design/api_contract.md` and a working local server you implement.

**Checkpoints**
- Fetch a document’s graph in the frontend successfully, confirm IDs match stored artifacts.

---

# Phase 12 — Frontend Integration (Cytoscape.js)

**What you’ll build**
- A navigable, layered mind map that reflects the learned hierarchy and summaries.

**What you’ll learn**
- Hierarchical UI patterns; performance considerations for large graphs.

**Features to Implement**
1. **Level controls:** toggle depth (e.g., show only level ≤ 2).
2. **Node panels:** show extractive/abstractive summary, top member spans, keyphrases.
3. **Search & filter:** find entities, collapse/expand subtrees.
4. **Cross-doc mode:** highlight nodes shared across documents.
5. **Hover previews:** show representative sentences without expanding.

**Deliverables**
- A working UI where you can upload multiple PDFs and explore the merged graph.

**Checkpoints**
- Performance acceptable on mid-size document sets; no broken links or orphaned nodes in UI.

---

# Phase 13 — MLOps & Reproducibility (Lightweight)

**What you’ll build**
- Processes that make your work repeatable and shareable.

**What you’ll learn**
- Why configs, logs, and data versioning are essential for ML projects.

**Steps**
1. Keep every model choice and hyperparameter in configs.
2. Save **intermediate artifacts** (text, embeddings, clusters, summaries).
3. Record experiment results and decisions (what worked, what didn’t, and why).
4. Optional: dataset tracking (e.g., DVC or a simple checksum system).

**Deliverables**
- `docs/decisions/*.md` and `experiments/` history that tells the story of your iterations.

**Checkpoints**
- A collaborator could reproduce your last run from scratch using the repo and configs.

---

# Phase 14 — Extensions & Next Steps

**Ideas**
- **Graph ML:** Train node embeddings (e.g., Node2Vec) to recommend related concepts not explicitly connected.
- **Temporal Evolution:** Add a time dimension to see topics changing across publication years.
- **Interactive Summarization:** Let users select subgraphs and generate a custom summary.
- **Retrieval-Augmented Reading:** Query the graph + text to answer questions with citations.
- **Evaluation Benchmarks:** Create a tiny gold set (manually labeled clusters) to measure progress over time.

---

## Definitions (Glossary)
- **Embedding:** A numeric vector representation of text that captures semantic meaning; similar texts have similar vectors.
- **Cosine Similarity/Distance:** A measure of how similar two vectors are based on the angle between them.
- **Clustering:** Grouping data points so that points in a group are more similar to each other than to those in other groups.
- **Hierarchical Clustering:** A method that builds a tree (dendrogram) of clusters by iteratively merging (bottom-up) or splitting (top-down) groups.
- **Dendrogram:** A tree diagram that shows how clusters were merged/split at different distances.
- **Topic Modeling:** Techniques (e.g., LDA, BERTopic) to discover abstract topics within a collection of documents.
- **Extractive Summarization:** Selecting existing sentences from a text to form a summary.
- **Abstractive Summarization:** Generating new sentences that paraphrase and condense the source text.
- **NER (Named Entity Recognition):** Detecting entities (people, places, organizations, etc.) in text.
- **Entity Linking:** Mapping detected entity mentions to canonical identities across documents.
- **Graph Schema:** The definition of node and edge types and their attributes.
- **Silhouette Score:** A metric to evaluate how well data are clustered (higher is typically better).
- **ROUGE/BERTScore:** Metrics that compare a generated summary to a reference; use cautiously for imperfect proxies of quality.
- **Ablation Study:** An experiment where one component is changed/removed to measure its effect on performance.

---

## Tutorial-Style Authoring Guidance (for Cursor AI or any assistant you use)
- Always **explain** before instructing: give a quick conceptual overview, then list numbered steps.
- Use **short, concrete steps** with explicit inputs/outputs and where to store artifacts.
- Include **rationale** for each decision and, when appropriate, offer 1–2 alternatives and when to choose them.
- **Never provide code unless explicitly requested.** If the developer asks for code:
  - Provide one minimal, well-commented snippet at a time.
  - Match it directly to the current step and the configs in use.
  - Include quick validation checks after the snippet (expected outputs, where artifacts appear).
- Favor **determinism and reproducibility**: fixed seeds, stable ordering, documented versions.
- After each phase, prompt for a **sanity check** and a short **retrospective** (“What worked? What felt brittle? What will you try next?”).

---

## Definition of Done (Per Phase)
- **P0:** Environment + configs + logging scaffold in place.
- **P1:** JSONL text with clean metadata emitted for each PDF.
- **P2:** Normalized spans with audit notes; deterministic IDs.
- **P3:** Optional concept candidates available for labeling support.
- **P4:** Embeddings saved with a stable mapping; basic NN sanity checks pass.
- **P5:** Clusters produced and documented; diagnostics saved.
- **P6:** Tree built with labels and parents; outliers handled.
- **P7:** Summaries generated (extractive + abstractive) with quality notes.
- **P8:** Cross-doc merges created; false merges analyzed.
- **P9:** Graph exported with schema docs; sample loaded to UI.
- **P10:** Metrics + human eval write-up; ablations recorded.
- **P11:** API serves graph and summaries; contracts documented.
- **P12:** Frontend shows hierarchy with functional navigation and summaries.
- **P13:** Reproducible runs and decision logs.
- **P14:** At least one extension explored and documented.

---

## Final Notes
- This project is a **learning lab**: prioritize understanding over raw performance.
- Keep your **README** updated as you make decisions; the repo is a portfolio piece—show your reasoning.
- When you want code for a step, ask for it specifically (e.g., “Give me the code to batch-embed spans and save `.npy` with an index, based on the config structure we defined.”).

---

**You’ve got this.** Build the pipeline end-to-end, keep artifacts tidy, and iterate thoughtfully. The result will be both a valuable learning journey and an impressive portfolio system.
