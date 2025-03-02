import io
import time
from datetime import datetime
import os
import shutil
import pdb

import sounddevice as sd
import numpy as np
from pydub import AudioSegment
import wave


class AudioRecorder:
    def __init__(self, threshold_db=-30, sample_rate=44100, channels=1, amplification=1.0):
        self.threshold_db = threshold_db
        self.sample_rate = sample_rate
        self.channels = channels
        self.amplification = amplification
        self.chunk_duration = 0.1  # seconds
        self.chunk_samples = int(self.sample_rate * self.chunk_duration)
        self.mp3_buffer = AudioSegment.empty()
        self.current_file = None
        self.recording = False
        self.silence_duration = 0
        self.stream = None
        self.device_id = None
        self.running = False
        self.last_device_name = None
        # Whether we've written audio to the buffer (and not just silence)
        self.wrote_audio = False

    def get_bluetooth_device(self):
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if 'Samson RXD wireless receiver' == device['name']:
                self.last_device_name = device['name']
                return i
        raise ValueError("No Bluetooth input device found")

    def get_meter_string(self, db):
        meter_width = shutil.get_terminal_size().columns - 10
        min_db = -60
        max_db = 0

        db = max(min_db, min(db, max_db))
        fill_count = int((db - min_db) * meter_width / (max_db - min_db))

        meter = ""
        for i in range(meter_width):
            if i < fill_count:
                if i / meter_width < 0.7:
                    meter += "\033[92m█\033[0m"
                elif i / meter_width < 0.9:
                    meter += "\033[93m█\033[0m"
                else:
                    meter += "\033[91m█\033[0m"
            else:
                meter += "░"

        return f"{meter} {db:>5.1f}dB"

    def audio_callback(self, indata, frames, time, status):
        if status:
            if isinstance(status, sd.CallbackAbort):
                print("\nDevice disconnected. Attempting to reconnect...")
                self.handle_disconnect()
                return
            print(f"\nStatus: {status}")

        if not self.recording:
            self.start_new_recording()

        try:
            # Convert to float32 if not already
            audio_data = indata.copy()
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # Calculate volume in dB
            rms = np.sqrt(np.mean(audio_data**2))
            db = 20 * np.log10(rms) if rms > 0 else -100

            # Print the meter
            print("\033[A\033[K" + self.get_meter_string(db))

            # Convert numpy array to wav bytes
            bytes_io = io.BytesIO()
            with wave.open(bytes_io, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes((audio_data * 32767).astype(np.int16))

            # Convert wav bytes to AudioSegment and add to buffer
            bytes_io.seek(0)
            segment = AudioSegment.from_wav(bytes_io)

            if db > self.threshold_db:
                self.wrote_audio = True
                # Amplify the audio if there's something to record
                audio_data = np.clip(audio_data * self.amplification, -1.0, 1.0)

                self.silence_duration = 0
                self.mp3_buffer += segment

            else:
                self.silence_duration += self.chunk_duration
                if self.silence_duration > 2.0:
                    if len(self.mp3_buffer.raw_data) >= 135 * 1024 * 1024:
                        self.save_current_file()
                        self.start_new_recording()
                if self.recording:
                    if self.silence_duration <= 2.0:
                        self.mp3_buffer += segment

        except Exception as e:
            print(f"\nError in audio callback: {e}")
            self.handle_disconnect()

    def handle_disconnect(self):
        """Handle device disconnection and initiate reconnection"""
        if self.stream:
            print(f'Device disconnect detected - closing stream and trying reconnect')
            self.stream.close()
        self.stream = None

        self.reconnect_device()

    def reconnect_device(self):
        """Attempt to reconnect to the Bluetooth device"""
        while self.running:
            try:
                # Reset sounddevice because it retains memory of initial device connection
                sd._terminate()
                sd._initialize()
                # Try to find the same device that was previously connected
                devices = sd.query_devices()
                found_device = False
                for i, device in enumerate(devices):
                    if self.last_device_name and self.last_device_name == device['name']:
                        self.device_id = i
                        found_device = True
                        break

                if not found_device:
                    return

                # Test the device by creating a new stream
                self.create_stream()
                print(f"\nReconnected to device: {sd.query_devices(self.device_id)['name']}")
                print()  # Add an extra line for the meter
                return

            except Exception as e:
                print(f"\rAttempting to reconnect... ({e})", end="")
                time.sleep(1)

    def create_stream(self):
        """Create a new audio input stream"""
        if self.stream:
            self.stream.close()

        self.stream = sd.InputStream(
            device=self.device_id,
            channels=self.channels,
            samplerate=self.sample_rate,
            callback=self.audio_callback,
            blocksize=self.chunk_samples
        )
        self.stream.start()

    def start_new_recording(self):
        self.wrote_audio = False
        self.recording = True
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.current_file = f"{timestamp}_recording.mp3"
        self.mp3_buffer = AudioSegment.empty()
        print(f"\nStarted new recording: {self.current_file}")
        print()  # Add an extra line for the meter

    def save_current_file(self):
        if not self.wrote_audio:
            return

        out_dir = '/Users/john.wang/Documents/00 my outputs'
        if self.mp3_buffer and self.current_file:
            os.makedirs(out_dir, exist_ok=True)
            filepath = os.path.join(out_dir, self.current_file)
            self.mp3_buffer.export(filepath, format="mp3")
            print(f"\nSaved recording: {filepath}")
            self.mp3_buffer = AudioSegment.empty()

    def start_recording(self):
        try:
            self.running = True
            self.device_id = self.get_bluetooth_device()
            print(f"Using device: {sd.query_devices(self.device_id)['name']}")

            self.create_stream()

            while self.running:
                if not self.stream or not self.stream.active:
                    self.handle_disconnect()
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nRecording stopped.")
            self.running = False
            if self.recording:
                self.save_current_file()
            if self.stream:
                self.stream.close()
        except Exception as e:
            print(f"Error: {e}")
            self.running = False
            if self.stream:
                self.stream.close()

if __name__ == "__main__":
    recorder = AudioRecorder(threshold_db=-50, amplification=2)
    recorder.start_recording()
