import torch
import torchaudio
import numpy as np
from pydub import AudioSegment
import tempfile
import os
from scipy.io import wavfile
import argparse

def load_silero_vad():
    """Load the Silero VAD model."""
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                model='silero_vad',
                                force_reload=False)

    (get_speech_timestamps,
     save_audio,
     read_audio,
     VADIterator,
     collect_chunks) = utils

    return model, get_speech_timestamps, read_audio

def convert_mp3_to_wav(mp3_path):
    """Convert MP3 to WAV format."""
    audio = AudioSegment.from_mp3(mp3_path)

    # Create temporary WAV file
    temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    audio.export(temp_wav.name, format='wav')

    return temp_wav.name

def process_audio(input_path, output_path, threshold=0.5, sample_rate=16000):
    """Process audio file to keep only speech segments."""
    # Load the VAD model
    model, get_speech_timestamps, read_audio = load_silero_vad()
    model.eval()

    # Convert MP3 to WAV if needed
    if input_path.lower().endswith('.mp3'):
        wav_path = convert_mp3_to_wav(input_path)
    else:
        wav_path = input_path

    # Read and resample audio
    wav = read_audio(wav_path, sampling_rate=sample_rate)

    # Get speech timestamps
    speech_timestamps = get_speech_timestamps(
        wav,
        model,
        threshold=threshold,
        sampling_rate=sample_rate
    )

    # Create empty audio array
    result = np.zeros_like(wav.numpy())

    # Fill in speech segments
    silence_gap = 2 * sample_rate
    current_position = 0
    for ts in speech_timestamps:
        start = ts['start']
        end = ts['end']
        result[current_position:current_position+(end-start)] = wav[start:end]
        current_position += (end-start) + silence_gap
    # Trim end
    result = result[:current_position]

    # Save processed audio
    temp_wav_output = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    wavfile.write(temp_wav_output.name, sample_rate, result)

    # Convert back to MP3 if output is MP3
    if output_path.lower().endswith('.mp3'):
        audio = AudioSegment.from_wav(temp_wav_output.name)
        audio.export(output_path, format='mp3')
    else:
        # If output should be WAV, just copy the temp file
        os.rename(temp_wav_output.name, output_path)

    # Clean up temporary files
    if input_path.lower().endswith('.mp3'):
        os.unlink(wav_path)
    if output_path.lower().endswith('.mp3'):
        os.unlink(temp_wav_output.name)

def main():
    parser = argparse.ArgumentParser(description='Extract speech segments from audio file.')
    parser.add_argument('input_path', help='Path to input audio file')
    parser.add_argument('output_path', help='Path to output audio file')
    parser.add_argument('--threshold', type=float, default=0.5,
                      help='Speech detection threshold (0.0 to 1.0)')
    parser.add_argument('--sample_rate', type=int, default=16000,
                      help='Sample rate for processing')

    args = parser.parse_args()

    process_audio(args.input_path, args.output_path,
                 threshold=args.threshold,
                 sample_rate=args.sample_rate)

if __name__ == "__main__":
    main()

