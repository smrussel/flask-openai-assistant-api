import os
from time import sleep
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
from utils import create_assistant
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)
CORS(app, supports_credentials=True)

# Init client
client = OpenAI(api_key=OPENAI_API_KEY)

# Create new assistant or load existing
assistant_id = create_assistant(client)


# Start conversation thread
@app.route("/start", methods=["GET"])
def start_conversation():
    print("Starting a new conversation...")
    thread = client.beta.threads.create()
    print(f"New thread created with ID: {thread.id}")
    return jsonify({"thread_id": thread.id})


# Generate response
@app.route("/chat", methods=["POST"])
@cross_origin(supports_credentials=True)
def chat():
    data = request.json
    thread_id = data.get("thread_id")
    user_input = data.get("message", "")

    if not thread_id:
        print("Error: Missing thread_id")
        return jsonify({"error": "Missing thread_id"}), 400

    print(f"Received message: {user_input} for thread ID: {thread_id}")

    # Add the user's message to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_input
    )

    # Run the Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=assistant_id
    )

    # Check if the Run requires action (function call)
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id, run_id=run.id
        )
        print(f"Run status: {run_status.status}")
        if run_status.status == "completed":
            break
        sleep(1)  # Wait for a second before checking again

    # Retrieve and return the latest message from the assistant
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value

    print(f"Assistant response: {response}")
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
