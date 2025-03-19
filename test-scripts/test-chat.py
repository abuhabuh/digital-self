import json

import ollama


def test_with_chat(hf_model: str, ollama_model: str):
    """Incomplete"""
    messages = [
        {
            'role': 'user',
            'content': 'Wanna come to dinner?'
        },
        {
            'role': 'assistant',
            'content': 'No, I gotta go out from 6 to 9 tonight.',
        },
        {
            'role': 'user',
            'content': 'How come? And when exactly?'
        },
    ]

    msgs = []
    # Interactive chat
    while True:
        user_input = input('Prompt: ')
        content = ''
        content += user_input
        msgs.append({
            'role': 'user',
            'content': content
        })

        # Run LLM
        response = chat(model_name, messages=msgs)

        # Update next thread
        msgs.append({
            'role': 'assistant',
            'content': response['message']['content']
        })

        print('')
        print(f'John: {response['message']['content']}')
        print('')


def test_with_generate(hf_model: str, ollama_model: str):

    inputs = [
        'How many years did johnwang412 work at Petal?',
        'How long were johnwang412 employed by Petal in total?',
        'When did johnwang412\'s employment at Petal begin?',
        'When did johnwang412 start working at Petal?',
        'When did johnwang412 finish working at Petal?',
        'What organization were johnwang412 affiliated with between 2018 and 2024?',
        'When did johnwang412\'s tenure at Petal end?',
        'Were johnwang412 working at Petal in 2019?',
    ]

    for input_str in inputs:
        print('')
        print(f'Input: {input_str}')
        result = ollama.generate(ollama_model, prompt=input_str)
        print(f' > resp: {result.response}')
        print('')


def main():
    """
    """
    # hf_model not used rn
    hf_model = 'mlx-community/Mistral-7B-Instruct-v0.3-4bit'
    ollama_model = 'john-openchat-3.5:1'

    print(f'Running test with hf_model: {hf_model} and ollama_model: {ollama_model}')

    test_with_generate(
        hf_model=hf_model,
        ollama_model=ollama_model,
        )


if __name__ == '__main__':
    main()