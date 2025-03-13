"""
Combined Chat Parser Script

This script processes chat logs from three different sources:
1. Google Chat
2. Google Voice
3. Slack

The input format is determined by the folder name containing the files.
All outputs are standardized to a common JSON format for further processing.
"""
import os
import json
import glob
import re
import argparse
from datetime import datetime
from collections import defaultdict
from bs4 import BeautifulSoup

def parse_gchat_timestamp(timestamp_str):
    """Convert Google Chat timestamp string to ISO format."""
    # Parse the timestamp format: "Monday, June 8, 2015 at 11:46:23 PM UTC"
    dt_format = "%A, %B %d, %Y at %I:%M:%S %p UTC"
    dt = datetime.strptime(timestamp_str, dt_format)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+00:00"

def get_sanitized_filename(names):
    """Generate a filename from participant names, ensuring it's valid."""
    # Sort to ensure consistent naming regardless of the order names appear
    sorted_names = sorted(['_'.join(name.split(' ')) for name in names])
    # Join with dashes and replace any invalid filename characters
    filename = "-".join(sorted_names)
    # Replace characters not allowed in filenames
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    return filename

def process_gchat_file(file_path, output_dir):
    """Process a single Google Chat messages.json file."""
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
                'timestamp': parse_gchat_timestamp(msg.get('created_date', '')),
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

def parse_gvoice_html_chat(file_path, chat_buddy_name):
    """Parse a single Google Voice HTML chat file and return a list of message objects."""
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

    messages = []

    # Find all message divs
    for message_div in soup.find_all('div', class_='message'):
        # Extract timestamp
        timestamp = message_div.find('abbr', class_='dt')['title']

        # Check if message is from "Me"
        is_me = message_div.find('abbr', class_='fn') and message_div.find('abbr', class_='fn').text.strip() == 'Me'

        # Extract message content
        content = message_div.find('q').text.strip()

        message = {
            "role": "assistant" if is_me else "user",
            "content": content,
            "timestamp": timestamp,
            "name": 'John Wang' if is_me else chat_buddy_name,
        }

        messages.append(message)

    return messages

def process_gvoice_directory(directory_path, output_dir):
    """Process all Google Voice HTML files in the directory and group them by prefix."""
    # Dictionary to store messages grouped by prefix
    grouped_messages = defaultdict(list)

    # Walk through directory
    for filename in os.listdir(directory_path):
        if '- Text -' in filename and filename.endswith('.html'):
            # Get prefix (everything before first '-')
            prefix = filename.split('-')[0].strip()

            # Parse file and add messages to appropriate group
            file_path = os.path.join(directory_path, filename)
            messages = parse_gvoice_html_chat(file_path, prefix)
            grouped_messages[prefix].extend(messages)
            print(f'Processed Google Voice: {prefix}')

    # Save each group to a file
    for prefix, messages in grouped_messages.items():
        output_file = os.path.join(output_dir, f"{prefix.strip()}.json")

        # Sort messages by timestamp before saving
        sorted_messages = sorted(messages, key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')))

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_messages, f, indent=2)

def convert_slack_timestamp(ts):
    """Convert Unix timestamp to ISO 8601 format."""
    try:
        timestamp = float(ts)
        dt = datetime.fromtimestamp(timestamp, datetime.timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.000+00:00")
    except (ValueError, TypeError):
        return ts

def process_slack_message(message):
    """Process a single Slack message and return formatted output message."""
    # Skip messages with empty text
    if not message.get("text"):
        return None

    # Skip messages without user_profile
    if "user_profile" not in message:
        return None

    # Create output message
    name = message["user_profile"].get("real_name", "Unknown")
    role = "assistant" if name == "John Wang" else "user"

    output_message = {
        "user_id": message["user"],
        "name": name,
        "role": role,
        "timestamp": convert_slack_timestamp(message.get("ts")),
        "content": message["text"]
    }

    return output_message

def process_slack_file(input_path, output_path):
    """Process a single Slack JSON file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {input_path}")
            return

    if not isinstance(data, list):
        print(f"Warning: Expected a list in {input_path}, got {type(data)}")
        return

    output_messages = []
    messages_with_replies = {}
    users = {}

    # Track parent messages and their replies
    for message in data:
        processed_message = process_slack_message(message)
        if processed_message:
            output_messages.append(processed_message)
            users[processed_message["user_id"]] = processed_message["name"]

            # Check if this message has replies
            if "replies" in message:
                # Store the parent message and its replies
                messages_with_replies[message["ts"]] = {
                    "parent": processed_message,
                    "replies": []
                }

    # Process replies
    for message in data:
        if "thread_ts" in message and message.get("thread_ts") in messages_with_replies:
            # This is a reply to a parent message
            processed_reply = process_slack_message(message)
            if processed_reply:
                messages_with_replies[message["thread_ts"]]["replies"].append(processed_reply)

    # Add parent messages with their replies to the end of the output
    for thread_data in messages_with_replies.values():
        replies = thread_data["replies"]
        if replies:  # Only add if there are actual replies
            output_messages += replies

    # Replace user mentions with real names and remove 'user_id' field
    for msg in output_messages:
        del msg["user_id"]
        matches = re.findall(r"<@([A-Z0-9]+)>", msg['content'])
        if matches:
            content = msg['content']
            for match in matches:
                content = content.replace(f"<@{match}>", users.get(match, f"<@{match}>"))
            msg['content'] = content

    # Write output to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_messages, f, indent=2)

    print(f"Successfully processed {input_path} -> {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Process chat logs from different sources into standardized JSON format.')
    parser.add_argument('--input_dir', required=True, help='Root directory containing chat files')
    parser.add_argument('--output_dir', required=True, help='Directory to save processed JSON files')
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    # Create main output directory
    os.makedirs(output_dir, exist_ok=True)

    # Process files based on their source directory
    for root, dirs, files in os.walk(input_dir):
        # Determine the source type from the directory name
        dir_name = os.path.basename(root)

        if dir_name == "google-chat":
            continue
            # Create output subdirectory for Google Chat
            gchat_output_dir = os.path.join(output_dir, "google-chat")
            os.makedirs(gchat_output_dir, exist_ok=True)

            # Find all messages.json files
            message_files = glob.glob(os.path.join(root, "**", "messages.json"), recursive=True)

            if message_files:
                print(f"Found {len(message_files)} Google Chat files to process.")
                for file_path in message_files:
                    process_gchat_file(file_path, gchat_output_dir)

        elif dir_name == "google-voice":
            continue
            # Create output subdirectory for Google Voice
            gvoice_output_dir = os.path.join(output_dir, "google-voice")
            os.makedirs(gvoice_output_dir, exist_ok=True)

            # Process Google Voice files
            process_gvoice_directory(root, gvoice_output_dir)

        elif dir_name == "slack":
            continue
            # Create output subdirectory for Slack
            slack_output_dir = os.path.join(output_dir, "slack")
            os.makedirs(slack_output_dir, exist_ok=True)

            # Process Slack files
            json_files = [f for f in files if f.endswith('.json')]
            if json_files:
                print(f"Found {len(json_files)} Slack files to process.")
                for file in json_files:
                    input_path = os.path.join(root, file)
                    # Use the input filename for the output
                    output_path = os.path.join(slack_output_dir, file)
                    process_slack_file(input_path, output_path)

    print(f"Processing complete. Output files are in {output_dir}")

if __name__ == "__main__":
    main()