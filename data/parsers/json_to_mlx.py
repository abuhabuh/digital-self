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
    current_group = []

    for msg in messages:
        curr_role = msg["role"]
        curr_name = msg["name"]

        if not current_group:
            if curr_role == "user":
                if add_names: msg['content'] = f'{curr_name} said: ' + msg['content']
                current_group = [msg]
            else:
                continue
        else:
            last_msg_time = current_group[-1]["timestamp"]
            last_role = current_group[-1]["role"]
            last_name = current_group[-1]["name"]

            if msg["timestamp"] - last_msg_time > TIME_THRESHOLD:
                # Try to save out the block
                tmp_set = set()
                [tmp_set.add(msg['role']) for msg in current_group]
                if len(tmp_set) == 2:
                    # if we have two roles ('user', 'assistant'), then include
                    # else do nothing and current_group gets reset
                    grouped_messages.append(current_group)
                # reset current_group
                if curr_role == 'user':
                    if add_names: msg['content'] = f'{curr_name} said: ' + msg['content']
                    current_group = [msg]
                else:
                    current_group = []
            else:
                # Keep adding to current group
                if curr_role == last_role:
                    # Merge consecutive messages from the same role
                    if curr_role == 'assistant':
                        current_group[-1]['content'] += f'. {msg['content']}'
                    else:
                        if curr_name == last_name:
                            current_group[-1]['content'] += f'. {msg['content']}'
                        else:
                            name_content = ''
                            if add_names: name_content = f'{curr_name} said: '
                            tmp_content = f'. {name_content}' + msg['content']
                            current_group[-1]['content'] += tmp_content
                            current_group[-1]['name'] = curr_name
                else:
                    if curr_role == 'user' and add_names:
                        msg['content'] = f'{curr_name} said: ' + msg['content']
                    current_group.append(msg)

    if current_group:
        tmp_set = set()
        [tmp_set.add(msg['role']) for msg in current_group]
        if len(tmp_set) == 2:
            # if we have two roles ('user', 'assistant'), then include
            grouped_messages.append(current_group)

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
