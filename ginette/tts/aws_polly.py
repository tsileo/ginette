import abc
from subprocess import Popen, PIPE

import requests

from ginette.audio import AudioPlayer


PLAYER = AudioPlayer()

class TTSEngine(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, player=None, config=None):
        self.player = player or PLAYER
        self.config = config or {}

    @abc.abstractmethod
    def do_text_to_speech(self, text):
        pass

    def text_to_speech(self, text):
        return self.player.play_mp3(self.do_text_to_speech(text))


class HTTPolly(TTSEngine):
    """https://github.com/tsileo/httpolly backend"""

    DEFAULT_API_URL = 'http://localhost:8015'
    DEFAULT_VOICE_ID = 'Celine'

    def do_text_to_speech(self, text):
        resp = requests.post(
            self.config.get('api_url', self.DEFAULT_API_URL),
            json={'text': text, 'voice_id': self.DEFAULT_VOICE_ID},
        )
        resp.raise_for_status()
        return resp.content
