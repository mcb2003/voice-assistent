import pyaudio, math, struct, wave, time, os
from typing import Type
from types import FunctionType

class Listener:
    """ Listens for sound, records until silence, then returns the recorded audio. """

    # Multiplier that converts a 16 bit value to a float between 0 and 1.
    SHORT_NORMALIZE = (1.0/32768.0)

    @staticmethod
    def rms(frame, sampWidth: int) -> float:
        """ Calculate the RMS for a given audio frame and sample width. """
        count = len(frame) / sampWidth
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * Listener.SHORT_NORMALIZE
            sum_squares += n * n

        rms = math.pow(sum_squares / count, 0.5)
        return rms * 1000

    def __init__(self,
            onAudio: FunctionType,
        format: Type = pyaudio.paInt16,
        channels: int = 1,
        rate: int = 44100,
        sampWidth: int = 2, # Bytes (16 bits)
        chunk: int = 1024,
        threshold: float = 10,
        timeout: float = 1.0
        ):
        """ Create a new Listener object. """
        self.onAudio = onAudio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
                                      format=format,
                                      channels=channels,
                                      rate=rate,
                                      input=True,
                                      output=True,
                                  frames_per_buffer=chunk)

        # Store these values in the class so we can retrieve them later:
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.sampWidth = sampWidth
        self.threshold = threshold
        self.timeout = timeout

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
            if self.rms(data, self.sampWidth) >= self.threshold:
                end = time.time() + self.timeout

            # Update the current time
            current = time.time()
            # And add our most recent audio chunk to the list of chunks
            rec.append(data)

        # At this point, recording has finished,
        # So call the onAudio event.
        # The list of chunks is converted to bytes.
        self.onAudio(b''.join(rec))

    def listen(self):
        while True:
            input = self.stream.read(self.chunk)
            rms_val = self.rms(input, self.sampWidth)
            if rms_val > self.threshold:
                self.record()

if __name__ == "__main__":
    def log(rec):
        print("Got audio {} seconds long.".format(len(rec) / 2 / 44100))

    a = Listener(log)

    a.listen()
