import io
import json
from pathlib import Path
from zipfile import ZipFile, BadZipFile
from flask import Flask, request, jsonify, send_file, abort
from promofinder import analyze

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 20_000_000
root = Path(__file__).resolve().parent

@app.get("/")
def home():
    return send_file(root / "index.html")

@app.get("/results")
def demo():
    return send_file(root / "demo.json")

@app.post("/analyze")
def analyze_upload():
    if request.mimetype != "application/zip":
        abort(415)
    data = request.get_data()
    try:
        with ZipFile(io.BytesIO(data)) as pack:
            members = pack.infolist()
            if len(members)>250 or sum(m.file_size for m in members)>8_000_000:
                return "Upload up to 250 files and 8 MB of expanded scripts.",400
            for m in members:
                if m.filename.lower().endswith(".txt") and (m.file_size>150000 or pack.read(m).lower().count(b"start:")>500):
                    return "Episode exceeds demo size limit.",400
        return jsonify(analyze(data))
    except (ValueError, KeyError, TypeError, BadZipFile, RuntimeError, IndexError):
        return "Please upload a ZIP of timestamped episode scripts.",400
