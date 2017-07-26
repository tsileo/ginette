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
from ginette.tts.aws_polly import HTTPolly

log = logging.getLogger('ginette.core')

Config.load()

class GinetteError(Exception):
    """Base `Exception` for all Ginette related error."""

player = AudioPlayer()
polly = HTTPolly(player)
temp = Temperature()
sht30 = SHT30()
blinkm = BlinkM()


class Ginette(object):
    def __init__(self, modules=None):
        self.ongoing = None
        self.last_wakeup = None
        self.modules = modules or []

    def register_module(self, module):
        self.modules.append(module)

    def new_ctx(self):
        ctx = Context(polly)
        ctx.sht30 = sht30
        ctx.blinkm = blinkm
        return ctx

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
        self.blinkm = blinkm
        blinkm.reset()
        stream = AudioStream({'device_nam': 'respeaker'})
        self._engine = CMUSphinx(stream)
        while 1:
            blinkm.reset()
            ctx = self.new_ctx()
            print('keyphrase spotting', self.ongoing)
            self._engine.keyphrase_spotting_mode()
            # TODO detect_hotword (with a custom abc)
            kout = self._engine.detect()
            if kout is None:
                continue
            blinkm.fade_to(g=255)
            self.wakeup()
            self.stop_ongoing()
            self._engine.lm_mode()
            out = self._engine.detect(timeout=5)
            while out is not None and self.since_last_wakeup() < 30:
                ctx.build(out[0], self._engine, self._engine._stream)
                if not self.hyp_callback(out[0], ctx):
                    out = None
                else:
                    out = self._engine.detect(timeout=5)
            continue

    def hyp_callback(self, hypstr, ctx):
        print('hyp_callback', hypstr)

        self.blinkm.play_script(BlinkMScripts.GREEN_FLASH)
        if 'musique' in hypstr or 'radio' in hypstr:
            print('RADIO')
            try:
                self.start_ongoing('mpg321', '-g', '80', 'http://generationfm.ice.infomaniak.ch/generationfm-high.mp3')
            except GinetteError:
                pass
            self.blink.play_script(BlinkMScripts.WATER_REFLECTIONS)
            self._engine.keyphrase_stop_mode()
            out = self._engine.detect(timeout=5)
            while out is None:
                out = self._engine.detect(timeout=5)
                print(out)
            return False
        print(ctx)
        print(ctx.hypstr)

        for module in self.modules:
            print(module)
            if module.match(ctx):
                print(module, 'matched')
                module.do(ctx)
                break

        return True

print(AVAILABLE_MODULES)
print(temp.config)
g = Ginette(modules=[temp, Time()])
g.start()
