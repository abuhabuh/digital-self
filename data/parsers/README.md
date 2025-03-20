# Overview

Various parsing scripts for inbound data (google voice, slack, etc.)

# Parser components

## 0_raw

Scripts for processing raw output files into normalized output files.

Ex input file: Google Voice HTML output file with chat info inside

## 1_normalized

Scripts for processing normalized output files into formats appropriate
for further processing into final training format (e.g., adding system
instructions).

Ex input file:
    [
      {
        "role": "user",
        "content": "hi, John!",
        "timestamp": "2013-09-30T12:22:21.000+00:00",
        "name": "Jillian"
      },
      {
        "role": "user",
        "content": "congrats on your new job!!!",
        "timestamp": "2013-09-30T12:23:06.000+00:00",
        "name": "Jillian"
      },
      {
        "role": "assistant",
        "content": "Thanks!",
        "timestamp": "2013-09-30T15:33:48.000+00:00",
        "name": "John Wang"
      },
      {
        "role": "assistant",
        "content": "I start next Monday.",
        "timestamp": "2013-09-30T15:33:48.000+00:00",
        "name": "John Wang"
      },
    ]

## 2_staging

Scripts for processing staging files and doing final formatting and system
prompting so they are ready for training for the appropriate models.

Chats are formatted so they alternate user, assistant, user, etc. Group chats
have multiple people merged as needed.

Ex input file: (from above)
    [
      {
        "role": "user",
        "content": "hi, John! congrats on your new job!!!",
        "timestamp": "2013-09-30T12:23:06.000+00:00",
        "name": "Jillian"
      },
      {
        "role": "assistant",
        "content": "Thanks! I start next Monday.",
        "timestamp": "2013-09-30T15:33:48.000+00:00",
        "name": "John Wang"
      },
    ]

## 3_training

No scripts as this should represent the final output directory. Scripts are in
the proper training format with appropriate instructions, formats, etc.

Gemma sample:

  ```
  {"text": "<bos><start_of_turn>user\nawesome, thats a good amount of time. you have interviews and/or network connections lined up?<end_of_turn>\n<start_of_turn>model\nworking on that now. actually already have an offer from a company that's based there and  DC, lol. i want to do my due diligence and make sure i find the right project / culture fit<end_of_turn>\n<start_of_turn>user\ncool - its nice going there with at least one backup option. the trip sounds exciting, heh<end_of_turn>\n<start_of_turn>model\nyea dude, def come out for a wk if u have time. course, if everything works out and i move there, you're always welcome to crash<end_of_turn>\n"}
  ```

Llama sample:
  ```
  {"text": "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\nawesome, thats a good amount of time. you have interviews and/or network connections lined up?<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\nworking on that now. actually already have an offer from a company that's based there and  DC, lol. i want to do my due diligence and make sure i find the right project / culture fit<|eot_id|><|start_header_id|>user<|end_header_id|>\n\ncool - its nice going there with at least one backup option. the trip sounds exciting, heh<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\nyea dude, def come out for a wk if u have time. course, if everything works out and i move there, you're always welcome to crash<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"}
  ```
