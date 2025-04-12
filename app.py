from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
import zipfile
from steg_detector import SteganographyDetector
from flask_cors import CORS

app = Flask(__name__)
detector = SteganographyDetector()

CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, filename)
        file.save(filepath)

        result = detector.analyze_image(filepath)
        return jsonify(result)

@app.route('/analyzezip', methods=['POST'])
def analyze_zip():
    if 'zip' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['zip']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, filename)
        file.save(zip_path)


        if not zipfile.is_zipfile(zip_path):
            return jsonify({"error": "Uploaded file is not a valid zip file"}), 400

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        results = {'files': []}
        for root, _, files in os.walk(tmpdir):
            for name in files:
                file_path = os.path.join(root, name)
                if file_path == zip_path:
                    continue
                results['files'].append({name: detector.analyze_image(file_path)})

        return jsonify(results)

@app.route('/')
def index():
    return "Steganography Detection API is running."

if __name__ == '__main__':
    app.run(debug=True)
