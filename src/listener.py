""" Provides utilities for constantly monitoring a mic for sound. """

import math
import struct
import time

from sys import exit
from types import FunctionType

import pyaudio

class Listener:
    """ Listens for sound, records until silence, then returns the recorded audio. """

    # Multiplier that converts a 16 bit value to a float between 0 and 1.
    SHORT_NORMALIZE = (1.0/32768.0)

    @staticmethod
    def rms(frame, sample_width: int) -> float:
        """ Calculate the RMS for a given audio frame and sample width. """
        count = len(frame) / sample_width
        audio_format = "%dh" % (count)
        shorts = struct.unpack(audio_format, frame)

        sum_squares = 0.0
        for sample in shorts:
            normal = sample * Listener.SHORT_NORMALIZE
            sum_squares += normal * normal

        rms = math.pow(sum_squares / count, 0.5)
        return rms * 1000

    def __init__(self, on_audio: FunctionType, **kwargs):
        """ Create a new Listener object. """

        # Set defaults for arguments
        kwargs.setdefault('format', pyaudio.paInt16)
        kwargs.setdefault('channels', 1)
        kwargs.setdefault('rate', 44100)
        self.chunk = kwargs.pop('chunk', 1024)
        self.threshold = kwargs.pop('threshold', 10.0)
        self.timeout = kwargs.pop('timeout', 1.0)
        self.sample_width = pyaudio.get_sample_size(kwargs['format'])

        # Register the function called when audio is captured
        self.on_audio = on_audio

        # Save the named arguments
        self.stream_args = kwargs

        self.connection = pyaudio.PyAudio()
        self.stream = self.connection.open(input=True, **kwargs)

    def record(self):
        """ Start recording, and don't stop until there is silence. """
        rec = []
        # Create a reference to the current time.
        # This is updated on every iteration of the while loop.
        current = time.time()
        end = time.time() + self.timeout

        # Loop until there is silence:
        while current <= end:
            # Get a chunk of audio from the stream
            data = self.stream.read(self.chunk)
            # If the audio is loud enough, push our end time back
            # So we keep recording.
            if self.rms(data, self.sample_width) >= self.threshold:
                end = time.time() + self.timeout

            # Update the current time
            current = time.time()
            # And add our most recent audio chunk to the list of chunks
            rec.append(data)

        # At this point, recording has finished,
        # So call the on_audio event.
        # The list of chunks is converted to bytes.
        self.on_audio(b''.join(rec))

    def listen(self):
        """ Wait for sound, then start recording. """
        while True:
            latest = self.stream.read(self.chunk)
            rms_val = self.rms(latest, self.sample_width)
            if rms_val > self.threshold:
                self.record()

if __name__ == "__main__":
    def log(rec):
        """ Log the length of the captured audio. """
        print("Got audio {:0.2f} seconds long.".format(len(rec) / 2 / 44100))

    listener = Listener(log)

    try:
        listener.listen()
    except KeyboardInterrupt:
        exit()
