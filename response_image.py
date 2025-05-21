import os
from image_processor import process_single_image
from flask import Blueprint, jsonify, current_app

response_blueprint = Blueprint('response', __name__)

@response_blueprint.route('/detailed-text-extractor', methods=['GET'])
def detailed_extractor():
    """GET endpoint for structured data extraction from ALL uploaded files"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    if not os.path.exists(upload_folder):
        return jsonify({"error": "No files have been uploaded yet"}), 404

    files = os.listdir(upload_folder)
    if not files:
        return jsonify({"error": "Upload folder is empty"}), 404

    results = {}
    errors = []

    for filename in files:
        filepath = os.path.join(upload_folder, filename)
        
        try:
            extracted_data = process_single_image(filepath)
            
            if isinstance(extracted_data, dict) and "error" in extracted_data:
                errors.append({filename: extracted_data["error"]})
            else:
                results[filename] = extracted_data
                
        except Exception as e:
            errors.append({filename: str(e)})

    response = {"results": results}
    if errors:
        response["errors"] = errors

    return jsonify(response)

@response_blueprint.route('/text-extractor', methods=['GET'])
def text_extractor():
    """GET endpoint for raw text extraction from ALL uploaded files"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    
    if not os.path.exists(upload_folder):
        return jsonify({"error": "No files have been uploaded yet"}), 404

    files = os.listdir(upload_folder)
    if not files:
        return jsonify({"error": "Upload folder is empty"}), 404

    results = {}
    errors = []

    for filename in files:
        filepath = os.path.join(upload_folder, filename)
        
        try:
            extracted_text = process_single_image(filepath, extract_text_only=True)
            
            if isinstance(extracted_text, dict) and "error" in extracted_text:
                errors.append({filename: extracted_text["error"]})
            else:
                results[filename] = extracted_text
                
        except Exception as e:
            errors.append({filename: str(e)})

    response = {"results": results}
    if errors:
        response["errors"] = errors

    return jsonify(response)