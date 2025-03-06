"""
My Parsed Google Voice format -> Apple MLX Training format

Operates on output files of directory parser that parses raw html google voice
dumps. Takes the output files and formats them according to Apple MLX training
format.

Things done:
- Aggregates messages within X hours into single block
- Ensures messages alternate between user and assistant by combining
    consecutive messages from the same role
"""

import glob
import os
import json
import sys
from datetime import datetime, timedelta
import argparse

# Configuration
TIME_THRESHOLD = timedelta(hours=12)  # Messages within 12 hours are grouped


class MessageGroup:
    def __init__(self, add_names):
        self.group = []
        self.add_names = add_names

    def add_message(self, msg):
        if self.add_names and msg["role"] == "user":
            msg['content'] = f'{msg["name"]} said: ' + msg['content']
        self.group.append(msg)

    def merge_message(self, msg):
        last_msg = self.group[-1]
        if msg["role"] == "assistant":
            last_msg['content'] += f'. {msg["content"]}'
        else:
            if msg["name"] == last_msg["name"]:
                last_msg['content'] += f'. {msg["content"]}'
            else:
                name_content = f'{msg["name"]} said: ' if self.add_names else ''
                last_msg['content'] += f'. {name_content}{msg["content"]}'
                last_msg['name'] = msg["name"]

    def reset(self):
        self.group = []

    def is_empty(self):
        return len(self.group) == 0

    def get_last_message(self):
        return self.group[-1]

    def get_roles(self):
        return set(msg['role'] for msg in self.group)

    def get_group(self):
        return self.group


def process_json_file(input_filepath, train_filepath, valid_filepath):
    # Load JSON file
    with open(input_filepath, "r") as f:
        messages = json.load(f)

    # Convert timestamps to datetime objects
    names = set()
    for msg in messages:
        msg["timestamp"] = datetime.fromisoformat(msg["timestamp"])
        names.add(msg["name"])
    add_names = False
    if len(names) > 2:
        add_names = True

    # Sort messages by timestamp
    messages.sort(key=lambda x: x["timestamp"])

    # Group messages
    grouped_messages = []
    current_group = MessageGroup(add_names)

    for msg in messages:
        curr_role = msg["role"]

        if current_group.is_empty():
            if curr_role == "user":
                current_group.add_message(msg)
            else:
                continue
        else:
            last_msg_time = current_group.get_last_message()["timestamp"]
            last_role = current_group.get_last_message()["role"]

            if msg["timestamp"] - last_msg_time > TIME_THRESHOLD:
                if len(current_group.get_roles()) == 2:
                    grouped_messages.append(current_group.get_group())
                current_group.reset()
                if curr_role == 'user':
                    current_group.add_message(msg)
            else:
                if curr_role == last_role:
                    current_group.merge_message(msg)
                else:
                    current_group.add_message(msg)

    if not current_group.is_empty() and len(current_group.get_roles()) == 2:
        grouped_messages.append(current_group.get_group())

    for g in grouped_messages:
        for item in g:
            del item['timestamp']
    transformed_groups = grouped_messages

    # Save the transformed JSON file
    with open(train_filepath, "a") as train_fp:
        with open(valid_filepath, "a") as valid_fp:
            cnt = 1
            for grp in transformed_groups:
                if cnt % 10 == 0:
                    valid_fp.write(json.dumps({"messages": grp}) + '\n')
                else:
                    train_fp.write(json.dumps({"messages": grp}) + '\n')
                cnt += 1

def main(input_dir, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process all JSON files in the input directory
    train_output_path = os.path.join(output_dir, "train.jsonl")
    valid_output_path = os.path.join(output_dir, "valid.jsonl")
    # Blank out existing files
    with open(train_output_path, "w") as train_fp:
        pass
    with open(valid_output_path, "w") as valid_fp:
        pass

    message_files = glob.glob(os.path.join(input_dir, "**", "*.json"), recursive=True)

    for filename in message_files:
        if filename.endswith(".json"):
            input_path = os.path.join(input_dir, filename)
            process_json_file(input_path, train_output_path, valid_output_path)
            print(f"Processed: {filename}")

    print("All files processed successfully!")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert Google Voice JSON to Apple MLX format.")
    parser.add_argument("--input_dir", required=True, help="Directory containing input JSON files.")
    parser.add_argument("--output_dir", required=True, help="Directory to save output JSONL files.")
    
    args = parser.parse_args()
    
    main(input_dir=args.input_dir, output_dir=args.output_dir)
