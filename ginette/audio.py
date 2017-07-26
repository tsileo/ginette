from subprocess import Popen, PIPE
import logging

import pyaudio

log = logging.getLogger('ginette.audio')


class AudioPlayer(object):

    def __init__(self, config=None):
        self.config = config = {}

    def play_mp3(self, data):
        """Play the given mp3 bytes."""
        p = Popen(['mpg321', '-'], stdin=PIPE, stderr=PIPE)
        p.communicate(input=data)
        p.wait()


class AudioStream(object):

    def __init__(self, config=None):
        self.config = config or {}
        self.pyaudio = pyaudio.PyAudio()
        self.device_name = self.config.get('device_name')
        self._stream = None

    def _get_device_by_name(self, name):
        if name is None:
            return None

        device_index = None
        for i in range(self.pyaudio.get_device_count()):
            dev = self.pyaudio.get_device_info_by_index(i)
            name = dev['name'].encode('utf-8')
            if name.lower().find(name) >= 0 and dev['maxInputChannels'] > 0:
                return i

        return device_index

    def stream(self):
        if self._stream:
            return self._stream

        self._stream = self.pyaudio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            output=False,
            frames_per_buffer=1024,
            input_device_index=self._get_device_by_name(self.device_name),
        )

        return self._stream

    def start(self):
        stream = self.stream()
        if stream.is_stopped():
            stream.start_stream()

    def stop(self):
        stream = self.stream()
        if not stream.is_stopped():
            stream.stop_stream()

    def read(self, num_frames):
        return self.stream().read(num_frames)

    def close(self):
        if self._stream:
            self._stream.close()
