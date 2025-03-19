"""
Transform staging train.jsonl and valid.jsonl files into formats that are
compatible with the model being fine tuned using the right input format
where possible.

Consolidates all train and valid jsonl files into a single pair of files.
File entries will have the format {'text': 'training text'}
"""

import json
import os
import argparse

from transformers import AutoTokenizer


def process_messages(tokenizer: AutoTokenizer, msg_dict: dict) -> str:
    msgs = msg_dict['messages']
    if not msgs:
        return ''
    if msgs[-1]['role'] == 'user':
        # If chat block ends with input from user, remove that
        msgs.pop()
    # Prefix user name to user content
    text_output = tokenizer.apply_chat_template(
        msg_dict['messages'],
        tokenize=False,
        # Generation prompt not helpful in training
        add_generation_prompt=False,
        return_tensors='pt',  # return PyTorch tensors
    )
    return text_output


def process_json_file(input_file, output_file, tokenizer: AutoTokenizer):
    """Process input files based on their formats
    """

    with open(input_file, 'r') as in_fp:
        with open(output_file, 'a') as out_fp:
            for line in in_fp:
                data_dict = json.loads(line)
                text_output = ''
                if 'messages' in data_dict:
                    text_output = process_messages(tokenizer, data_dict)
                elif 'text' in data_dict:
                    text_output = data_dict['text']
                else:
                    print(f'Unhandled test data format')
                output_dict = {
                    'text': text_output
                }

                out_fp.write(json.dumps(output_dict) + '\n')


def main(input_dir, output_dir, hf_model: str):
    """Picks up both the train.jsonl and valid.jsonl.
    """
    print('Processing started ...')
    tokenizer = AutoTokenizer.from_pretrained(hf_model)

    # remove train.jsonl and valid.jsonl
    for fpath in [
            os.path.join(output_dir, 'train.jsonl'),
            os.path.join(output_dir, 'valid.jsonl')
        ]:
        if os.path.exists(fpath):
            os.unlink(fpath)

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith('.jsonl'):
                input_path = os.path.join(root, filename)
                print(f'input: {input_path}')
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
