"""
My Parsed Google Voice format -> Apple MLX Training format

Each line should contain something like:
{
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello."
        },
        {
            "role": "assistant",
            "content": "How can I assistant you today."
        }
    ]
}

Operates on output files of directory parser that parses raw html google voice
dumps. Takes the output files and formats them according to Apple MLX training
format.

Things done:
- Aggregates messages within X hours into single block
- Ensures messages alternate between user and assistant by combining
    consecutive messages from the same role
- Groups all chats found into a single training file
"""

import glob
import os
import json
from datetime import datetime, timedelta
import argparse

### Configuration
# Messages within 2 hours are grouped - msgs 2 hrs apart are likley not related
TIME_THRESHOLD = timedelta(hours=2)
# DMS_ONLY means we only process DMs and skip group msgs
DMS_ONLY = True

class MessageGroup:
    def __init__(self):
        self.group = []
        self.member_names = set()
        self.user_message_count = 0

        # Number of user messages remembered before a reply from the assistant
        # (limit this incase there is a long chain of dialogue before assistant
        # replies in the training data - e.g., slack channels where there's a
        # ton of back and forth before I reply.)
        self.consecutive_user_msg_limit = 20

    def add_message(self, msg):
        if msg['role'] == 'user':
            self.user_message_count += 1
            if self.user_message_count > self.consecutive_user_msg_limit:
                # Iterate backwards to find the first user message before an assistant message
                i = len(self.group) - 1
                i -= 19
                if i < 0:
                    raise Exception(
                        'Unexpected error: user msg cnt greater than msgs')
                if i - 1 >= 0 and self.group[i - 1]['role'] == 'user':
                    raise Exception(
                        'Unexpected error: earliest user msg is not after '
                        'assistant msg')
                # All checks pass, so pop the earliest message
                self.group.pop(i)
                self.user_message_count -= 1
        else:
            self.user_message_count = 0

        self.group.append(msg)
        self.member_names.add(msg['name'])

    def reset(self):
        self.group = []
        self.user_message_count = 0

    def is_empty(self):
        return len(self.group) == 0

    def get_last_message(self):
        return self.group[-1]

    def get_roles(self):
        return set(msg['role'] for msg in self.group)

    def get_group(self):
        return self.group

    def merge_messages(self):
        """Merge messages so that we alternate 'user', 'assistant' roles
        First message should always be from a 'user' role
        """
        if not self.group:
            return []
        is_group = len(self.member_names) > 2

        if is_group:
            self.group[0]['content'] = f'{self.group[0]["name"]} said: ' + self.group[0]['content']
        merged_group = [self.group[0]]
        for msg in self.group[1:]:
            last_msg = merged_group[-1]
            if msg["role"] == last_msg["role"]:
                if is_group and msg["role"] == "user" and msg["name"] != last_msg["name"]:
                    msg['content'] = f'{msg["name"]} said: ' + msg['content']
                    last_msg['name'] = msg['name']
                last_msg['content'] += f'. {msg["content"]}'
            else:
                if msg["role"] == "user" and is_group:
                    msg['content'] = f'{msg["name"]} said: ' + msg['content']
                merged_group.append(msg)

        self.group = merged_group
        return self.group


def process_json_file(input_filepath, train_filepath, valid_filepath):
    # Load JSON file
    with open(input_filepath, "r") as f:
        messages = json.load(f)

    # Convert timestamps to datetime objects
    for msg in messages:
        msg["timestamp"] = datetime.fromisoformat(msg["timestamp"])

    # Sort messages by timestamp
    messages.sort(key=lambda x: x["timestamp"])

    # Group messages
    grouped_messages = []
    current_group = MessageGroup()

    for msg in messages:
        curr_role = msg["role"]

        if current_group.is_empty():
            if curr_role == "user":
                current_group.add_message(msg)
            else:
                continue
        else:
            last_msg_time = current_group.get_last_message()["timestamp"]

            if msg["timestamp"] - last_msg_time > TIME_THRESHOLD:
                if len(current_group.get_roles()) == 2:
                    if not DMS_ONLY or len(current_group.member_names) == 2:
                        grouped_messages.append(current_group.merge_messages())
                current_group.reset()
                if curr_role == 'user':
                    current_group.add_message(msg)
            else:
                current_group.add_message(msg)

    if not current_group.is_empty() and len(current_group.get_roles()) == 2:
        if not DMS_ONLY or len(current_group.member_names) == 2:
            grouped_messages.append(current_group.merge_messages())

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

def main(input_dir: str, output_dir: str):
    print(f'Processing started ...')
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
            # print(f"Processed: {filename}")

    print("All files processed successfully!")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert Google Voice JSON to Apple MLX format.")
    parser.add_argument("--input_dir", required=True, help="Directory containing input JSON files.")
    parser.add_argument("--output_dir", required=True, help="Directory to save output JSONL files.")

    args = parser.parse_args()

    main(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
    )
