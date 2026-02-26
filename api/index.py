import sys
import os

# Ensure the root directory logic is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_from_directory
from agent import chat_with_agent

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

@app.route('/')
def home():
    return send_from_directory(ROOT_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    # Serve css, js, etc.
    return send_from_directory(ROOT_DIR, filename)

@app.route('/api/chat', methods=['POST'])
def chat():
    print("Received Chat HTTP Request")
    data = request.json
    user_input = data.get('message', '')
    history = data.get('history', [])
    
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
        
    from flask import Response, stream_with_context
    def generate():
        try:
            for chunk in chat_with_agent(user_input, history):
                yield chunk
        except Exception as e:
            yield f"\n[Error]: {str(e)}"
            
    return Response(stream_with_context(generate()), mimetype='text/plain')

# Standalone development runner
if __name__ == '__main__':
    app.run(port=5000, debug=True)
