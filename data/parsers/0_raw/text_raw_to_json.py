"""
UNUSED - for now

Originally written to generate q&a from all journal entries
"""

import os
import json

import ollama


def main():
    """Picks up both the train.jsonl and valid.jsonl.
    """
    print('Processing started ...')

    ollama_model = 'llama3.1:latest'

    folder = '/Users/johnwang/workspace/model-training/data/0-raw/text-bio'
    prompt = ''
    # prompt += 'Generate 10 facts about the author of the following text. '
    # prompt += 'Refer to the author as johnwang412 in the facts. '
    # prompt += 'Keep the facts specific where possible. '
    # prompt += 'Format the output in a json list. '

    prompt += 'Generate 20 questions and answers about information about the author in the following text. '
    prompt += 'For each answer, include relevant details from the text where possible. '
    prompt += 'Refer to the author as johnwang412 in the output. '
    prompt += 'Format the output with the question on one line and the answer on the next line. Labeled only with "question" and "answer". '

    """Alternative prompt from https://www.youtube.com/watch?v=_GkHZQYFOGM

    <input_text>
    {input_text}
    </input_text>
    Provide {questions_per_chunk} question and answer pairs based on the text above.
    The question should include sufficient information for the answer, without the
    user having any further context. The answer need not necessarily borrow verbatim
    from the input text, but they should maintain the meaning. Vary the style and
    format of questions. Include some tricky and nuanced questions. In some answers,
    reverse the order of words compared to how they appear in the input text.
    Respond in plain text on a new line for each question and answer.
    Do not include question numbers.
    Here is an example of a question answer pair:\n\n<example>\n\n{train_sample}\n\n</example>\n\n
    """


    output_file = 'out.jsonl'
    with open(output_file, 'w') as out_fp:

        for filename in os.listdir(folder):
            if filename.endswith(".md"):
                print(f'file: {filename}')
                with open(folder + '/' + filename, 'r') as fp:
                    txt = fp.read()


                    print(input_str)
                    return
                    # result = ollama.generate(ollama_model, prompt=input_str)
                    # print('')
                    # print(f'input: {input_str}')
                    # print('')
                    # print('--------------------------------')
                    # print('')
                    print(f'res: {result.response}')

                    out_fp.write(result.response + '\n')

    print(f'All files processed')


def tmp_gen():
    print('Processing started ...')

    ollama_model = 'llama3.1:latest'
    output_file = 'out.jsonl'

    prompt = 'Generate 20 question and answer pairs. The result should be output in a json list. Each list element should be a question and answer pair in the form of a dictionary. The question’s key should be “question” and the answer’s key should be “answer”. Do not include anything in the output except the json list string. The output has to be able to be parsed by a python json.loads function call. Generate this information based on the following fact: '

    q_list = [
        'You worked at a fintech startup named Petal for 6 years from 2018 to 2024.',
        # 'You moved to San Francisco in 2013 to start working as a software engineer.',
        # 'You joined the Hillary Clinton presidential campaign in 2016 and worked there until the campaign ended.',
        # 'Shyam recommended the DC restaurant Rasika to you in 2019.',
    ]

    fact_prompt = """
<input_text>
{input_text}
</input_text>

Provide {questions_per_chunk} question and answer pairs based on the text above.
The question should include sufficient information for the answer, without the
user having any further context. The answer need not necessarily borrow verbatim
from the input text, but they should maintain the meaning. Vary the style and
format of questions. Include some tricky and nuanced questions. In some answers,
reverse the order of words compared to how they appear in the input text.

The result should be output in a json list.
Each list element should be a question and answer pair in the form of a dictionary.
The question’s key should be “question” and the answer’s key should be “answer”.
Do not include anything in the output except the json list string.
The output has to be able to be parsed by a python json.loads function call.

Here is an example of a question answer pair:\n\n<example>\n\n{train_sample}\n\n</example>\n\n
    """

    final_list = []
    output_file = 'out.jsonl'
    while len(final_list) < 1100:
        # input_str = f'{prompt} {txt}'
        input_str = fact_prompt.format(
            input_text='johnwang412 worked at Petal from 2018 to 2024.',
            questions_per_chunk='10',
            train_sample='[ {"question": "Where did johnwang412 work in 2018?", "answer": "Petal"} ]'
        )
        result = ollama.generate(ollama_model, prompt=input_str)
        l = 0
        while l < len(result.response):
            if result.response[l] == '[':
                break
            l += 1
        r = len(result.response) - 1
        while r >= 0:
            if result.response[r] == ']':
                break
            r -= 1
        # print(f'result: {result.response[l:r+1]}')
        try:
            l = json.loads(result.response[l:r+1])
        except:
            print(f'*********** could not parse *************')
            continue
        final_list += l
        print(f'final_list len: {len(final_list)}')
    with open(output_file, 'w') as out_fp:
        out_fp.write(json.dumps(final_list))


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Process JSONL files to add system prompt.')
    # parser.add_argument('--input_dir', required=True, help='Input directory containing JSONL files')
    # parser.add_argument('--output_dir', required=True, help='Output directory for processed JSONL files')
    # parser.add_argument("--hf_model", required=True, help="Model type which dicates JSONL format.")

    tmp_gen()

    # args = parser.parse_args()
    # main(
    #     # args.input_dir,
    #     # args.output_dir,
    #     # hf_model=args.hf_model,
    # )

