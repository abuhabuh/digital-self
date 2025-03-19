"""
Ensure all text training data is in the same format:
{
    'text': 'text for training'
}
"""
import os
import json
import argparse
from pathlib import Path


def process_files(input_dir, output_dir):
    """
    Process all text files in input_dir and its subdirectories.
    Create train.jsonl and valid.jsonl files in output_dir.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Initialize output files
    train_file = os.path.join(output_dir, "train.jsonl")
    valid_file = os.path.join(output_dir, "valid.jsonl")

    train_count = 0
    valid_count = 0

    # Open output files
    with open(train_file, 'w', encoding='utf-8') as train_f, \
         open(valid_file, 'w', encoding='utf-8') as valid_f:

        # Walk through input directory and its subdirectories
        for root, _, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.join(root, file)

                try:
                    # Process each file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        line_count = 0
                        for line in f:
                            line = line.strip()
                            if not line:  # Skip empty lines
                                continue

                            # Create JSON object
                            json_obj = {"text": line}

                            # Every 10th line goes to valid.jsonl, the rest to train.jsonl
                            if line_count % 10 == 9:  # 0-indexed, so 9, 19, 29, etc.
                                valid_f.write(json.dumps(json_obj) + '\n')
                                valid_count += 1
                            else:
                                train_f.write(json.dumps(json_obj) + '\n')
                                train_count += 1

                            line_count += 1

                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")

    print(f"Processing complete. Created:")
    print(f"  {train_file} with {train_count} entries")
    print(f"  {valid_file} with {valid_count} entries")


def main():
    parser = argparse.ArgumentParser(description="Process text files into JSONL format")
    parser.add_argument("--input_dir", required=True, help="Directory containing input files.")
    parser.add_argument("--output_dir", required=True, help="Directory to save output files.")

    args = parser.parse_args()

    # Convert to absolute paths
    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)

    # Check if input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    process_files(input_dir, output_dir)


if __name__ == "__main__":
    main()