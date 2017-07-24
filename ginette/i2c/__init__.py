import smbus


class I2C(object):
    def __init__(self, bus=1):
        self.bus = bus

    def __enter__(self):
        self._bus = smbus.SMBus(self.bus)
        return self._bus

    def __exit__(self, *args):
        self._bus.close()
