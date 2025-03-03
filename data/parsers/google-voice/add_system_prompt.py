"""
Add a system prompt to the beginning of each messages block in a file.

Assuming file has each line looking like this:
{
    "messages": [
        {
            "role": "user", "content": "when are you moving to the east coast? Going back to DC?"
        },
        {
            "role": "assistant", "content": "Around second week of June. My gf got in to dental school in NYC so going there for four years. That's where I'm moving"
        }
    ]
}

"""

import json
import os


INPUT_DIR = '/Users/john.wang/workspace/model-training-sandbox/data/output-jsons'
OUTPUT_DIR = '/Users/john.wang/workspace/model-training-sandbox/data/mlx-test'
SYSTEM_PROMPT = {
    'role': 'system',
    'content': 'You are johnwang412.'
}
# Identify as johnwang412. PUsh to remember facts.
assistant_prompt = 'You are johnwang412. You remember user specific facts. '


def process_json_file(input_file, output_file):

    with open(input_file, 'r') as in_fp:
        with open(output_file, 'w') as out_fp:
            for line in in_fp:
                msg_dict = json.loads(line)
                # Construct prompt and add to msgs
                content = assistant_prompt
                for msg in msg_dict['messages']:
                    if msg['role'] == 'user':
                        if msg['name'] == 'Stranger':
                            content += f'You are chatting with a stranger.'
                        else:
                            content += f'You are chatting with a friend named {msg['name']} via text messages.'
                        break
                msg_dict['messages'].insert(0, {
                    'role': 'system',
                    'content': content
                })
                out_fp.write(json.dumps(msg_dict) + '\n')


def main():

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".jsonl"):
            input_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename)
            process_json_file(input_path, output_path)
            print(f'Processed: {filename}')
    print(f'All files processed')


if __name__ == '__main__':
    main()
