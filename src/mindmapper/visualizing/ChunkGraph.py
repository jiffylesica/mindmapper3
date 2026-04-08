import json
from pathlib import Path
from collections import defaultdict
from pyvis.network import Network
from mindmapper.embedding.ChunkEmbedder import ChunkAssignment


class ChunkGraph:

    def __init__(self, output_dir: Path | None = None, use_cluster_hubs: bool = True):
        self._chunk_map = {}
        self._chunk_assignments: list[ChunkAssignment] = []
        self._cluster_summaries: dict[int, str] = {}
        self.net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
        self.output_dir = output_dir or Path.cwd() / "generated_graphs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.use_cluster_hubs = use_cluster_hubs

    @property
    def chunk_map(self) -> dict[str, int]:
        return self._chunk_map

    @chunk_map.setter
    def chunk_map(self, value: dict[str, int]) -> None:
        if not isinstance(value, dict):
            raise TypeError("chunk_map must be a dict")
        self._chunk_map = value

    @property
    def chunk_assignments(self) -> list[ChunkAssignment]:
        return self._chunk_assignments

    @chunk_assignments.setter
    def chunk_assignments(self, value: list[ChunkAssignment]) -> None:
        if not isinstance(value, list):
            raise TypeError("chunk_assignments must be a list")
        if any(not isinstance(item, ChunkAssignment) for item in value):
            raise TypeError("all chunk_assignments entries must be ChunkAssignment")
        self._chunk_assignments = value

    @property
    def cluster_summaries(self) -> dict[int, str]:
        return self._cluster_summaries

    @cluster_summaries.setter
    def cluster_summaries(self, value: dict[int, str]) -> None:
        if not isinstance(value, dict):
            raise TypeError("cluster_summaries must be a dict")
        self._cluster_summaries = value

    def _get_assignments(self) -> list[ChunkAssignment]:
        if self.chunk_assignments:
            return self.chunk_assignments
        return [
            ChunkAssignment(chunk_id=index, text=text, cluster_id=int(cluster_id))
            for index, (text, cluster_id) in enumerate(self.chunk_map.items())
        ]

    def create_graph(self, output_filename: str = "chunk_map.html") -> Path:
        self.net = Network(height="750px", width="100%",
                        bgcolor="#111827", font_color="#f9fafb")

        assignments = self._get_assignments()

        if self.use_cluster_hubs:
            clusters = defaultdict(list)
            for assignment in assignments:
                clusters[assignment.cluster_id].append(assignment)

            for cluster_id, members in clusters.items():
                hub_id = f"cluster-{cluster_id}-hub"
                summary = self.cluster_summaries.get(
                    cluster_id,
                    f"Cluster {cluster_id}: Summary unavailable.",
                )
                self.net.add_node(
                    hub_id,
                    label=f"Cluster {cluster_id}",
                    title=summary,
                    shape="diamond",
                    size=30,
                    physics=True,
                    color="#fdd835",
                )

                for assignment in members:
                    node_id = f"node-{assignment.chunk_id}"
                    self.net.add_node(
                        node_id,
                        label=f"Chunk {assignment.chunk_id + 1}",
                        group=str(cluster_id),
                        title=assignment.text.strip(),
                        shape="dot",
                        size=18,
                    )
                    self.net.add_edge(hub_id, node_id, length=150)
        else:
            # fallback: add without hubs but still assign groups
            for assignment in assignments:
                self.net.add_node(
                    assignment.chunk_id,
                    label=f"Chunk {assignment.chunk_id + 1}",
                    group=str(assignment.cluster_id),
                    title=assignment.text.strip(),
                    shape="dot",
                    size=18,
                )

        self._apply_cluster_layout()
        output_path = self.output_dir / output_filename
        self.net.show(str(output_path), notebook=False)
        self._inject_modal(output_path)
        return output_path

    def _apply_cluster_layout(self) -> None:
        assignments = self._get_assignments()
        unique_clusters = sorted({str(assignment.cluster_id) for assignment in assignments})

        palette = [
            ("#60a5fa", "#1d4ed8"),
            ("#f97316", "#c2410c"),
            ("#34d399", "#047857"),
            ("#f472b6", "#be185d"),
            ("#a78bfa", "#6d28d9"),
            ("#f43f5e", "#be123c"),
            ("#facc15", "#ca8a04"),
            ("#38bdf8", "#0ea5e9"),
        ]

        groups: dict[str, dict[str, object]] = {}
        for idx, cluster_id in enumerate(unique_clusters):
            bg, border = palette[idx % len(palette)]
            groups[cluster_id] = {
                "color": {"background": bg, "border": border},
                "borderWidth": 2,
            }

        options = {
            "physics": {
                "stabilization": True,
                "solver": "forceAtlas2Based",
                "forceAtlas2Based": {
                    "theta": 0.45,
                    "gravitationalConstant": -65,
                    "damping": 0.35,
                },
                "minVelocity": 0.5,
            },
            "groups": groups,
            "edges": {
                "smooth": {
                    "enabled": True,
                    "type": "dynamic",
                },
                "color": "#94a3b8",
            },
        }

        self.net.set_options(json.dumps(options))

    def _inject_modal(self, html_path: Path) -> None:
        """
        Append modal markup and interaction script to the generated PyVis HTML
        so clicking a node opens the full chunk text.
        """
        try:
            content = html_path.read_text(encoding="utf-8")
        except OSError:
            return

        # Avoid injecting twice
        if "chunk-modal" in content:
            return

        style_block = """
<style>
  .chunk-modal {
    position: fixed;
    inset: 0;
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 9999;
  }
  .chunk-modal.is-active {
    display: flex;
  }
  .chunk-modal__backdrop {
    position: absolute;
    inset: 0;
    background: rgba(15, 23, 42, 0.65);
  }
  .chunk-modal__content {
    position: relative;
    max-width: 720px;
    width: 90%;
    max-height: 80vh;
    background: #ffffff;
    color: #111827;
    border-radius: 12px;
    box-shadow: 0 24px 48px rgba(15, 23, 42, 0.35);
    padding: 1.75rem 2rem;
    overflow-y: auto;
    font-family: "Inter", "Segoe UI", Helvetica, Arial, sans-serif;
  }
  .chunk-modal__close {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    background: transparent;
    border: none;
    font-size: 1.5rem;
    color: #475569;
    cursor: pointer;
  }
  .chunk-modal__title {
    margin: 0 0 1rem;
    font-size: 1.25rem;
    font-weight: 600;
  }
  .chunk-modal__body {
    white-space: pre-wrap;
    line-height: 1.6;
    font-size: 1rem;
    font-family: "Source Code Pro", "Menlo", "Monaco", monospace;
  }
</style>
"""

        modal_markup = """
<div id="chunk-modal" class="chunk-modal" role="dialog" aria-modal="true" aria-labelledby="chunk-modal-title">
  <div class="chunk-modal__backdrop"></div>
  <div class="chunk-modal__content">
    <button type="button" id="chunk-modal-close" class="chunk-modal__close" aria-label="Close chunk dialog">&times;</button>
    <h3 id="chunk-modal-title" class="chunk-modal__title">Chunk Details</h3>
    <pre id="chunk-modal-body" class="chunk-modal__body"></pre>
  </div>
</div>
"""

        script_block = """
<script type="text/javascript">
  window.addEventListener("load", function () {
    if (typeof network === "undefined") {
      return;
    }

    const modal = document.getElementById("chunk-modal");
    const backdrop = modal.querySelector(".chunk-modal__backdrop");
    const closeBtn = document.getElementById("chunk-modal-close");
    const titleEl = document.getElementById("chunk-modal-title");
    const bodyEl = document.getElementById("chunk-modal-body");

    function openModal(title, text) {
      titleEl.textContent = title || "Chunk";
      bodyEl.textContent = text || "No text available.";
      modal.classList.add("is-active");
    }

    function closeModal() {
      modal.classList.remove("is-active");
    }

    closeBtn.addEventListener("click", closeModal);
    backdrop.addEventListener("click", closeModal);
    window.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeModal();
      }
    });

    network.on("selectNode", function (params) {
      if (!params.nodes || !params.nodes.length) {
        return;
      }
      const nodeId = params.nodes[0];
      const node = network.body.data.nodes.get(nodeId);
      if (!node) {
        return;
      }
      openModal(node.label, node.title);
    });

    network.on("deselectNode", function () {
      closeModal();
    });
  });
</script>
"""

        injection = f"{style_block}\n{modal_markup}\n{script_block}\n"

        if "</body>" in content:
            content = content.replace("</body>", f"{injection}</body>")
        else:
            content += injection

        try:
            html_path.write_text(content, encoding="utf-8")
        except OSError:
            pass