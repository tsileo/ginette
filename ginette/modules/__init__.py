import abc
from datetime import datetime

from ginette.config import Config


AVAILABLE_MODULES = {}


class Context(object):
    def __init__(self, tts):
        self.tts = tts

    def build(self, hypstr, engine, stream):
        self.hypstr = hypstr
        self.engine = engine
        self.stream = stream


class _ModuleMeta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        if not cls.__name__.startswith('_') and cls.__name__ != 'Module':
            AVAILABLE_MODULES[cls.__name__] = cls
        return cls


class _Meta(abc.ABCMeta, _ModuleMeta):
    pass


class Module(object):
    __metaclass__ = _Meta

    def __init__(self, extra_config=None):
        self.config = Config.module(self.name())
        if extra_config and self.config:
            self.config.update(extra_config)

    def name(self):
        return self.__class__.__name__

    @abc.abstractmethod
    def match(self, ctx):
        pass

    @abc.abstractmethod
    def do(self, ctx):
        pass


class Temperature(Module):

    def match(self, ctx):
        if 'temp\xc3\xa9rature' in ctx.hypstr:
            return True
        return False

    def do(self, ctx):
        temp, humid = ctx.sht30.get_temp_and_humid()
        ctx.tts.text_to_speech(
            'La temp\xc3\xa9rature {} est de {:.2f} degr\xc3\xa9'.format(self.config.get('name'), temp)
        )
        print('done')


class Time(Module):

    def match(self, ctx):
        if 'heure' in ctx.hypstr:
            return True
        return False

    def do(self, ctx):
        now = datetime.now()
        ctx.tts.text_to_speech(
            'Il est {} heures et {} minutes'.format(
                now.strftime('%H').lstrip('0'),
                now.strftime('%M').lstrip('0'),
            )
        )
