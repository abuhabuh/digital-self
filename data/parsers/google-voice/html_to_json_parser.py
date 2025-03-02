"""Purpose: Convert all google voice .html dump files to json format
for LLM fine tuning

Includes a few extra fields.
"""

import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict

def parse_html_chat(file_path):
    """
    Parse a single HTML chat file and return a list of message objects.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

    messages = []

    # Find all message divs
    for message_div in soup.find_all('div', class_='message'):
        # Extract timestamp
        timestamp = message_div.find('abbr', class_='dt')['title']

        # Extract phone number
        phone_link = message_div.find('a', class_='tel')
        phone_number = phone_link['href'].replace('tel:', '') if phone_link else None

        # Check if message is from "Me"
        is_me = message_div.find('abbr', class_='fn') and message_div.find('abbr', class_='fn').text.strip() == 'Me'

        # Extract message content
        content = message_div.find('q').text.strip()

        message = {
            "role": "assistant" if is_me else "user",
            "content": content,
            "phone": phone_number,
            "timestamp": timestamp
        }

        messages.append(message)

    return messages

def process_directory(directory_path):
    """
    Process all HTML files in the directory and group them by prefix.
    """
    # Dictionary to store messages grouped by prefix
    grouped_messages = defaultdict(list)

    # Walk through directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.html'):
            # Get prefix (everything before first '-')
            prefix = filename.split('-')[0]

            # Parse file and add messages to appropriate group
            file_path = os.path.join(directory_path, filename)
            messages = parse_html_chat(file_path)
            grouped_messages[prefix].extend(messages)

    return grouped_messages

def save_grouped_messages(grouped_messages, output_directory):
    """
    Save each group of messages to a separate JSON file.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Save each group to a file
    for prefix, messages in grouped_messages.items():
        output_file = os.path.join(output_directory, f"{prefix.strip()}.json")

        # Sort messages by timestamp before saving
        sorted_messages = sorted(messages, key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')))

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sorted_messages, f, indent=2)

def main():
    # Directory containing HTML files
    input_directory = "chat_logs"  # Change this to your input directory
    output_directory = "processed_chats"  # Change this to your desired output directory

    # Process all files and group by prefix
    grouped_messages = process_directory(input_directory)

    # Save grouped messages to files
    save_grouped_messages(grouped_messages, output_directory)

if __name__ == "__main__":
    main()
