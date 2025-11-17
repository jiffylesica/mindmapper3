from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, flash, url_for, send_file, abort
from werkzeug.utils import secure_filename

from mindmapper.pipeline import TextToGraphPipeline

# Load environment variables from .env (must exist at project root)
load_dotenv()

# Constants
ALLOWED_EXTENSIONS = {"txt"}
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
            flash("Only .txt files are supported.")
            return redirect(url_for("index"))

        filename = secure_filename(file.filename)
        saved_path = UPLOAD_DIR / filename
        file.save(saved_path)

        with saved_path.open("r", encoding="utf-8") as f:
            text = f.read()

        try:
            graph_filename = f"{Path(filename).stem}_graph.html"
            result_path = pipeline.run_pipeline_from_text(
                text=text,
                sent_per_chunk=4,
                num_clusters=3,
                output_filename=graph_filename,
            )
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
    app.run(debug=True)