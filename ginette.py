import subprocess
import logging
import os
from time import time

# from pocketshpinx.pocketsphinx import Decoder
from pocketsphinx.pocketsphinx import *

import pyaudio

log = logging.getLogger('ginette.core')


model_dir = "/home/pi/cmusphinx-fr-ptm-5.2/"
hmm = model_dir
lm = '/home/pi/fr-small.lm.bin'
dic = os.path.join(model_dir, "/home/pi/fr2.dic")


class SpeechRecognitionEngine(object):

    def __init__(self, stream):
        self._decoder = self.get_pocketsphinx_decoder()
        self._decoder.set_kws('keyword', 'kwd.txt')
        self._decoder.set_lm_file('lm', lm)
        self._stream = stream

    def get_pocketsphinx_decoder(self):
        config = Decoder.default_config()
        config.set_string('-hmm', hmm)
        config.set_string('-lm', lm)
        config.set_string('-dict', dic)
        config.set_string('-logfn', '/dev/null')
        config.set_int('-nfft', 512)
        config.set_float('-vad_threshold', 3.4)

        return Decoder(config)

    def keyphrase_spotting_mode(self):
        self._decoder.set_search('keyword')

    def lm_mode(self):
        self._decoder.set_search('lm')

    def detect(self, timeout=None):
        self._stream.start()
        self._decoder.start_utt()
        self._in_speech = False
        hypstr = None
        last_update = None
        start = time()
        while 1:
            try:
                buf = self._stream.read(1024)
            except Exception as exc:
                print(exc)
                self._decoder.end_utt()
		self._stream._stream = None
                return

            if not buf:
                continue

            self._decoder.process_raw(buf, False, False)
            new_hyp = self._decoder.hyp()
            if new_hyp and new_hyp.hypstr != hypstr:
                hypstr = new_hyp.hypstr
                last_update = time()
            if timeout and time() - start > timeout:
                self._decoder.end_utt()
                self._stream.stop()
                return None
            in_speech = self._decoder.get_in_speech()
            # print(self._decoder.hyp(), in_speech, self._in_speech)
            if in_speech != self._in_speech or (last_update and time() - last_update > 1):
                self._in_speech = in_speech
                if in_speech:
                    continue

                current_hyp = self._decoder.hyp()
                if current_hyp is None:
                    continue

                out = (current_hyp.hypstr, self._decoder.seg())
                print([(seg.word, seg.prob, seg.start_frame, seg.end_frame) for seg in self._decoder.seg()])
                print("Detected keyphrase, restarting search")

                self._decoder.end_utt()
                self._stream.stop()

                return out


class AudioStream(object):
    def __init__(self, device_name):
        self.pyaudio = pyaudio.PyAudio()
        self.device_name = device_name
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


class GinetteError(Exception):
    """Base `Exception` for all Ginette related error."""


class Ginette(object):
    def __init__(self):
        self.ongoing = None
        self.last_wakeup = None

    def wakeup(self):
        self.last_wakeup = time()

    def since_last_wakeup(self):
        return time() - self.last_wakeup

    def start_ongoing(self, *args, **kwargs):
        if self.ongoing is not None:
            raise GinetteError('an ongoing process is already running')

        self.ongoing = subprocess.Popen(args, **kwargs)

    def stop_ongoing(self):
        if self.ongoing is None:
            return

        self.ongoing.terminate()
        ret = self.ongoing.wait()
        log.info('ongoing process terminated with return_code=%d', ret)
        self.ongoing = None

    def start(self):
        stream = AudioStream('respeaker')
        self._engine = SpeechRecognitionEngine(stream)
        while 1:
            print('keyphrase spotting')
            self._engine.keyphrase_spotting_mode()
            kout = self._engine.detect()
            if kout is None:
                continue
            self._engine.lm_mode()
            out = self._engine.detect(timeout=5)
            while out is not None:
                out = self._engine.detect(timeout=5)
            continue

g = Ginette()
g.start()
