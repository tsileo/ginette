import abc


class Context(object):
    def __init__(self, tts):
        self.tts = tts

    def build(self, hypstr, engine, stream):
        self.hypstr = hypstr
        self.engine = engine
        self.stream = stream


# TODO metaclass module registery for config matching
class Module(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config=None):
        self.config = config or {}

    @abc.abstractmethod
    def match(self, ctx):
        pass

    @abc.abstractmethod
    def do(self, ctx):
        pass


class Temperature(Module):

    def match(self, ctx):
        if 'temp\xc3rature' in ctx.hypstr:
            return True
        return False

    def do(self, ctx):
        temp, humid = ctx.sht30.get_temp_and_humid()
        ctx.tts.text_to_speech(
            'temperature {:.2f} et {:.2f} humide'.format(temp, humid)
        )
