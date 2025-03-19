from flask import(
    Flask,
    request,
    Response,
    stream_with_context
)

from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os

# load the environment variable
load_dotenv()

# initialize flask application
app = Flask(__name__)

# Apply CORS (Cross-origin resourse sharing)
CORS(app)

# Configure Google GenAI API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash"
)

@app.route('/chat', methods=['POST'])

def chat():
    """Processes user input and returns AI-generated responses.

    This function handles POST requests to the '/chat' endpoint. It expects a JSON payload
    containing a user message and an optional conversation history. It returns the AI's
    response as a JSON object.

    Args:
        None (uses Flask `request` object to access POST data)

    Returns:
        A JSON object with a key "text" that contains the AI-generated response.
    """

    # Parse the incoming JSON data into variable
    data = request.json
    msg = data.get('chat', '')
    chat_history = data.get('history',[])

    # Start a chat session with the model using the provided history
    chat_session = model.start_chat(history=chat_history)

    # Send the latest user input to the model and get the response
    response = chat_session.send_message(msg)

    return {"text": response.text}

@app.route("/stream", methods=["POST"])
def stream():
    """Streams AI responses for real-time chat interactions.

    This function initiates a streaming session with the Gemini AI model,
    continuously sending user inputs and streaming back the responses. It handles
    POST requests to the '/stream' endpoint with a JSON payload similar to the
    '/chat' endpoint.

    Args:
        None (uses Flask `request` object to access POST data)

    Returns:
        A Flask `Response` object that streams the AI-generated responses.
    """
    def generate():
        data = request.json
        msg = data.get('chat','')
        chat_history = data.get('history',[])

        chat_session = model.start_chat(history=chat_history)
        response = chat_session.send_message(msg,stream=True)

        for chunk in response:
            yield f"{chunk.txt}"

        return Response(stream_with_context(generate()), mimetype="text/event-stream")
    

# configure the server to run on port 8000
if __name__ == '__main__':
    app.run(port=os.getenv("PORT"))
    print("Server is running")