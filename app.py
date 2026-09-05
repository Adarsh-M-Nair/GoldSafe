from flask import Flask, render_template, request, send_file
import os
import time
from ml.similarity import find_top_k_similar

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    image = request.files.get("image")

    if not image:
        return "No image uploaded"

    filename = image.filename or f"webcam_{int(time.time())}.jpg"
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    results = find_top_k_similar(image_path)

    return render_template(
    "results.html",
    query_image=image_path,   # KEEP FULL PATH
    results=results
)

DEFAULT_DATASET_DIR = os.path.join(app.root_path, "Dataset")
DATASET_DIR = os.environ.get("DATASET_DIR", DEFAULT_DATASET_DIR)

# 🔥 SERVE DATASET IMAGES FROM LOCAL DATASET FOLDER OR CUSTOM PATH
@app.route("/dataset_image")
def dataset_image():
    path = request.args.get("path")
    category = request.args.get("category")
    item_id = request.args.get("item_id")

    # Try resolving candidate paths
    candidate_paths = []
    if category and item_id:
        candidate_paths.extend([
            os.path.join(DATASET_DIR, category, item_id, "1.webp"),
            os.path.join(DEFAULT_DATASET_DIR, category, item_id, "1.webp"),
            os.path.join(app.root_path, "static", "Dataset", category, item_id, "1.webp"),
        ])

    if path:
        candidate_paths.append(path)

    for p in candidate_paths:
        if p and os.path.exists(p):
            return send_file(p)

    return "Image not found", 404


if __name__ == "__main__":
    app.run(debug=True)
