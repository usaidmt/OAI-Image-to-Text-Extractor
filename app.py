from flask import Flask
from flask_cors import CORS
from upload_file import upload_blueprint, configure_upload
from response_image import response_blueprint

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return "Hello, World! Flask app is live."

# Configure upload settings
configure_upload(app)

# Register blueprints
app.register_blueprint(upload_blueprint)
app.register_blueprint(response_blueprint)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=443, debug=True)
