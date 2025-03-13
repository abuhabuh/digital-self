import os
import json


def main():
    """Picks up both the train.jsonl and valid.jsonl.
    """
    print('Processing started ...')

    folder = '/Users/johnwang/workspace/model-training/data/0-raw/text-bio'

    out_json = []
    for filename in os.listdir(folder):
        if filename.endswith(".md"):
            print(f'file: {filename}')
            with open(folder + '/' + filename, 'r') as fp:
                txt = fp.read()
                out_json.append({'text': txt})

    output_file = 'out.jsonl'
    with open(output_file, 'w') as out_fp:
        for item in out_json:
            out_fp.write(json.dumps(item) + '\n')


    print(f'All files processed')


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Process JSONL files to add system prompt.')
    # parser.add_argument('--input_dir', required=True, help='Input directory containing JSONL files')
    # parser.add_argument('--output_dir', required=True, help='Output directory for processed JSONL files')
    # parser.add_argument("--hf_model", required=True, help="Model type which dicates JSONL format.")

    # args = parser.parse_args()
    main(
        # args.input_dir,
        # args.output_dir,
        # hf_model=args.hf_model,
    )

