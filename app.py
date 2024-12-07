from flask import Flask, jsonify, request, render_template, logging
from controller import retrieve
from flask_cors import CORS
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from mangum import Mangum
from asgiref.wsgi import WsgiToAsgi
import logging
import asyncio
import json

app = Flask(__name__, template_folder='templates')
CORS(app)

@app.route('/')
def home():
    return render_template('index.html'), 200

@app.route('/document', methods=['POST'])
def document():
    if request.is_json:
        data = request.get_json()

        repo_owner = data.get('repo_owner')
        repo = data.get('repo')
        files_changed = data.get('files_changed')
        github_token = data.get('github_token')

        if not repo_owner or not repo:
            return jsonify(error="Missing data: 'repo' and 'repo_owner' required."), 400
        if not files_changed:
            return jsonify(message="No files changed."), 200

        try:
            updated_doc = asyncio.run(retrieve(repo_owner, repo, files_changed, github_token))
            if updated_doc == "No previous documentation found":
                return jsonify({'error': "No previous documentation found"})
            return jsonify({'updated_doc': updated_doc})
        except Exception as e:
            logging.error(f"Exception: {e}")
            return jsonify(error="Failed to fetch files"), 400
    else:
        return jsonify(message="Request was not JSON"), 400


asgi_app = WsgiToAsgi(app)
handler = Mangum(asgi_app, lifespan="off")

def lambda_handler(event, context):
    return handler(event, context)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)