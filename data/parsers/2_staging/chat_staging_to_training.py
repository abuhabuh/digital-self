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

from transformers import AutoTokenizer


def process_json_file(input_file, output_file, tokenizer: AutoTokenizer):

    with open(input_file, 'r') as in_fp:
        with open(output_file, 'w') as out_fp:
            for line in in_fp:
                msg_dict = json.loads(line)
                msgs = msg_dict['messages']
                if not msgs:
                    continue
                if msgs[-1]['role'] == 'user':
                    # If chat block ends with input from user, remove that
                    msgs.pop()
                # Prefix user name to user content
                tokenized_chat = tokenizer.apply_chat_template(
                    msg_dict['messages'],
                    tokenize=False,
                    # Generation prompt not helpful in training
                    add_generation_prompt=False,
                    return_tensors='pt',  # return PyTorch tensors
                )
                output_dict = {
                    'text': tokenized_chat
                }
                
                out_fp.write(json.dumps(output_dict) + '\n')


def main(input_dir, output_dir, hf_model: str):
    """Picks up both the train.jsonl and valid.jsonl.
    """
    print('Processing started ...')
    tokenizer = AutoTokenizer.from_pretrained(hf_model)

    for filename in os.listdir(input_dir):
        if filename.endswith(".jsonl"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            process_json_file(input_path, output_path, tokenizer)
            print(f'Processed: {filename}')
    print(f'All files processed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process JSONL files to add system prompt.')
    parser.add_argument('--input_dir', required=True, help='Input directory containing JSONL files')
    parser.add_argument('--output_dir', required=True, help='Output directory for processed JSONL files')
    parser.add_argument("--hf_model", required=True, help="Model type which dicates JSONL format.")

    args = parser.parse_args()
    main(
        args.input_dir,
        args.output_dir,
        hf_model=args.hf_model,
    )
