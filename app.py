import os
from flask import Flask, jsonify, request
import logging
from werkzeug.utils import quote as url_quote

app = Flask(__name__)

# Secure configuration for production
app.config.from_mapping(
    SECRET_KEY=os.getenv('SECRET_KEY', 'my_default_secret_key'),
    DEBUG=os.getenv('FLASK_DEBUG', 'False') == 'True'
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route('/example')
def example():
    quoted_url = url_quote('https://example.com')
    return jsonify({"quoted_url": quoted_url})

@app.route('/')
def hello_world():
    logger.info('Hello World route accessed')
    return '@LazyDeveloper'

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    # Retrieve host and port from environment variables for production
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 8080))
    app.run(debug=app.config['DEBUG'], host=host, port=port)
