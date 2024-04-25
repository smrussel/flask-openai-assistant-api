import json
import os
from pathlib import Path

basedir = os.path.abspath(os.path.dirname(__file__))

def create_assistant(client):
    assistant_file_path = "assistant.json"

    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, "r") as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data["assistant_id"]
            print("Loaded existing assistant ID.")
    else:
        file = client.files.create(
            file=Path(os.path.join(basedir,"company-info.docx")), purpose="assistants"
        )

        assistant = client.beta.assistants.create(
            instructions="""
          The assistant, GreenPower Solutions Sales Mentor, has been programmed to assist junior sales representatives in learning company standard operating procedures and effective selling techniques as salespersons.
          A document has been provided with information on GreenPower Solutions' solar sales processes and training details.
          """,
            model="gpt-3.5-turbo-1106", # or  gpt-4-1106-preview
            tools=[
                    # {"type": "code_interpreter"},
                    {"type": "retrieval"}
                ],
            file_ids=[file.id],
        )

        with open(assistant_file_path, "w") as file:
            json.dump({"assistant_id": assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id
