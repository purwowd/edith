import os
import shutil
from dotenv import load_dotenv
import subprocess

# Load environment variables from .env file
load_dotenv()

def msg_messages():
    """
    Process WhatsApp database files by moving them to a working directory 
    and running wtsexporter to extract chat messages.
    
    Returns:
        str: Success or error message.
    """
    # Read environment variables
    OUTPUT_DIR = os.getenv("OUTPUT_DIR")
    LOCAL_WA_FILE = os.getenv("LOCAL_WA_FILE")
    LOCAL_MSG_FILE = os.getenv("LOCAL_MSG_FILE")

    if not OUTPUT_DIR or not LOCAL_WA_FILE or not LOCAL_MSG_FILE:
        return "Error: Missing required environment variables."

    # Define working directory
    WORKING_DIR = os.path.join(OUTPUT_DIR, "working_wts")
    os.makedirs(WORKING_DIR, exist_ok=True)

    # Define file paths
    local_wa_path = os.path.join(OUTPUT_DIR, LOCAL_WA_FILE)
    local_msg_path = os.path.join(OUTPUT_DIR, LOCAL_MSG_FILE)
    working_wa_path = os.path.join(WORKING_DIR, LOCAL_WA_FILE)
    working_msg_path = os.path.join(WORKING_DIR, LOCAL_MSG_FILE)

    # Move files to working directory if they exist
    errors = []
    if os.path.exists(local_wa_path):
        shutil.move(local_wa_path, working_wa_path)
    else:
        errors.append(f"File {local_wa_path} not found.")

    if os.path.exists(local_msg_path):
        shutil.move(local_msg_path, working_msg_path)
    else:
        errors.append(f"File {local_msg_path} not found.")

    if errors:
        return " | ".join(errors)

    # Change to working directory
    os.chdir(WORKING_DIR)

    # Run wtsexporter command
    try:
        subprocess.run(["wtsexporter", "-a", "--no-html", "--txt"], check=True)
        return "WhatsApp chat export completed successfully."
    except subprocess.CalledProcessError as e:
        return f"Error occurred while running wtsexporter: {e}"

# Contoh pemanggilan dari skrip lain:
# result = msg_messages()
# print(result)

import os
import json

def combine_txt_to_json(result_dir, output_json_file):
    """
    Combine all .txt files in the specified directory into a single JSON file.

    Args:
        result_dir (str): Path to the directory containing .txt files.
        output_json_file (str): Path to the output JSON file.

    Returns:
        str: Success message or error message.
    """
    result_dir = os.getenv("result_dir")
    output_json_file = os.getenv("output_json_file")
    if not os.path.exists(result_dir):
        return f"Error: Directory {result_dir} not found."

    # Dictionary to store combined data
    combined_data = {}

    # Iterate over all files in the result directory
    for filename in os.listdir(result_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(result_dir, filename)

            # Read the content of the .txt file
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Use the filename (without extension) as the key in the JSON
            key = os.path.splitext(filename)[0]
            combined_data[key] = content

    # Write the combined data to the output JSON file
    try:
        with open(output_json_file, "w", encoding="utf-8") as json_file:
            json.dump(combined_data, json_file, ensure_ascii=False, indent=4)
        return f"All .txt files have been combined into {output_json_file}"
    except Exception as e:
        return f"Error writing JSON file: {e}"


def wa_messageprocess():
    result_dir = os.getenv("result_dir")
    output_json_file = os.getenv("output_json_file")
    msg_messages()
    combine_txt_to_json(result_dir, output_json_file)
    return {"message": "All data saved successfully."}

def view_combined_json():
    """
    Load and display the contents of the combined JSON file.
    
    Returns:
        dict: Parsed JSON content or an error message.
    """
    json_file = os.getenv("output_json_file")
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {"error": f"File {json_file} not found."}
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON. The file might be corrupted."}

# Contoh pemanggilan
result = view_combined_json()
print(result)
