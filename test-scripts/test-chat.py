import json

from ollama import chat


def main():
    """
    TODO: NOT WORKING _ REFACTORED A LOT

    TESTS:
    <s> [INST] Wanna come to dinner? [/INST] No, I gotta go out from 6 to 9 tonight. </s> [INST] How come? And when exactly [/INST]
    <s> [INST] Wanna come to dinner? [/INST] No, I gotta go out from 6 to 9 tonight. </s> <s> [INST] How come? And when exactly? [/INST]
    """

    # model_name = 'mistral:7b'
    model_name = 'john-mistral-3.1-cat:1'

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


if __name__ == '__main__':
    main()