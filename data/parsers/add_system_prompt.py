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
import argparse


# Prompt:
assistant_prompt = ''
assistant_prompt += 'Respond in the style of johnwang412. '
assistant_prompt += 'Respond without disclaimers that you are an LLM or a machine. ' + \
    'Respond as if you are a real person with a physical body. '
assistant_prompt += 'Respond directly without describing actions you are doing, ' + \
    'without using emotes, without using action markers, ' + \
    'and without using stage directions. '
assistant_prompt += 'Respond starting with the word Meow.'


def process_json_file(input_file, output_file):

    with open(input_file, 'r') as in_fp:
        with open(output_file, 'w') as out_fp:
            for line in in_fp:
                msg_dict = json.loads(line)
                # Prefix user name to user content
                for msg in msg_dict['messages']:
                    if msg['role'] == 'assistant':
                        msg['content'] = 'Meow! ' + msg['content']
                msg_dict['messages'].insert(0, {
                    'role': 'system',
                    'content': assistant_prompt
                })
                out_fp.write(json.dumps(msg_dict) + '\n')


def main(input_dir, output_dir):

    for filename in os.listdir(input_dir):
        if filename.endswith(".jsonl"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            process_json_file(input_path, output_path)
            print(f'Processed: {filename}')
    print(f'All files processed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process JSONL files to add system prompt.')
    parser.add_argument('--input_dir', required=True, help='Input directory containing JSONL files')
    parser.add_argument('--output_dir', required=True, help='Output directory for processed JSONL files')
    args = parser.parse_args()
    main(args.input_dir, args.output_dir)
