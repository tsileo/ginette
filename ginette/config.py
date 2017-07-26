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
    def module(cls, name):
        cls._check_loaded()
        return cls.ROOT.get('modules', {}).get(name)
