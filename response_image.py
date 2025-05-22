# import os
# from image_processor import process_single_image
# from flask import Blueprint, jsonify, current_app

# response_blueprint = Blueprint('response', __name__)

# @response_blueprint.route('/detailed-text-extractor', methods=['GET'])
# def detailed_extractor():
#     """GET endpoint for structured data extraction from ALL uploaded files"""
#     upload_folder = current_app.config['UPLOAD_FOLDER']
    
#     if not os.path.exists(upload_folder):
#         return jsonify({"error": "No files have been uploaded yet"}), 404

#     files = os.listdir(upload_folder)
#     if not files:
#         return jsonify({"error": "Upload folder is empty"}), 404

#     results = {}
#     errors = []

#     for filename in files:
#         filepath = os.path.join(upload_folder, filename)
        
#         try:
#             extracted_data = process_single_image(filepath)
            
#             if isinstance(extracted_data, dict) and "error" in extracted_data:
#                 errors.append({filename: extracted_data["error"]})
#             else:
#                 results[filename] = extracted_data
                
#         except Exception as e:
#             errors.append({filename: str(e)})

#     response = {"results": results}
#     if errors:
#         response["errors"] = errors

#     return jsonify(response)

# @response_blueprint.route('/text-extractor', methods=['GET'])
# def text_extractor():
#     """GET endpoint for raw text extraction from ALL uploaded files"""
#     upload_folder = current_app.config['UPLOAD_FOLDER']
    
#     if not os.path.exists(upload_folder):
#         return jsonify({"error": "No files have been uploaded yet"}), 404

#     files = os.listdir(upload_folder)
#     if not files:
#         return jsonify({"error": "Upload folder is empty"}), 404

#     results = {}
#     errors = []

#     for filename in files:
#         filepath = os.path.join(upload_folder, filename)
        
#         try:
#             extracted_text = process_single_image(filepath, extract_text_only=True)
            
#             if isinstance(extracted_text, dict) and "error" in extracted_text:
#                 errors.append({filename: extracted_text["error"]})
#             else:
#                 results[filename] = extracted_text
                
#         except Exception as e:
#             errors.append({filename: str(e)})

#     response = {"results": results}
#     if errors:
#         response["errors"] = errors

#     return jsonify(response)

import os
from image_processor import process_single_image
from flask import request, Blueprint, jsonify, current_app, Response, stream_with_context
import json

response_blueprint = Blueprint('response', __name__)

@response_blueprint.route('/detailed-text-extractor', methods=['GET'])
def detailed_extractor():
    """Endpoint for structured data extraction with streaming support"""
    return handle_extraction(extract_text_only=False)

@response_blueprint.route('/text-extractor', methods=['GET'])
def text_extractor():
    """Endpoint for raw text extraction with streaming support"""
    return handle_extraction(extract_text_only=True)

def handle_extraction(extract_text_only):
    """Shared extraction logic with streaming support"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    stream = request.args.get('stream', 'false').lower() == 'true'

    # Validate upload folder
    if not os.path.exists(upload_folder):
        return jsonify({"error": "No files have been uploaded yet"}), 404

    files = os.listdir(upload_folder)
    if not files:
        return jsonify({"error": "Upload folder is empty"}), 404

    if stream:
        def generate():
            yield 'data: {"status": "started", "total_files": %d}\n\n' % len(files)
            
            results = {}
            errors = []
            
            for filename in files:
                filepath = os.path.join(upload_folder, filename)
                
                try:
                    for chunk in process_single_image(filepath, extract_text_only):
                        if isinstance(chunk, dict) and "error" in chunk:
                            errors.append({filename: chunk["error"]})
                            yield 'data: %s\n\n' % json.dumps({"error": {filename: chunk["error"]}})
                        else:
                            results[filename] = chunk
                            yield 'data: %s\n\n' % json.dumps({"progress": filename, "data": chunk})
                
                except Exception as e:
                    errors.append({filename: str(e)})
                    yield 'data: %s\n\n' % json.dumps({"error": {filename: str(e)}})
            
            # Final complete message
            yield 'data: %s\n\n' % json.dumps({
                "status": "complete",
                "results": results,
                "errors": errors if errors else None
            })

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )
    else:
        # Non-streaming version
        results = {}
        errors = []

        for filename in files:
            filepath = os.path.join(upload_folder, filename)
            
            try:
                extracted_data = process_single_image(filepath, extract_text_only)
                
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