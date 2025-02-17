from datetime import datetime
import io
import os
import shutil
import time

import numpy as np
from pydub import AudioSegment
import sounddevice as sd
import wave


class AudioRecorder:
    def __init__(self, threshold_db=-30, sample_rate=44100, channels=1):
        self.threshold_db = threshold_db
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_duration = 0.1  # seconds
        self.chunk_samples = int(self.sample_rate * self.chunk_duration)
        self.mp3_buffer = AudioSegment.empty()
        self.current_file = None
        self.recording = False
        self.silence_duration = 0

    def get_meter_string(self, db):
        """Create a visual meter string based on dB value"""
        # Define meter parameters
        meter_width = shutil.get_terminal_size().columns - 10  # Leave space for dB value
        min_db = -60
        max_db = 0

        # Calculate how many blocks to fill
        db = max(min_db, min(db, max_db))  # Clamp value
        fill_count = int((db - min_db) * meter_width / (max_db - min_db))

        # Create the meter string with different colors based on level
        meter = ""
        for i in range(meter_width):
            if i < fill_count:
                if i / meter_width < 0.7:  # Green zone
                    meter += "\033[92m█\033[0m"
                elif i / meter_width < 0.9:  # Yellow zone
                    meter += "\033[93m█\033[0m"
                else:  # Red zone
                    meter += "\033[91m█\033[0m"
            else:
                meter += "░"

        return f"{meter} {db:>5.1f}dB"


    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Status: {status}")

        # Convert to float32 if not already
        audio_data = indata.copy()
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Calculate volume in dB
        rms = np.sqrt(np.mean(audio_data**2))
        db = 20 * np.log10(rms) if rms > 0 else -100

        print("\033[A\033[K" + self.get_meter_string(db))

        # Convert numpy array to wav bytes
        bytes_io = io.BytesIO()
        with wave.open(bytes_io, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(self.sample_rate)
            wf.writeframes((audio_data * 32767).astype(np.int16))

        # Convert wav bytes to AudioSegment and add to buffer
        bytes_io.seek(0)
        segment = AudioSegment.from_wav(bytes_io)

        if db > self.threshold_db:
            if not self.recording:
                self.start_new_recording()
            self.silence_duration = 0

            self.mp3_buffer += segment

            # Check file size and create new file if needed
            if len(self.mp3_buffer.raw_data) >= 50 * 1024 * 1024:  # 50MB
                self.save_current_file()
                self.start_new_recording()
        else:
            self.silence_duration += self.chunk_duration
            if self.recording:
                if self.silence_duration <= 2.0:  # Keep up to 2 seconds of silence
                    self.mp3_buffer += segment

    def start_new_recording(self):
        self.recording = True
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_file = f"recording_{timestamp}.mp3"
        self.mp3_buffer = AudioSegment.empty()
        # print(f"Started new recording: {self.current_file}")

    def save_current_file(self):
        print(f'\033[A\033[K saving file')
        if self.mp3_buffer and self.current_file:
            os.makedirs("/Users/john.wang/Documents/00\ my\ outputs", exist_ok=True)
            filepath = os.path.join("recordings", self.current_file)
            self.mp3_buffer.export(filepath, format="mp3")
            # print(f"Saved recording: {filepath}")
            self.mp3_buffer = AudioSegment.empty()

    def start_recording(self, device_id):
        try:
            with sd.InputStream(
                device=device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self.audio_callback,
                blocksize=self.chunk_samples
            ):
                # print("Recording started. Press Ctrl+C to stop.")
                while True:
                    time.sleep(1)

        except KeyboardInterrupt:
            print("\nRecording stopped.")
            if self.recording:
                self.save_current_file()
        except Exception as e:
            print(f"Error: {e}")


def get_bluetooth_device():
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if 'Samson RXD wireless receiver' == device['name']:
            return i
    return None


def main():
    device_id = get_bluetooth_device()
    if device_id is None:
        print(f'Samson mic device not found')
        return
    device = sd.query_devices(device_id)

    print(f"Found device: {device['name']}")

    """
    Samson Device
    {
        'name': 'Samson RXD wireless receiver',
        'index': 0,
        'hostapi': 0,
        'max_input_channels': 1,
        'max_output_channels': 0,
        'default_low_input_latency': 0.004583333333333333,
        'default_low_output_latency': 0.01,
        'default_high_input_latency': 0.013916666666666667,
        'default_high_output_latency': 0.1,
        'default_samplerate': 48000.0
    }
    """
    recorder = AudioRecorder(
        threshold_db=-50,
        sample_rate=device['default_samplerate'],
        channels=device['max_input_channels'],
    )
    recorder.start_recording(device_id)


if __name__ == "__main__":
    main()
