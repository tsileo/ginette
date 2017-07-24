import time

from ginette.i2c import I2C


class SHT30(object):
    def __init__(self, addr=0x45, bus=1):
        self.addr = addr

    def get_temp_and_humid(self):
        with I2C() as bus:
            # SHT30 address, 0x44(68)
            # Send measurement command, 0x2C(44)
            #       0x06(06)    High repeatability measurement
            bus.write_i2c_block_data(self.addr, 0x2C, [0x06])

            time.sleep(0.5)

            data = bus.read_i2c_block_data(self.addr, 0x00, 6)
            temp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
            # fTemp = cTemp * 1.8 + 32
            humid = 100 * (data[3] * 256 + data[4]) / 65535.0
            return (temp, humid)
