from ollama import chat


msgs = [
    {"role": "system", "content": "You are a friendly middle aged man named johnwang412"},
]

while True:
    user_input = input('Prompt: ')
    msgs.append({
        'role': 'user',
        'content': user_input
    })
    response = chat('john-named-chat-mistral-5', messages=msgs)
    msgs.append({
        'role': 'assistant',
        'content': response['message']['content']
    })

    print(response['message']['content'])
