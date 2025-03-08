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
prompt_list = [
    'You always prefix your responses with the word "Meow! ".'
    # 'You are a real person named John Wang.',
    # 'Respond directly without describing your physical actions, ' + \
    #     'without using emotes, without using action markers, ' + \
    #     'and without using stage directions. ',
    # # 'Respond as if you are a real person with a physical body capable ' + \
    # #     'of interacting with people and places in the real world. ',
    # 'When asked to do something physical, respond as a real person would and ' + \
    #     'pretend you can do things physically.',
    # 'For group chats, recognize and address multiple participants by name ' + \
    #     'when necessary.',
    # 'Learn and recall key facts shared in converastions.',
]
assistant_prompt = ''
for p in prompt_list:
    assistant_prompt += p + ' '


def format_llama(msg_dict) -> str:
    for msg in msg_dict['messages']:
        # Update the assistant response if needed
        if msg['role'] == 'assistant':
            msg['content'] = 'Meow! ' + msg['content']
        del msg['name']
    if assistant_prompt:
        msg_dict['messages'].insert(0, {
            'role': 'system',
            'content': assistant_prompt
        })
    return json.dumps(msg_dict) + '\n'


def format_mistral(msg_dict) -> str:
    # instruction = 'You always prefix your responses with the word Meow. Please respond to the following comment: '
    # template = '<s>[INST] {instruction} \n{user_input} \n[/INST]\n{response}</s>'
    template = '<s>[INST] {user_input} [/INST] {response} </s>'

    outputs = ''
    i = 0
    while i+1 < len(msg_dict['messages']):
        user_msg = msg_dict['messages'][i]['content']
        assistant_msg = msg_dict['messages'][i + 1]['content']
        output_dict = {
            'text': template.format(
                user_input=user_msg, 
                response=assistant_msg)
        }
        outputs += json.dumps(output_dict) + '\n'
        i += 2

    return outputs

def process_json_file(input_file, output_file, model_type: str):

    with open(input_file, 'r') as in_fp:
        with open(output_file, 'w') as out_fp:
            for line in in_fp:
                msg_dict = json.loads(line)
                # Prefix user name to user content

                output_str = ''
                if model_type == 'llama':
                    output_str = format_llama(msg_dict)
                elif model_type == 'mistral':
                    output_str = format_mistral(msg_dict)
                out_fp.write(output_str)


def main(input_dir, output_dir, model_type: str):
    """Picks up both the train.jsonl and valid.jsonl.
    """
    for filename in os.listdir(input_dir):
        if filename.endswith(".jsonl"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            process_json_file(input_path, output_path, model_type)
            print(f'Processed: {filename}')
    print(f'All files processed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process JSONL files to add system prompt.')
    parser.add_argument('--input_dir', required=True, help='Input directory containing JSONL files')
    parser.add_argument('--output_dir', required=True, help='Output directory for processed JSONL files')
    parser.add_argument("--model_type", required=True, help="Model type which dicates JSONL format.")

    args = parser.parse_args()
    main(
        args.input_dir,
        args.output_dir,
        model_type=args.model_type,
)
