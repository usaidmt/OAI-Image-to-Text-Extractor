import os
import glob
from image_processor import allowed_file
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app

upload_blueprint = Blueprint('upload', __name__)

def configure_upload(app):
    app.config["UPLOAD_FOLDER"] = "uploads"
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def clear_upload_folder():
    """Remove all files in the upload folder"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    files = glob.glob(os.path.join(upload_folder, '*'))
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Error deleting file {f}: {str(e)}")

@upload_blueprint.route('/upload-file', methods=['POST', 'GET'])
def upload_files():
    if request.method == 'POST':
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400

        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            return jsonify({"error": "No selected files"}), 400

        # Clear existing files before saving new ones
        clear_upload_folder()

        saved_files = []
        errors = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                try:
                    file.save(filepath)
                    saved_files.append(filename)
                except Exception as e:
                    errors.append({file.filename: str(e)})
            else:
                errors.append({file.filename: "File type not allowed"})

        response = {
            "message": "Upload successful. Previous files were removed.",
            "saved_files": saved_files
        }
        if errors:
            response["errors"] = errors

        return jsonify(response)
    
    elif request.method == 'GET':
        return jsonify({
            "description": "File upload endpoint",
            "methods": ["POST", "GET"],
            "POST": {
                "parameters": {
                    "files": "One or more files to upload"
                },
                "response": {
                    "message": "Success message",
                    "saved_files": "List of successfully uploaded filenames",
                    "errors": "List of errors if any occurred"
                }
            }
        })