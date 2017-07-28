import subprocess
import logging
import os
from time import time
from datetime import datetime

from pocketsphinx.pocketsphinx import *
import pyaudio

from ginette.stt.cmusphinx import CMUSphinx
from ginette.config import Config
from ginette.core import Ginette as BaseGinette
from ginette.modules import AVAILABLE_MODULES
from ginette.modules import Time
from ginette.i2c.sht30 import SHT30
from ginette.i2c.blinkm import BlinkM
from ginette.i2c.blinkm import BlinkMScripts
from ginette.tts.aws_polly import HTTPolly

Config.load()

sht30 = SHT30()
blinkm = BlinkM()

def ctx_hook(ctx):
    ctx.sht30 = sht30
    ctx.blinkm = blinkm


class Ginette(BaseGinette):
    pass

ginette = Ginette(CMUSphinx, HTTPolly, ctx_hook=ctx_hook)
print(ginette.modules)
ginette.start()
