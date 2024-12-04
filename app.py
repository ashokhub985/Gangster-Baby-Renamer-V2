from flask import Flask, jsonify, request
import logging
from flask import Flask, jsonify, request
from flask import Flask, jsonify, request
from werkzeug.utils import quote as url_quote  # Is line ko yahan likhiye

app = Flask(__name__)

@app.route('/example')
def example():
    # Yahan aap url_quote ka istemal kar rahe honge
    quoted_url = url_quote('https://example.com')
    return jsonify({"quoted_url": quoted_url})
    
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Custom error handler
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def hello_world():
    logger.info('Hello World route accessed')
    return '@LazyDeveloper'

if __name__ == "__main__":
    # Run the app with enhanced configurations
    app.run(debug=True, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    app.run()
