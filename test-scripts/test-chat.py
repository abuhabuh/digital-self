import json

from ollama import chat


model_name = 'john-chat-llama-2'
# model_name = 'john-chat-mistral-4'

prefix = 'You are johnwang412. ' + \
        'Respond without disclaimers that you are an LLM or a machine. ' \
        'Respond as if you have a physical body and are able to do things ' \
        'a real person would do in the world.'

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


while True:
    user_input = input('Prompt: ')
    content = ''
#    content += prefix
    prefix = ''
    content += user_input
    msgs.append({
        'role': 'user',
        'content': content
    })

    # Run LLM
    print(f'Running: {json.dumps(msgs, indent=2)}')
    response = chat(model_name, messages=msgs)

    # Update next thread
    msgs.append({
        'role': 'assistant',
        'content': response['message']['content']
    })

    print(response['message']['content'])

