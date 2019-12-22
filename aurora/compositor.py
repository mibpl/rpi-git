from led_config import LEDConfig
from keyboard_config import KeyboardConfig
import protocol
from client import connect
import time
import typing
import itertools

def key_to_normalized_position(note):
    return (note - KeyboardConfig.low_note) / (KeyboardConfig.high_note - KeyboardConfig.low_note + 1)

def key_to_closest_pixel(note):
    ratio = key_to_normalized_position(note)
    n = round(ratio * (LEDConfig.high_light - LEDConfig.low_light + 1) + LEDConfig.low_light)
    return int(n)

def clip_color(color):
    def clip(x):
        return int(min(255, max(0, x)))
    r, g, b = color
    return (clip(r), clip(g), clip(b))

ColorT = typing.Tuple[int, int, int]

BLUE = (0, 0, 255)
LIGHT_BLUE = (0, 0, 10)

GREEN = (0, 255, 0)
LIGHT_GREEN = (0, 10, 0)

YELLOW = (80, 40, 0)
YELLOW_LIGHT = (8, 6, 0)

class ShadePalette(typing.NamedTuple):
    normal: ColorT
    light: ColorT

BLUES = ShadePalette(normal=BLUE, light=LIGHT_BLUE)
GREENS = ShadePalette(normal=GREEN, light=LIGHT_GREEN)
YELLOWS = ShadePalette(normal=YELLOW, light=YELLOW_LIGHT)

class Compositor:
    def new_canvas(self) -> typing.List[ColorT]:
        return LEDConfig.total_lights * [(0, 0, 0)]

    def __init__(self) -> None:
        self.canvas = self.new_canvas()
        self.pressed_keys = []
        self.hl_keys = []

    def add_pressed_keys(self, keys):
        self.pressed_keys = list(keys)

    def add_hl_keys(self, keys):
        self.hl_keys = list(keys)

    def overlay_keys(self, keys, shades: ShadePalette):
        for key in keys:
            n = key_to_closest_pixel(key)
            self.canvas[n] = shades.normal

    def color_test(self, t):
        for i in range(0, 40):
            self.canvas[i*3] = (2*i, t, 0)

    def _clip_color_space(self):
        self.canvas = [clip_color(x) for x in self.canvas]

    def get_pxl(self, i):
        try:
            return self.canvas[i]
        except IndexError:
            return 0, 0, 0

    def sum_color(self, c1, c2):
        return tuple(
            x1 + x2 for x1, x2 in zip(c1, c2) 
        )

    def mute_color(self, c):
        while max(c) > 15:
            c = tuple(x//2 for x in c)
        return c

    def blur(self):
        canvas = self.new_canvas()
        for i, c in enumerate(self.canvas):
            if c == (0, 0, 0):
                left = self.get_pxl(i-1)
                right = self.get_pxl(i+1)
                canvas[i] = self.mute_color(self.sum_color(left, right))
            else:
                canvas[i] = c
        self.canvas = canvas

    def as_state_event(self):
        self.overlay_keys(self.pressed_keys, BLUES)
        self.hl_keys = self.pressed_keys

        self.overlay_keys(self.hl_keys, GREENS)

        black_hl = [x for x in self.hl_keys if KeyboardConfig.is_black_key(x)]
        print(self.hl_keys, black_hl)
        self.overlay_keys(black_hl, YELLOWS)

        self.blur()

        self._clip_color_space()

        return protocol.SetStateEvent(
            {
                i: self.canvas[i] for i in range(len(self.canvas)) if self.canvas[i] != (0, 0, 0)
            }
        )

def main():
    s = connect()
    while True:
        for t in range(0, 80):
            print(f"T: {t}")
            c = Compositor()
            c.color_test(t)
            s.sendall(c.as_state_event().serialize().encode())
            time.sleep(0.1)

if __name__ == '__main__':
    main()

