import yaml


class Config(object):
    """Config singleton"""

    ROOT = {}
    _loaded = False

    @classmethod
    def load(cls, path='config.yaml'):
        with open(path, 'rb') as f:
            cls.ROOT = yaml.load(f)
            cls._loaded = True

    @classmethod
    def _check_loaded(cls):
        if not cls._loaded:
            raise Exception('config must be loaded first')

    @classmethod
    def get(cls, name, default=None):
        cls._check_loaded()
        return cls.ROOT.get(name, default)

    @classmethod
    def module(cls, name, default=None):
        cls._check_loaded()
        return cls.ROOT.get('modules', {}).get(name, default)


class WithConfig(object):
    def __init__(self):
        self.config = Config.get(self.__class__.__name__)
        self.init()
