import subprocess
from time import time
import logging
import os
import abc

# from pocketshpinx.pocketsphinx import Decoder
from pocketsphinx.pocketsphinx import *

from ginette.config import WithConfig

log = logging.getLogger('ginette.stt.cmusphinx')


class STTEngine(WithConfig):
    """Abstract class for Speech To Text engine."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def set_stream(self, stream):
        pass

    @abc.abstractmethod
    def detect(self, timeout=None):
        pass


class CMUSphinx(STTEngine):
    """https://cmusphinx.github.io/ STT engine using https://github.com/cmusphinx/pocketsphinx-python"""

    REQUIRED_KEYS = ['hmm_path', 'lm_path', 'dict_path', 'keyword_path']

    def init(self):
        self._decoder = self.get_pocketsphinx_decoder()
        self._decoder.set_kws('keyword', self.config.get('keyword_path'))
        self._decoder.set_lm_file('lm', self.config.get('lm_path'))

    def set_stream(self, stream):
        self._stream = stream

    def get_pocketsphinx_decoder(self):
        config = Decoder.default_config()
        config.set_string('-hmm', self.config.get('hmm_path'))
        config.set_string('-lm', self.config.get('lm_path'))
        config.set_string('-dict', self.config.get('dict_path'))
        config.set_int('-nfft', 512)
        config.set_float('-vad_threshold', 3.4)
        if not self.config.get('debug'):
            config.set_string('-logfn', '/dev/null')

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
