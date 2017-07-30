import yaml

from ginette import GinetteError


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
    REQUIRED_KEYS = []

    def __init__(self):
        self.config = Config.get(self.__class__.__name__)

        missing_keys = []
        if self.REQUIRED_KEYS and self.config is None:
            missing_keys = list(self.REQUIRED_KEYS)

        for key in self.REQUIRED_KEYS:
            if not key in self.config:
                missing_keys.append(key)

        if missing_keys:
            raise GinetteError('the following config items are missing for {}: {}'.format(
                self.__class__.__name__,
                ', '.join(missing_keys),
            ))

        self.init()
