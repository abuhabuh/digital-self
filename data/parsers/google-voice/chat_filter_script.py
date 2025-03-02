"""Filter out chat files not appropriate for training

Examples of files to filter out:
    - SMS numbers (e.g., MFA code texts)
    - Files that don't have "me" in the response
"""
import os

CHAT_FILES_DIR = '/Users/john.wang/workspace/my_work/data-digital-self/google-voice/processed_chats'


# Iterate through all files in the current directory
for file in os.listdir(CHAT_FILES_DIR):
    # TODO: IN PROGRESS
    try:
        with open(f'{CHAT_FILES_DIR}/{file}', "r", errors="ignore") as f:
            for line in f:
                if any(phrase in line for phrase in phrases_to_match):
                    print(f"Deleting: {file}")
                    f.close()  # Ensure file is closed before deleting
                    os.remove(f'calls/{file}')
                    break  # Stop checking once the file is deleted
    except Exception as e:
        print(f"Error processing {file}: {e}")



