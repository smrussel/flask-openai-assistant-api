import json
import os

basedir = os.path.abspath(os.path.dirname(__file__))

def create_assistant(client):
    assistant_file_path = os.path.join(basedir,"assistant.json")
    # load the existing assistant id from json file
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, "r") as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data["assistant_id"]
            print("Loaded existing assistant ID.")
    else:
        # Create a vector store 
        vector_store = client.beta.vector_stores.create(name="Company data")
        
        # Ready the files for upload to OpenAI
        file_paths = [os.path.join(basedir,"company-info.docx")]
        file_streams = [open(path, "rb") for path in file_paths]

        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )

        assistant = client.beta.assistants.create(
            instructions="""
          The assistant, GreenPower Solutions Sales Mentor, has been programmed to assist junior sales representatives in learning company standard operating procedures and effective selling techniques as salespersons.
          A document has been provided with information on GreenPower Solutions' solar sales processes and training details.
          """,
            model="gpt-3.5-turbo-1106", # or  gpt-4-1106-preview
            tools=[
                    # {"type": "code_interpreter"},
                    {"type": "file_search"}
                ],
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )
        
        print(assistant)

        with open(assistant_file_path, "w") as file:
            json.dump({"assistant_id": assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id
