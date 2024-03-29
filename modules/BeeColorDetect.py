from micropython import const
from machine import Pin, I2C

import time
import ustruct


class BeeColorDetect():

    # const = lambda x:x

    _COMMAND_BIT = const(0x80)

    _REGISTER_ENABLE = const(0x00)
    _REGISTER_ATIME = const(0x01)

    _REGISTER_AILT = const(0x04)
    _REGISTER_AIHT = const(0x06)

    _REGISTER_ID = const(0x12)

    _REGISTER_APERS = const(0x0c)

    _REGISTER_CONTROL = const(0x0f)

    _REGISTER_SENSORID = const(0x12)

    _REGISTER_STATUS = const(0x13)
    _REGISTER_CDATA = const(0x14)
    _REGISTER_RDATA = const(0x16)
    _REGISTER_GDATA = const(0x18)
    _REGISTER_BDATA = const(0x1a)

    _ENABLE_AIEN = const(0x10)
    _ENABLE_WEN = const(0x08)
    _ENABLE_AEN = const(0x02)
    _ENABLE_PON = const(0x01)

    _GAINS = (1, 4, 16, 60)
    _CYCLES = (0, 1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60)

    def __init__(self, port: tuple[int, int], gain=1, integration_time=50) -> None:
        """
        @desc: Define ColorSensor module
        @requires: color sensor module
        @args:
            - port: connected to BeeBrain through PORTx with x: [1-6]
            - gain (optional): Set the gain for the internal ADCs to work better in certain low-light conditions. 
                               Value must in [1, 4, 16, 60].
            - integration_time (optional): The amount of time the light sensor is exposed. 
                                           Value must in [2.4, 24, 50, 101, 120, 154, 180, 199, 240, 300, 360, 401, 420, 480, 499, 540, 600, 614] miliseconds
        @returns:
            None
        """
        self.i2c = I2C(scl=Pin(port[0]), sda=Pin(port[1]))
        self.address = 0x29
        self._active = False
        self._set_integration_time(integration_time)
        self._set_gain(gain)
        sensor_id = self._sensor_id()
        if sensor_id not in (0x44, 0x10):
            raise RuntimeError("wrong sensor id 0x{:x}".format(sensor_id))

    def _register8(self, register, value=None):
        register |= self._COMMAND_BIT
        if value is None:
            return self.i2c.readfrom_mem(self.address, register, 1)[0]
        data = ustruct.pack('<B', value)
        self.i2c.writeto_mem(self.address, register, data)

    def _register16(self, register, value=None):
        register |= self._COMMAND_BIT
        if value is None:
            data = self.i2c.readfrom_mem(self.address, register, 2)
            return ustruct.unpack('<H', data)[0]
        data = ustruct.pack('<H', value)
        self.i2c.writeto_mem(self.address, register, data)

    def active(self, value=None):
        if value is None:
            return self._active
        value = bool(value)
        if self._active == value:
            return
        self._active = value
        enable = self._register8(self._REGISTER_ENABLE)
        if value:
            self._register8(self._REGISTER_ENABLE, enable | self._ENABLE_PON)
            time.sleep_ms(3)
            self._register8(self._REGISTER_ENABLE,
                            enable | self._ENABLE_PON | self._ENABLE_AEN)
        else:
            self._register8(self._REGISTER_ENABLE,
                            enable & ~(self._ENABLE_PON | self._ENABLE_AEN))

    def _sensor_id(self):
        return self._register8(self._REGISTER_SENSORID)

    def _set_integration_time(self, value=None):
        if value is None:
            return self._integration_time
        value = min(614.4, max(2.4, value))
        cycles = int(value / 2.4)
        self._integration_time = cycles * 2.4
        return self._register8(self._REGISTER_ATIME, 256 - cycles)

    def _set_gain(self, value):
        if value is None:
            return self._GAINS[self._register8(self._REGISTER_CONTROL)]
        if value not in self._GAINS:
            raise ValueError("gain must be 1, 4, 16 or 60")
        return self._register8(self._REGISTER_CONTROL, self._GAINS.index(value))

    def _valid(self):
        return bool(self._register8(self._REGISTER_STATUS) & 0x01)

    def _read(self, raw=False):
        was_active = self.active()
        self.active(True)
        while not self._valid():
            time.sleep_ms(int(self._integration_time + 0.9))
        data = tuple(self._register16(register) for register in (
            self._REGISTER_RDATA,
            self._REGISTER_GDATA,
            self._REGISTER_BDATA,
            self._REGISTER_CDATA,
        ))
        self.active(was_active)
        if raw:
            return data
        return self._temperature_and_lux(data)

    def _temperature_and_lux(self, data):
        r, g, b, c = data
        x = -0.14282 * r + 1.54924 * g + -0.95641 * b
        y = -0.32466 * r + 1.57837 * g + -0.73191 * b
        z = -0.68202 * r + 0.77073 * g + 0.56332 * b
        d = x + y + z
        try:
            n = (x / d - 0.3320) / (0.1858 - y / d)
            cct = 449.0 * n**3 + 3525.0 * n**2 + 6823.3 * n + 5520.33
        except ValueError:
            cct = 0
        return cct, y

    def _threshold(self, cycles=None, min_value=None, max_value=None):
        if cycles is None and min_value is None and max_value is None:
            min_value = self._register16(self._REGISTER_AILT)
            max_value = self._register16(self._REGISTER_AILT)
            if self._register8(self._REGISTER_ENABLE) & self._ENABLE_AIEN:
                cycles = self._CYCLES[self._register8(
                    self._REGISTER_APERS) & 0x0f]
            else:
                cycles = -1
            return cycles, min_value, max_value
        if min_value is not None:
            self._register16(self._REGISTER_AILT, min_value)
        if max_value is not None:
            self._register16(self._REGISTER_AIHT, max_value)
        if cycles is not None:
            enable = self._register8(self._REGISTER_ENABLE)
            if cycles == -1:
                self._register8(self._REGISTER_ENABLE,
                                enable & ~(self._ENABLE_AIEN))
            else:
                self._register8(self._REGISTER_ENABLE,
                                enable | self._ENABLE_AIEN)
                if cycles not in self._CYCLES:
                    raise ValueError("invalid persistence cycles")
                self._register8(self._REGISTER_APERS,
                                self._CYCLES.index(cycles))

    def _interrupt(self, value=None):
        if value is None:
            return bool(self._register8(self._REGISTER_STATUS) & self._ENABLE_AIEN)
        if value:
            raise ValueError("interrupt can only be cleared")
        self.i2c.writeto(self.address, b'\xe6')

    def get_color(self, color: str) -> int:
        """
        @desc: get red, green, blue color from sensor
        @requires: color sensor module
        @args:
            - color: get specific color value: ("red", "green", "blue", "all")
        @returns:
            - value of color
        """
        red, green, blue = self.get_all_colors_in_rgb()
        if color == "red":
            return red
        elif color == "green":
            return green
        elif color == "blue":
            return blue
        return None

    def get_all_colors_in_rgb(self) -> (int, int, int):
        """
        @desc: get colors in rgb from sensor
        @requires: color sensor module
        @args:
            None
        @returns:
            - tuples of (reg, green, blue) value
        """
        data = self._read(raw=True)
        r, g, b, c = data
        red = int(r / c * 255)
        green = int(g / c * 255)
        blue = int(b / c * 255)
        return (red, green, blue)

    def html_hex(self) -> str:
        """
        @desc: get color in hex from sensor
        @requires: color sensor module
        @args:
            None
        @returns:
            - str: color in hex value
        """
        r, g, b = self.get_all_colors_in_rgb()
        return "{0:02x}{1:02x}{2:02x}".format(int(r), int(g), int(b))

    def _rgb_to_hsv(self, r: int, g: int, b: int) -> (float, float, float):
        """
        @desc: convert rgb to hsv
        @requires: color sensor module
        @args:
            - red: red value
            - green: green value
            - blue: blue value
        @returns:
            - tuples: h, s, v value
        """
        r, g, b = r/255.0, g/255.0, b/255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx-mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g-b)/df) + 360) % 360
        elif mx == g:
            h = (60 * ((b-r)/df) + 120) % 360
        elif mx == b:
            h = (60 * ((r-g)/df) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = (df/mx)*100
        v = mx*100
        return h, s, v

    def _detect_color(self, red: int, green: int, blue: int) -> str:
        """
        @desc: Detect color name with rgb value
        @requires: color sensor module
        @args:
            - red: red value
            - green: green value
            - blue: blue value
        @returns:
            - str: color name
        """
        h, s, v = self._rgb_to_hsv(red, green, blue)

        if 0 <= h <= 2.0:
            return "red"
        elif 60.0 <= h <= 120.0 and s >= 40.0:
            return "green"
        elif 180.0 <= h <= 240.0:
            return "blue"
        else:
            return "none"

    def is_color(self, color: str) -> bool:
        """
        @desc: Check if color is deteced
        @requires: color sensor module
        @args:
            - color: color name
        @returns:
            - bool: True if color name is detected
        """
        r, g, b = self.get_all_colors_in_rgb()
        if color == self._detect_color(r, g, b):
            return True
        else:
            return False
