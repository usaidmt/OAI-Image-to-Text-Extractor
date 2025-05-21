from flask import Flask
from upload_file import upload_blueprint, configure_upload
from response_image import response_blueprint

app = Flask(__name__)

# Configure upload settings
configure_upload(app)

# Register blueprints
app.register_blueprint(upload_blueprint)
app.register_blueprint(response_blueprint)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)