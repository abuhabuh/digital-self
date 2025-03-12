import re
import os
import json
import argparse
import datetime
from collections import defaultdict

def convert_timestamp(ts):
    """Convert Unix timestamp to ISO 8601 format."""
    try:
        timestamp = float(ts)
        dt = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.000+00:00")
    except (ValueError, TypeError):
        return ts

def process_message(message):
    """Process a single message and return formatted output message."""
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
        "timestamp": convert_timestamp(message.get("ts")),
        "content": message["text"]
    }
    
    return output_message

def process_file(input_path, output_path):
    """Process a single JSON file."""
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
        processed_message = process_message(message)
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
            processed_reply = process_message(message)
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

def process_directory(input_dir, output_dir):
    """Process all JSON files in a directory."""
    os.makedirs(output_dir, exist_ok=True)
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.json'):
                # Get the full path to the input file
                input_path = os.path.join(root, file)
                
                # Create the output path based on the input path
                rel_path = os.path.relpath(input_path, input_dir)
                output_filename = '-'.join(rel_path.split(os.path.sep)).replace('.json', '') + '.json'
                output_path = os.path.join(output_dir, output_filename)
                
                print(f"Processing: {input_path} -> {output_path}")
                process_file(input_path, output_path)

def main():
    parser = argparse.ArgumentParser(description='Process JSON files from input directory to output directory.')
    parser.add_argument('--input_dir', required=True, help='Input directory containing JSON files')
    parser.add_argument('--output_dir', required=True, help='Output directory for processed JSON files')
    
    args = parser.parse_args()
    
    process_directory(args.input_dir, args.output_dir)
    print("Processing complete.")

if __name__ == "__main__":
    main()