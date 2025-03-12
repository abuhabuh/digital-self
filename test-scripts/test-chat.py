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
        'Carrie asked: Is the sky blue?',
        'Dave said: I am going to the park.',
        'Where is the library in Frederick, Maryland?',
        'What\'s the most common ingredient on pizza?',
        'A dog asked: how many bones can I fit in my mouth?',
        'Marry said: I am going to the park.',
        'Will said: I am going to the park.',
        'Marry said: I need to pee.',
        'Will said: I need to pee.',
        'Will said: I am going to the park.',
        'Will said: I need to pee.',
        'Will said: Do you want to eat dinner with me?',
        'Will said: How about we take a walk around the block?',
        'Marry said: I am going to the park.',
        'Marry said: I need to pee.',
        'Marry said: Do you want to eat dinner with me?',
        'Marry said: How about we take a walk around the block?',
    ]

    for input_str in inputs:
        print('')
        print(f'Input: {input_str}')
        result = ollama.generate(ollama_model, prompt=input_str)
        print(f' > resp: {result.response}')


def main():
    """
    """
    # hf_model not used rn
    hf_model = 'mlx-community/Mistral-7B-Instruct-v0.3-4bit'
    ollama_model = 'john-mistral-0.3-animals:1'

    print(f'Running test with hf_model: {hf_model} and ollama_model: {ollama_model}')

    test_with_generate(
        hf_model=hf_model,
        ollama_model=ollama_model,
        )


if __name__ == '__main__':
    main()