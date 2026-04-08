from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, flash, url_for, send_file, abort
from werkzeug.utils import secure_filename

from mindmapper.pipeline import TextToGraphPipeline
from mindmapper.extraction import PDFExtractor
from mindmapper.cleaning.TextProcessor import CHUNKING_STRATEGY_FIXED, CHUNKING_STRATEGY_HIERARCHICAL

# Load environment variables from .env (must exist at project root)
load_dotenv()

# Constants
ALLOWED_EXTENSIONS = {"txt", "pdf"}
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
RESULT_DIR = BASE_DIR / "generated_graphs"

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# Flask app
app = Flask(__name__)
app.secret_key = "change-me"          # replace with a secure value

# Pipeline (reuse the same instance per process)
pipeline = TextToGraphPipeline(graph_output_dir=RESULT_DIR)
pdf_extractor = PDFExtractor()

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            flash("Please choose a file before submitting.")
            return redirect(url_for("index"))
        if not allowed_file(file.filename):
            flash("Only .txt and .pdf files are supported.")
            return redirect(url_for("index"))

        filename = secure_filename(file.filename)
        saved_path = UPLOAD_DIR / filename
        file.save(saved_path)

        # Extract text based on file type
        file_ext = filename.rsplit(".", 1)[1].lower()
        try:
            if file_ext == "pdf":
                text = pdf_extractor.extract_text_from_pdf(saved_path)
            else:  # txt
                with saved_path.open("r", encoding="utf-8") as f:
                    text = f.read()
        except Exception as exc:
            flash(f"Failed to read file: {exc}")
            return redirect(url_for("index"))

        try:
            graph_filename = f"{Path(filename).stem}_graph.html"
            
            # Get chunking strategy from form
            chunking_strategy = request.form.get("chunking_strategy", CHUNKING_STRATEGY_FIXED)

            # Get and validate cluster count from form (allowed range: 2-5)
            num_clusters_raw = request.form.get("num_clusters", "3")
            try:
                num_clusters = int(num_clusters_raw)
                if num_clusters < 2 or num_clusters > 5:
                    num_clusters = 3
            except (ValueError, TypeError):
                num_clusters = 3
            
            # Prepare kwargs for pipeline
            pipeline_kwargs = {
                "text": text,
                "num_clusters": num_clusters,
                "output_filename": graph_filename,
                "chunking_strategy": chunking_strategy,
            }
            
            # Add strategy-specific parameters
            if chunking_strategy == CHUNKING_STRATEGY_HIERARCHICAL:
                max_chunk_size = request.form.get("max_chunk_size", "10")
                try:
                    max_chunk_size = int(max_chunk_size)
                    if max_chunk_size < 1 or max_chunk_size > 10:
                        max_chunk_size = 10
                except (ValueError, TypeError):
                    max_chunk_size = 10
                pipeline_kwargs["max_chunk_size"] = max_chunk_size
            else:
                sent_per_chunk = request.form.get("sent_per_chunk", "4")
                try:
                    sent_per_chunk = int(sent_per_chunk)
                    if sent_per_chunk <= 0:
                        sent_per_chunk = 4
                except (ValueError, TypeError):
                    sent_per_chunk = 4
                pipeline_kwargs["sent_per_chunk"] = sent_per_chunk
            
            result_path = pipeline.run_pipeline_from_text(**pipeline_kwargs)
        except Exception as exc:
            flash(f"Pipeline failed: {exc}")
            return redirect(url_for("index"))

        flash(f"Uploaded {filename} successfully.")
        return redirect(url_for("result", graph_filename=result_path.name))

    return render_template("index.html")

@app.route("/result/<graph_filename>")
def result(graph_filename: str):
    graph_path = RESULT_DIR / graph_filename
    if not graph_path.exists():
        abort(404)
    return render_template("result.html", graph_url=url_for("serve_graph", graph_filename=graph_filename))

@app.route("/graphs/<graph_filename>")
def serve_graph(graph_filename: str):
    graph_path = RESULT_DIR / graph_filename
    if not graph_path.exists():
        abort(404)
    return send_file(graph_path)

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8080)