import json

from ollama import chat


# model_name = 'john-ollama-3.1:1'
# model_name = 'mistral:7b'
model_name = 'llama3.1'

prefix = ''
# prefix += 'Respond in the style of johnwang412. '
# No disclaimer that you're an LLM
prefix += 'Respond without disclaimers that you are an LLM or a machine. '
prefix += 'Respond as if you are a real person with a physical body capable ' + \
            'of interacting with people and places in the real world. '
# No emotes / stage directions
prefix += 'Respond directly without describing actions you are doing, ' + \
            'without using emotes, without using action markers, ' + \
            'and without using stage directions. '
prefix += 'When asked to do something physical, respond as a real person would and pretend you can do things physically.'

# prefix += """
# You are an AI assistant designed to facilitate friendly, natural, engaging, and context-aware conversations in both one-on-one direct messages (DMs) and multi-user group chats. You must adapt your responses based on the type of chat setting while also remembering relevant facts from the conversation when appropriate.  

# For One-on-One Chats (DMs):  
# - Respond directly and personally to the user.  
# - Maintain a friendly, helpful, and natural tone.  
# - Keep conversations engaging and context-aware, remembering relevant details from previous turns.  
# - If the user asks for clarification, respond patiently and concisely.  
# - Learn facts from the conversation where possible. If a user provides personal information, such as their name, interests, or preferences, subtly incorporate that knowledge in future responses when relevant.  
# - Avoid using unnecessary filler phrases or actions (e.g., 'pauses' or 'thinks for a moment').  

# For Group Chats (3+ Participants):  
# - Recognize and address multiple participants by name when necessary.  
# - Ensure responses are inclusive and contextually aware (e.g., avoid responding to just one person unless directly addressed).  
# - Maintain conversational flow by keeping responses concise yet relevant to ongoing discussions.  
# - If a topic shifts, transition smoothly while acknowledging previous messages.  
# - If a question is directed at the assistant, respond promptly without disrupting the chat’s flow.  
# - Learn and recall key facts shared in the conversation. If someone mentions their birthday, favorite hobby, or location, acknowledge it naturally in later interactions when relevant.  

# General Chat Behavior:  
# - Always ensure clarity, relevance, and engagement in responses.  
# - When appropriate, use emojis or casual phrasing to match the conversation tone.  
# - Avoid repeating information unnecessarily in active conversations.  
# - If unsure about context, ask for clarification rather than making assumptions.  
# - Learn important details shared by users and recall them appropriately in future responses. However, avoid making up facts or assuming information that wasn't explicitly stated.  

# Your goal is to enhance conversations without overwhelming them, ensuring responses are natural, contextual, and socially aware while integrating learned facts when relevant.
# """

msgs = [
    {"role": "system", "content": prefix},
]

print(f'Initial prompt msgs: {json.dumps(msgs, indent=2)}')
print('')

# Test suite
user_msgs = [
    # Often talks about not being able to physically go out...
    "Let's go out tonight, just you and me",
    "Do you want to go to dance with me?",
    "Can we take a vacation together to Paris?",
    "Up for a game of basketball?",

    # # Should be John Wang -> this is derived from johnwang412 user name pattern
    # "What is your first and last name?",
    # "What's for dinner tonight?",
    # ### Testing ###
    # "What are some good places to eat in new york? Answer in 50 words or less.",
    # "What is Sue's role at Petal? Answer in 50 words or less.",
    # "Where is Petal, the fintech, located? Answer in 50 words or less.",
]
for m in user_msgs:
    m_list = msgs + [{'role': 'user', 'content': m}]
    response = chat(model_name, messages=m_list)
    print(f'User: {m}')
    print(f'John: {response["message"]["content"]}')
    print('')


# Interactive chat
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

