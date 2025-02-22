import os
import json
from datetime import datetime

def parse_slack_message(message):
    """
    Parse a single Slack message into the desired format.
    Only process messages that have user_profile information.
    """
    # Skip system messages or messages without proper user profile
    if 'user_profile' not in message or 'subtype' in message:
        return None

    # Extract the required fields
    return {
        'name': message['user_profile']['real_name'],
        'content': message['text'],
        'timestamp': datetime.fromtimestamp(float(message['ts'])).strftime('%Y-%m-%d %H:%M:%S')
    }

def process_chat_file(input_file_path):
    """
    Process a single chat file and return list of parsed messages.
    """
    with open(input_file_path, 'r', encoding='utf-8') as file:
        chat_data = json.load(file)

    # Process each message in the chat data
    parsed_messages = []
    for message in chat_data:
        parsed_message = parse_slack_message(message)
        if parsed_message:  # Only add if message was successfully parsed
            parsed_messages.append(parsed_message)

    return parsed_messages

def process_directory(directory_path, output_path):
    """
    Process all JSON files in the directory and create corresponding output files.
    """
    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            input_file_path = os.path.join(directory_path, filename)
            output_filename = f"../{output_path}/output-{filename}"
            output_file_path = os.path.join(directory_path, output_filename)

            try:
                # Process the file
                parsed_messages = process_chat_file(input_file_path)

                # Write the processed messages to output file
                with open(output_file_path, 'w', encoding='utf-8') as outfile:
                    json.dump(parsed_messages, outfile, indent=2)

                print(f"Successfully processed {filename} -> {output_filename}")

            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

def main():
    # Directory containing the chat files
    directory_path = "chat_files"  # Change this to your input directory
    output_path = 'output'

    # Create directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)

    # Process all files in the directory
    process_directory(directory_path, output_path)

if __name__ == "__main__":
    main()
