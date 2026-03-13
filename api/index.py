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
    import asyncio
    
    def generate():
        try:
            # chat_with_agent is an async generator, we need to iterate it using asyncio
            # Since Flask view is synchronous, we create an event loop to run the async iteration
            async def run_async_generator():
                chunks = []
                async for chunk in chat_with_agent(user_input, history):
                    chunks.append(chunk)
                return chunks
                
            # For streaming in a synchronous flask app, we can use run_coroutine_threadsafe or run_until_complete
            # A simple synchronous block to yield chunks as they arrive is harder without async flask features.
            # Instead, we will simulate the stream by awaiting the whole thing and yielding parts, 
            # or yielding them as they are awaited. 
            # Note: For real streaming in Flask, one should use ASGI (e.g., Quart/FastAPI).
            # To keep it working in WSGI Flask, we can just consume the generator synchronously, wrapped in asyncio.run
            
            async def consume_stream():
                async for chunk in chat_with_agent(user_input, history):
                    yield chunk

            # A helper to iterate over async generator in a sync environment
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            gen = chat_with_agent(user_input, history)
            while True:
                try:
                    chunk = loop.run_until_complete(gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
            loop.close()
            
        except Exception as e:
            yield f"\n[Error]: {str(e)}"
            
    return Response(stream_with_context(generate()), mimetype='text/plain')

# Standalone development runner
if __name__ == '__main__':
    app.run(port=5000, debug=True)
