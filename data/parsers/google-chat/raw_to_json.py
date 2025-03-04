"""Claude assisted script for parsing raw google chat outputs into list of converstations

"""
import os
import json
import glob
from datetime import datetime
import hashlib
import re

def parse_timestamp(timestamp_str):
    """Convert the timestamp string to Unix timestamp (seconds since epoch)."""
    # Parse the timestamp format from the sample: "Monday, June 8, 2015 at 11:46:23 PM UTC"
    dt_format = "%A, %B %d, %Y at %I:%M:%S %p UTC"
    dt = datetime.strptime(timestamp_str, dt_format)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+00:00"

def get_sanitized_filename(names):
    """Generate a filename from participant names, ensuring it's valid."""
    # Sort to ensure consistent naming regardless of the order names appear
    sorted_names = sorted(names)
    # Join with dashes and replace any invalid filename characters
    filename = "-".join(sorted_names)
    # Replace characters not allowed in filenames
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    return filename

def process_messages_file(file_path, output_dir):
    """Process a single messages.json file and write output to the output directory."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'messages' not in data:
            print(f"Warning: No messages found in {file_path}")
            return

        messages = data['messages']
        if not messages:
            print(f"Warning: Empty messages list in {file_path}")
            return

        # Process each message and convert to the desired format
        processed_messages = []
        participants = set()

        for msg in messages:
            # Skip system messages like "Updated room membership"
            if "Updated room membership" in msg.get('text', ''):
                continue

            creator = msg.get('creator', {})
            name = creator.get('name', '')
            email = creator.get('email', '')

            # Add to participants set if not a system message
            if name and email:
                participants.add(name)

            # Create the message dictionary
            message_dict = {
                'role': "assistant" if email == "djmnemonic@gmail.com" else "user",
                'content': msg.get('text', ''),
                'timestamp': parse_timestamp(msg.get('created_date', '')),
                'name': name
            }

            processed_messages.append(message_dict)

        # Generate output filename based on participant names
        output_filename = get_sanitized_filename(participants) + ".json"
        output_path = os.path.join(output_dir, output_filename)

        # Write the processed messages to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_messages, f, indent=2)

        print(f"Successfully processed {file_path} -> {output_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def main():
    # Define the root directory to search and output directory
    root_dir = "/Users/john.wang/Desktop/Takeout/Google Chat/Groups"  # Current directory, change if needed
    output_dir = os.path.join('.', "processed_chats")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Find all messages.json files in subdirectories
    message_files = glob.glob(os.path.join(root_dir, "**", "messages.json"), recursive=True)

    if not message_files:
        print("No messages.json files found.")
        return

    print(f"Found {len(message_files)} messages.json files to process.")

    # Process each file
    for file_path in message_files:
        process_messages_file(file_path, output_dir)

    print(f"Processing complete. Output files are in {output_dir}")

if __name__ == "__main__":
    main()
