import argparse
import datetime
import json
import os
import subprocess

import ollama


def get_lines(outfile: str) -> int:
    try:
        result = subprocess.run(
            ['wc', '-l', outfile],
            capture_output=True,
            text=True,
            )
        output = result.stdout.strip()
        return int(output.split()[0]) # Extract the number from the output string
    except Exception as e:
        print(str(e))
        return 0


def main(input_dir: str, output_dir: str, ollama_model: str):



    prompt = """
    <text>
    {source_text}
    </text>

    Summarize the text above.
    Repeat this {num_summaries} times with anywhere from 150 to {summary_length_words} words in each summary.
    Summarize a different portion of the text each time. Replace "I" with "johnwang412".
    Do not mention the reference text explicitly in the summary.
    The output has to be a single list of summary strings that can be parsed by a computer program.
    """
    # prompt = """
    # <text>
    # {source_text}
    # </text>
    # The text above is authored by johnwang412.
    # Rewrite the text above in the third person with at least 250 words
    # and no more than {summary_length_words} words.
    # Do not mention the reference text explicitly in the summary.
    # Repeat this {num_summaries} times. Focus on a different theme or portion of the text each time.
    # The output should be a json list where each element in the list is a simple string
    # containing the summary.
    # An example output:
    # [
    # 'summary text 1 with a summary of the source text',
    # 'summary text 2 with summary information',
    # ]
    # """
    summary_length_words = 400
    summaries_per_run = 10
    total_summaries = 4000

    print(f'---')
    print(f'prompt: {prompt}')
    print(f'length: {summary_length_words}')
    print(f'total_summaries: {total_summaries}')
    print(f'---')
    print('')

    for filename in os.listdir(input_dir):

        with open(input_dir+'/'+filename, 'r') as fp:
            source_text = fp.read()

        out_file = output_dir + '/' + filename
        num_summaries = get_lines(out_file)
        write_mode = 'a' if num_summaries > 0 else 'w'
        with open(out_file, write_mode) as out_fp:
            while num_summaries <= total_summaries:
                print(f'> {datetime.datetime.now().strftime("%H:%M:%S")}: running generate ...')
                # result = ollama.generate(
                #     ollama_model, prompt=prompt.format(
                #         source_text=source_text,
                #         summary_length_words=summary_length_words,
                #         num_summaries=summaries_per_run
                #         ))
                response = ollama.chat(
                    ollama_model,
                    messages=[
                        {
                            'role': 'user',
                            'content': prompt.format(
                                source_text=source_text,
                                summary_length_words=summary_length_words,
                                num_summaries=summaries_per_run
                            )
                        }
                    ]
                )
                content = response['message']['content']
                l = content.find('[')
                r = content.rfind(']')
                if l == -1 or r == -1:
                    continue
                try:
                    summaries_list = json.loads(content[l:r+1])
                    for s in summaries_list:
                        if type(s) == str:
                            out_fp.write(s+'\n')
                        else:
                            out_fp.write(s['summary']+'\n')  # assume we're getting a dict with 'summary' key
                    num_summaries += summaries_per_run
                except Exception as e:
                    print(f'parse / write exception: {e}')
                    print(f'{content[l:r+1]}')
                print(f'num summaries: {num_summaries}')
    print(f'')
    print(f'Complete. Num lines in output file: {num_summaries}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process JSONL files to add system prompt.')
    parser.add_argument('--input_dir', required=True, help='Input directory containing JSONL files')
    parser.add_argument('--output_dir', required=True, help='Output directory for processed JSONL files')
    parser.add_argument("--ollama_model", required=True, help="Ollama model string.")

    args = parser.parse_args()
    main(
        args.input_dir,
        args.output_dir,
        ollama_model=args.ollama_model,
    )