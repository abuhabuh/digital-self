"""Create directory structure for training data processing
"""
import os
import argparse


DIR_STRUCTURE = [
    {
        'dir_name': '0-raw',
        'sub_dir': [
            {'dir_name': 'chat', 'sub_dir': []},
            {'dir_name': 'email', 'sub_dir': []},
            {'dir_name': 'text', 'sub_dir': []},
        ]
    },
    {
        'dir_name': '1-normalized',
        'sub_dir': [
            {'dir_name': 'chat', 'sub_dir': []},
            {'dir_name': 'email', 'sub_dir': []},
            {'dir_name': 'text', 'sub_dir': []},
        ]
    },
    {
        'dir_name': '2-staging',
        'sub_dir': [
            {'dir_name': 'chat', 'sub_dir': []},
            {'dir_name': 'text', 'sub_dir': []},
        ]
    },
    {
        'dir_name': '2-staging',
        'sub_dir': [],
    }
]


def create_directories(root_path, directories):
    """
    Create directories and subdirectories based on a nested JSON structure.

    Args:
        root_path (str): The root directory path
        directories (list): A list of dictionaries with directory structures
    """
    for dir_obj in directories:
        dir_name = dir_obj.get('dir_name')
        sub_dirs = dir_obj.get('sub_dir', [])

        # Create the main directory
        dir_path = os.path.join(root_path, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")
        else:
            print(f"Directory already exists: {dir_path}")

        # Recursively create subdirectories
        if sub_dirs:
            create_directories(dir_path, sub_dirs)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Create directory structure from JSON definition')
    parser.add_argument('--root_dir', required=True, help='Root directory path')

    args = parser.parse_args()

    # Create root directory if it doesn't exist
    if not os.path.exists(args.root_dir):
        os.makedirs(args.root_dir)
        print(f"Created root directory: {args.root_dir}")

    # Create the directory structure
    create_directories(args.root_dir, DIR_STRUCTURE)
    print("Directory structure creation complete.")

if __name__ == "__main__":
    main()