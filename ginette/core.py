import subprocess
import logging
import os
from time import time
from datetime import datetime

from pocketsphinx.pocketsphinx import *
import pyaudio
from ginette.audio import AudioStream
from ginette.audio import AudioPlayer
from ginette.stt.cmusphinx import CMUSphinx
from ginette.config import Config
from ginette.modules import AVAILABLE_MODULES
from ginette.modules import Time
from ginette.modules import Temperature
from ginette.modules import Context
from ginette.i2c.sht30 import SHT30
from ginette.i2c.blinkm import BlinkM
from ginette.i2c.blinkm import BlinkMScripts
# from ginette.tts.aws_polly import HTTPolly

log = logging.getLogger('ginette.core')


class GinetteError(Exception):
    """Base `Exception` for all Ginette related error."""


# TODO(tsileo): also load stt_engine and tss_engine from config 
# TODO(tsileo): hooks for the led


class Ginette(object):
    def __init__(self, stt_engine_cls, tts_engine_cls, ctx_hook=None):
        self.stt_engine_cls = stt_engine_cls
        self.tts_engine_cls = tts_engine_cls
        self.tts_engine = self.tts_engine_cls()
        self.ctx_hook = ctx_hook
        self.last_wakeup = None
        self.modules = []
        self._load_modules()

    def _load_modules(self):
        for module in Config.ROOT.get('modules', []):
            if not module in AVAILABLE_MODULES:
                print('Missing module', module)
            mod_cls = AVAILABLE_MODULES[module]
            self.modules.append(mod_cls(Config.module(module)))

    def wakeup(self):
        self.last_wakeup = time()

    def since_last_wakeup(self):
        return time() - self.last_wakeup

    def start(self):
        stream = AudioStream()
        self.stt_engine = self.stt_engine_cls()
        self.stt_engine.set_stream(stream)
        while 1:
            ctx = Context(self.tts_engine, self.stt_engine, stream)
            if callable(self.ctx_hook):
                self.ctx_hook(ctx)

            print('keyphrase spotting')
            self.stt_engine.keyphrase_spotting_mode()
            # TODO detect_hotword (with a custom abc)?
            out = self.stt_engine.detect()
            self.wakeup()

            self.stt_engine.lm_mode()
            out = self.stt_engine.detect(timeout=5)
            ctx.set_hypstr(out[0])

            for module in self.modules:
                if module.match(ctx):
                    module.do(ctx)
                    break
