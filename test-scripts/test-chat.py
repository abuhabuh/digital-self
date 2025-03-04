import json

from ollama import chat


model_name = 'john-chat-llama:6'
# model_name = 'john-chat-mistral-4'

prefix = ''
prefix += 'Respond in the style of johnwang412. '
prefix += 'Respond without disclaimers that you are an LLM or a machine. ' \
        'Respond as if you have a physical body and are able to do things ' \
        'a real person would do in the world. '
prefix += 'You answer directly without describing actions you are doing, emotions you feel, or stage directions. '
prefix += """
"""

msgs = [
    {"role": "system", "content": prefix},
]


#for i in range(0,5):
#    msgs = [{
#        'role': 'user', 'content': prefix + 'let\'s go out just the two of us'
#    }]
#    print(f'Running: {msgs}')
#    response = chat(model_name, messages=msgs)
#    print(response['message']['content'])
#    print('')

print(f'Initial prompt msgs: {json.dumps(msgs, indent=2)}')

while True:
    user_input = input('Prompt: ')
    content = ''
    prefix = ''
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

