import time

from ginette.i2c import I2C


GO_TO_RGB = 0x6e
FADE_TO_RGB = 0x63
FADE_TO_HSB = 0x68
FADE_TO_RANDOM_RGB = 0x43
FADE_TO_RANDOM_HSB = 0x48
PLAY_LIGHT_SCRIPT = 0x70
STOP_SCRIPT = 0x6f
SET_FADE_SPEED = 0x66
SET_TIME_ADJUST = 0x74
GET_CURRENT_RGB = 0x67
WRITE_SCRIPT_LINE = 0x57
READ_SCRIPT_LINE = 0x52
SET_SCRIPT_LENGTH_AND_REPEATS = 0x4c
SET_BLINKM_ADDRESS = 0x41
GET_BLINKM_ADDRESS = 0x61
GET_BLINKM_FIRMWARE_VERSION = 0x5a
SET_STARTUP_PARAMETERS = 0x42


class BlinkMScripts(object):
    STARTUP = 0
    RGB = 1
    WHITE_FLASH = 2
    RED_FLASH = 3
    GREEN_FLASH = 4
    BLUE_FLASH = 5
    CYAN_FLASH = 6
    MAGENTA_FLASH = 7
    YELLOW_FLASH = 8
    BLACK = 9
    HUE_CYCLE = 10
    MOOD_LIGHT = 11
    VIRTUAL_CANDLE = 12
    WATER_REFLECTIONS = 13
    OLD_NEON = 14
    THE_SEASONS = 15
    THUNDERSTORM = 16
    STOP_LIGHT = 17
    MORSE_CODE = 18


class BlinkM(object):
    def __init__(self, addr=0x09):
        self.addr = addr

    def stop_script(self):
        with I2C() as bus:
            bus.write_byte(self.addr, STOP_SCRIPT)

    def reset(self):
        with I2C() as bus:
            bus.write_byte(self.addr, STOP_SCRIPT)
            bus.write_byte(self.addr, FADE_TO_RGB)
            bus.write_byte(self.addr, 0)
            bus.write_byte(self.addr, 0)
            bus.write_byte(self.addr, 0)

    def fade_to(self, r=0, g=0, b=0):
        with I2C() as bus:
            bus.write_byte(self.addr, FADE_TO_RGB)
            bus.write_byte(self.addr, r)
            bus.write_byte(self.addr, g)
            bus.write_byte(self.addr, b)

    def play_script(self, script_number, repeat=0, start_line=0):
        with I2C() as bus:
            bus.write_byte(self.addr, PLAY_LIGHT_SCRIPT)
            bus.write_byte(self.addr, script_number)
            bus.write_byte(self.addr, repeat)
            bus.write_byte(self.addr, start_line)
