from led_config import LEDConfig
from keyboard_config import KeyboardConfig
import protocol
from client import connect
import time
import typing
import itertools
from collections import deque
import enum
import mapper


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

PURPLE = (25, 0, 65)

DARK = (0, 0, 0)


class ShadePalette(typing.NamedTuple):
    normal: ColorT
    light: ColorT


BLUES = ShadePalette(normal=BLUE, light=LIGHT_BLUE)
GREENS = ShadePalette(normal=GREEN, light=LIGHT_GREEN)
YELLOWS = ShadePalette(normal=YELLOW, light=YELLOW_LIGHT)
PURPLES = ShadePalette(normal=PURPLE, light=PURPLE)


class CBuffer:
    def __init__(self, n=10):
        self.buf = deque()
        self.n = n

    def get(self):
        return iter(self.buf)
    
    def add(self, e):
        if len(self.buf) >= self.n:
            self.buf.popleft()
        self.buf.append(e)


def new_canvas() -> typing.List[ColorT]:
    return LEDConfig.total_lights * [DARK]


class EffectManager:
    def __init__(self, key_mapper: mapper.KeyMapper):
        self.effects = list()
        self.key_mapper = key_mapper
    
    def update(self, dt):
        for e in list(self.effects):
            e.update(dt)
            if e.is_ended():
                self.effects.remove(e)
        # if len(self.effects) > 0:
        #     print(f"{len(self.effects)} effects managed")

    def spawn_key_release_effects(self, key, palette=None):
        if palette is None:
            palette = PURPLES if KeyboardConfig.is_black_key(key) else BLUES
        self.effects.append(
            PixelFadeOut(
                self.key_mapper.key_to_pixel(key),
                palette
            )
        )

    def spawn_led_selection_effects(self, pixel, palette=None):
        if palette is None:
            palette = PURPLES if KeyboardConfig.is_black_key(key) else BLUES
        self.effects.append(
            PixelFadeOut(
                pixel,
                palette
            )
        )

class Effect:
    def is_ended(self):
        return False

    def update(self, dt):
        pass


class BlendType(enum.Enum):
    OVERLAY = 1


class PixelFadeOut(Effect):
    def __init__(self, pixel: int, palette: ShadePalette, speed=0.05):
        self.pixel = pixel
        self.color = palette.normal
        self.speed = speed
    
    def update(self, dt):
        r, g, b = self.color
        self.color = (
            r * self.speed ** dt,
            g * self.speed ** dt,
            b * self.speed ** dt
        )

    def get_canvas(self):
        canvas = new_canvas()
        canvas[self.pixel] = self.color
        return canvas
    
    def is_ended(self):
        if max(self.color) <= 2:
            return True
        return False


class Compositor:
    def __init__(self):
        self.frame_history = CBuffer()
        self.effect_manager = EffectManager(mapper.KeyMapper())
        self.last_time = None

    def new_frame(self):
        f = Frame(self)
        self.frame_history.add(f)
        return Frame(self)

    def update(self):
        t = time.time()
        if self.last_time is None:
            self.last_time = t
        dt = t - self.last_time
        self.last_time = t
        self.effect_manager.update(dt)


def overlay_canvas(back, fore):
    return [b if f == DARK else f for b, f in zip(back, fore)]


def halve(c):
    return tuple(x//2 for x in c)


class Frame:
    def new_canvas(self) -> typing.List[ColorT]:
        return new_canvas()

    def __init__(self, compositor) -> None:
        self.canvas = self.new_canvas()
        self.pressed_keys = []
        self.hl_keys = []
        self.compositor = compositor
        self.effect_manager = compositor.effect_manager

    def overlay_effects(self):
        canvas = new_canvas()
        for e in self.effect_manager.effects:
            canvas = overlay_canvas(canvas, e.get_canvas())
        self.canvas = overlay_canvas(self.canvas, canvas)

    def on_press(self, note):
        pass

    def on_release(self, note, palette=None):
        self.effect_manager.spawn_key_release_effects(note, palette=palette)

    def add_pressed_keys(self, keys):
        self.pressed_keys = list(keys)

    def add_hl_keys(self, keys):
        self.hl_keys = list(keys)

    def overlay_keys(self, keys, shades: ShadePalette):
        for key in keys:
            n = self.effect_manager.key_mapper.key_to_pixel(key)
            self.canvas[n] = shades.normal

    def color_test(self, t):
        for i in range(0, 40):
            self.canvas[i*3] = (2*i, 0, t)

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
        c = halve(c)
        while max(c) > 10:
            c = halve(c)
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
        self.compositor.update()
        self.overlay_effects()
        self.overlay_keys(self.pressed_keys, BLUES)
        black_press = [x for x in self.pressed_keys if KeyboardConfig.is_black_key(x)]
        self.overlay_keys(black_press, PURPLES)

        self.overlay_keys(self.hl_keys, GREENS)
        black_hl = [x for x in self.hl_keys if KeyboardConfig.is_black_key(x)]
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
            c = Compositor().new_frame()
            c.color_test(t)
            s.sendall(c.as_state_event().serialize().encode())
            time.sleep(0.1)


if __name__ == '__main__':
    main()

