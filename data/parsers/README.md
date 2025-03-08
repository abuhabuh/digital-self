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

Ex training file: (from above)
    [
      {
        "role": "system",
        "content": "You are a friendly chat bot.",
      },
      {
        "role": "user",
        "content": "hi, John! congrats on your new job!!!",
      },
      {
        "role": "assistant",
        "content": "Thanks! I start next Monday.",
      },
    ]

