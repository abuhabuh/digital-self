"""
My Parsed Google Voice format -> Apple MLX Trainig format

Operates on output files of directory parser that parses raw html google voice
dumps. Takes the output files and formats them according to Apple MLX training
format.
"""

import os
import json
from datetime import datetime, timedelta

# Configuration
# Directory containing JSON files
INPUT_DIR = '/Users/john.wang/workspace/model-training-sandbox/data/input-jsons'
# Directory to save processed files
OUTPUT_DIR = '/Users/john.wang/workspace/model-training-sandbox/data/output-jsons'
TIME_THRESHOLD = timedelta(hours=12)  # Messages within 12 hours are grouped

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_chat_buddy_name(fpath):
    n = fpath.split('/')[-1]
    n = n.split('.')[0]
    n = n.split('-')[0]
    n = n.strip()
    if n.lower() == 'misc':
        n = 'Stranger'
    return n


def process_json_file(input_filepath, train_filepath, valid_filepath):
    chat_buddy_name = get_chat_buddy_name(input_filepath)

    # Load JSON file
    with open(input_filepath, "r") as f:
        messages = json.load(f)

    # Convert timestamps to datetime objects
    for msg in messages:
        msg["timestamp"] = datetime.fromisoformat(msg["timestamp"])
        if msg['role'] == 'user':
            msg['name'] = chat_buddy_name

    # Sort messages by timestamp
    messages.sort(key=lambda x: x["timestamp"])

    # Group messages
    grouped_messages = []
    current_group = []

    for msg in messages:
        if not current_group:
            if msg["role"] == "user":
                current_group = [msg]
            else:
                continue
        else:
            last_msg_time = current_group[-1]["timestamp"]
            last_role = current_group[-1]["role"]
            curr_role = msg["role"]

            if msg["timestamp"] - last_msg_time > TIME_THRESHOLD:
                # Try to save out the block
                tmp_set = set()
                [tmp_set.add(msg['role']) for msg in current_group]
                if len(tmp_set) == 2:
                    # if we have two roles ('user', 'assistant'), then include
                    grouped_messages.append(current_group)
                if curr_role == 'user':
                    current_group = [msg]
                else:
                    current_group = []
            else:
                # Keep adding to current group
                if curr_role == last_role:
                    current_group[-1]['content'] += f'. {msg['content']}'
                else:
                    current_group.append(msg)
    if current_group:
        tmp_set = set()
        [tmp_set.add(msg['role']) for msg in current_group]
        if len(tmp_set) == 2:
            # if we have two roles ('user', 'assistant'), then include
            grouped_messages.append(current_group)

#    # Merge consecutive messages from the same user within each group
#    transformed_groups = []
#
#    for group in grouped_messages:
#        merged_group = []
#        current_message = group[0]  # Start with the first message
#
#        for msg in group[1:]:
#            if msg["role"] == current_message["role"]:
#                # Merge content
#                current_message["content"] += ". " + msg["content"]
#            else:
#                # Append the last merged message and start a new one
#                merged_group.append({
#                    "role": current_message["role"],
#                    "content": current_message["content"],
#                    # "timestamp": current_message["timestamp"].isoformat()
#                })
#                current_message = msg
#
#        # Append the last message in the group
#        merged_group.append({
#            "role": current_message["role"],
#            "content": current_message["content"],
#            # "timestamp": current_message["timestamp"].isoformat()
#        })
#
#        transformed_groups.append(merged_group)
    for g in grouped_messages:
        for item in g:
            del item['timestamp']
            del item['phone']
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

# Process all JSON files in the input directory
train_output_path = os.path.join(OUTPUT_DIR, "train.jsonl")
valid_output_path = os.path.join(OUTPUT_DIR, "valid.jsonl")
with open(train_output_path, "w") as train_fp:
    pass
with open(valid_output_path, "w") as valid_fp:
    pass
for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".json"):
        input_path = os.path.join(INPUT_DIR, filename)
        process_json_file(input_path, train_output_path, valid_output_path)
        print(f"Processed: {filename}")

print("All files processed successfully!")

