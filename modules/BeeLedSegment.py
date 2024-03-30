from micropython import const
from machine import Pin
from time import sleep_us, sleep_ms


class BeeLedSegment(object):
    """Library for quad 7-segment LED modules based on the TM1637 LED driver."""

    TM1637_CMD1 = const(64)  # 0x40 data command
    TM1637_CMD2 = const(192)  # 0xC0 address command
    TM1637_CMD3 = const(128)  # 0x80 display control command
    TM1637_DSP_ON = const(8)  # 0x08 display on
    TM1637_DELAY = const(10)  # 10us delay between clk/dio pulses
    # msb is the decimal point or the colon depending on your display
    TM1637_MSB = const(128)

    # 0-9, a-z, blank, dash, star
    _SEGMENTS = bytearray(
        b'\x3F\x06\x5B\x4F\x66\x6D\x7D\x07\x7F\x6F\x77\x7C\x39\x5E\x79\x71\x3D\x76\x06\x1E\x76\x38\x55\x54\x3F\x73\x67\x50\x6D\x78\x3E\x1C\x2A\x76\x6E\x5B\x00\x40\x63')

    def __init__(self, port: tuple[int, int], brightness=7) -> None:
        """
        @desc: Define Led 7 Segments module
        @requires: led 7 segments module
        @args:
            - port: connected to BeeBrain through PORTx with x in [1, 6]
            - brightness: brightness of segments led [0-7]
        @return:
            None
        """
        self.clk = Pin(port[0])
        self.dio = Pin(port[1])

        if not 0 <= brightness <= 7:
            raise ValueError("Brightness out of range")
        self._brightness = brightness

        self.clk.init(Pin.OUT, value=0)
        self.dio.init(Pin.OUT, value=0)
        sleep_us(self.TM1637_DELAY)

        self._write_data_cmd()
        self._write_dsp_ctrl()

    def _start(self):
        self.dio(0)
        sleep_us(self.TM1637_DELAY)
        self.clk(0)
        sleep_us(self.TM1637_DELAY)

    def _stop(self):
        self.dio(0)
        sleep_us(self.TM1637_DELAY)
        self.clk(1)
        sleep_us(self.TM1637_DELAY)
        self.dio(1)

    def _write_data_cmd(self):
        # automatic address increment, normal mode
        self._start()
        self._write_byte(self.TM1637_CMD1)
        self._stop()

    def _write_dsp_ctrl(self):
        # display on, set brightness
        self._start()
        self._write_byte(self.TM1637_CMD3 |
                         self.TM1637_DSP_ON | self._brightness)
        self._stop()

    def _write_byte(self, b):
        for i in range(8):
            self.dio((b >> i) & 1)
            sleep_us(self.TM1637_DELAY)
            self.clk(1)
            sleep_us(self.TM1637_DELAY)
            self.clk(0)
            sleep_us(self.TM1637_DELAY)
        self.clk(0)
        sleep_us(self.TM1637_DELAY)
        self.clk(1)
        sleep_us(self.TM1637_DELAY)
        self.clk(0)
        sleep_us(self.TM1637_DELAY)

    def brightness(self, val=None):
        """
        @desc: Set the display brightness
        @requires: led 7 segments module
        @args:
            - val: value of brightness [0-7]
        @returns:
            None
        """
        # brightness 0 = 1/16th pulse width
        # brightness 7 = 14/16th pulse width
        if val is None:
            return self._brightness
        if not 0 <= val <= 7:
            raise ValueError("Brightness out of range")

        self._brightness = val
        self._write_data_cmd()
        self._write_dsp_ctrl()

    def _write(self, segments, pos=0):
        """
        @desc: Display up to 6 segments moving right from a given position.
               The MSB in the 2nd segment controls the colon between the 2nd and 3rd segments.
        """
        if not 0 <= pos <= 5:
            raise ValueError("Position out of range")
        self._write_data_cmd()
        self._start()

        self._write_byte(self.TM1637_CMD2 | pos)
        for seg in segments:
            self._write_byte(seg)
        self._stop()
        self._write_dsp_ctrl()

    def encode_digit(self, digit):
        """
        @desc: Convert a character 0-9, a-f to a segment.
        """
        return self._SEGMENTS[digit & 0x0f]

    def encode_string(self, string):
        """
        @desc: Convert an up to 4 character length string containing 0-9, a-z, space, dash, star to an array of segments, matching the length of the source string.
        """
        segments = bytearray(len(string))
        for i in range(len(string)):
            segments[i] = self.encode_char(string[i])
        return segments

    def encode_char(self, char):
        """
        @desc: Convert a character 0-9, a-z, space, dash or star to a segment.
        """
        o = ord(char)
        if o == 32:
            return self._SEGMENTS[36]  # space
        if o == 42:
            return self._SEGMENTS[38]  # star/degrees
        if o == 45:
            return self._SEGMENTS[37]  # dash
        if o >= 65 and o <= 90:
            return self._SEGMENTS[o-55]  # uppercase A-Z
        if o >= 97 and o <= 122:
            return self._SEGMENTS[o-87]  # lowercase a-z
        if o >= 48 and o <= 57:
            return self._SEGMENTS[o-48]  # 0-9
        raise ValueError(
            "Character out of range: {:d} '{:s}'".format(o, chr(o)))

    def hex(self, val: str):
        """
        @desc: Display a hex value 0x0000 through 0xffff, right aligned.
        @requires: led 7 segments module
        @args:
            - val: hex value to display 
        @returns:
            None
        """
        string = '{:04x}'.format(val & 0xffff)
        self._write(self.encode_string(string))

    def number(self, num: int) -> None:
        """
        @desc: Display a numeric value -999 through 9999, right aligned.
        @requires: led 7 segments module
        @args:
            - num: number to display
        @returns:
            None
        """
        # limit to range -999 to 9999
        num = max(-999, min(num, 9999))
        string = '{0: >4d}'.format(num)
        self._write(self.encode_string(string))

    def numbers(self, num1: int, num2: int, colon=True) -> None:
        """
        @desc: Display two numeric values -9 through 99, with leading zeros and separated by a colon.
        @requires: led 7 segments module
        @args:
            - num1: 1st number. Value in range [-9, 99]
            - num2: 2nd number. Value in range [-9, 99]
            - colon: display : between num1 and num2 if True. Default by True
        @return:
            None
        """
        num1 = max(-9, min(num1, 99))
        num2 = max(-9, min(num2, 99))
        segments = self.encode_string('{0:0>2d}{1:0>2d}'.format(num1, num2))
        if colon:
            segments[1] |= 0x80  # colon on
        self._write(segments)

    def temperature(self, num: float) -> None:
        """
        @desc: Display temperature with oC/oF
        @requires: led 7 segments module
        @args:
            - num: temperature value. Value in range [-9, 99] else display LO (low) or HI (hight)
        @returns:
            None
        """
        if num < -9:
            self.show('lo')  # low
        elif num > 99:
            self.show('hi')  # high
        else:
            string = '{0: >2d}'.format(num)
            self._write(self.encode_string(string))
        self._write([self._SEGMENTS[38], self._SEGMENTS[12]], 2)  # degrees C

    def show(self, string: str, colon=False) -> None:
        """
        @desc: Display a string with/without colon.
        @requires: led 7 segments module
        @args:
            - string: string to display
            - colon: dipslay : or not. Defaul by False
        @returns:
            None
        """
        segments = self.encode_string(string)
        if len(segments) > 1 and colon:
            segments[1] |= 128
        self._write(segments[:4])

    def scroll(self, string: str, delay=250) -> None:
        """
        @desc: Display a string with scroll mode
        @requires: led 7 segments module
        @args:
            - string: string to display
            - delay: sroll delay in ms
        @return:
            None
        """
        segments = string if isinstance(
            string, list) else self.encode_string(string)
        data = [0] * 8
        data[4:0] = list(segments)
        for i in range(len(segments) + 5):
            self._write(data[0+i:4+i])
            sleep_ms(delay)

    def display(self, string: str) -> None:
        """
        @desc: Display a string. If length of message > 4 characters -> change to scroll mode
        @requires: led 7 segments module
        @args:
            - string: string to display
        @return:
            None
        """
        string = '{0: >4}'.format(string)
        if len(string) <= 4:
            self.show(string)
        else:
            self.scroll(string)

    def clear(self):
        """
        @desc: Clear all segments of module
        @requires: led 7 segments module
        @args:
            None
        @return:
            None
        """
        self._write([0, 0, 0, 0])


# class Led7SegmentsDecimal(BeeLedSegment):

#     """Library for quad 7-segment LED modules based on the TM1637 LED driver.

#     This class is meant to be used with decimal display modules (modules
#     that have a decimal point after each 7-segment LED).
#     """
#     TM1637_MSB = const(128)

#     def encode_string(self, string):
#         """Convert a string to LED segments.

#         Convert an up to 4 character length string containing 0-9, a-z,
#         space, dash, star and '.' to an array of segments, matching the length of
#         the source string."""
#         segments = bytearray(len(string.replace('.', '')))
#         j = 0
#         for i in range(len(string)):
#             if string[i] == '.' and j > 0:
#                 segments[j-1] |= self.TM1637_MSB
#                 continue
#             segments[j] = self.encode_char(string[i])
#             j += 1
#         return segments
