from flask import Flask, jsonify, request
import logging

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
