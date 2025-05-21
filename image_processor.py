import os
import re
import json
import base64
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-2025-04-14")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_json_response(response_text):
    """
    Clean the response from GPT-4o by removing markdown code blocks and other formatting
    to return a pure JSON string.
    """
    # Remove markdown code blocks if present
    json_content = re.sub(r'```json\s*|\s*```', '', response_text)
    
    # Remove any non-JSON text before or after JSON
    json_content = json_content.strip()
    
    # Try to parse the cleaned content to ensure it's valid JSON
    try:
        parsed_json = json.loads(json_content)
        return parsed_json
    except json.JSONDecodeError:
        # If parsing fails, return the cleaned string
        return json_content

def process_single_image(image_path, extract_text_only=False):
    """Process a single image and return extracted data or raw text"""
    try:
        with open(image_path, "rb") as file:
            image_bytes = file.read()
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Determine MIME type based on file extension
            filename = os.path.basename(image_path)
            if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
                mime_type = "image/jpeg"
            elif filename.lower().endswith(".png"):
                mime_type = "image/png"
            elif filename.lower().endswith(".gif"):
                mime_type = "image/gif"
            elif filename.lower().endswith(".bmp"):
                mime_type = "image/bmp"
            elif filename.lower().endswith(".tiff"):
                mime_type = "image/tiff"
            else:
                mime_type = "application/octet-stream"
                
            image_data_url = f"data:{mime_type};base64,{encoded_image}"

        if extract_text_only:
            # For text extraction only
            prompt = "Extract all the text from this image exactly as it appears, preserving the original formatting, line breaks, and punctuation. Do not interpret or structure the text, just return it exactly as it appears in the image."
        else:
            # For structured data extraction
            prompt = "Extract key-value pairs from this image and return a valid JSON object."

        response = openai.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts information from documents." if extract_text_only else "You are a helpful assistant that extracts key-value pairs from documents. Return only a valid JSON object with no explanation or markdown formatting."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data_url}}
                    ]
                }
            ],
            max_tokens=1000,
        )
        
        raw_extracted_data = response.choices[0].message.content
        
        if extract_text_only:
            return raw_extracted_data  # Return raw text directly
        else:
            return clean_json_response(raw_extracted_data)

    except Exception as e:
        return {"error": str(e)}