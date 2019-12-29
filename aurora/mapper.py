import json

from keyboard_config import KeyboardConfig
from led_config import LEDConfig

from rtmidi.midiutil import open_midiinput
import mido
import time
import os
import sys
from client import connect


FN = "keymap.txt"


def _key_to_normalized_position(
    note,
    low_x = KeyboardConfig.low_note,
    high_x = KeyboardConfig.high_note,
):
    return (note - low_x) / (high_x - low_x + 1)


def _key_to_closest_pixel(
    note,
    low_x = KeyboardConfig.low_note,
    high_x = KeyboardConfig.high_note,
    low_y = LEDConfig.low_light,
    high_y = LEDConfig.high_light,
):
    ratio = _key_to_normalized_position(note, low_x=low_x, high_x=high_x)
    n = round(ratio * (high_y - low_y + 1) + low_y)
    return int(n)


class KeyMapper:
    def __init__(self, fn=FN):
        self.km = {}
        m = {}
        with open(FN) as f:
            m = json.load(f)
        m = {int(x): int(y) for x, y in m.items()}
        for key in range(KeyboardConfig.low_note, KeyboardConfig.high_note + 1):
            lb = max(filter(lambda x: x<=key, m.keys()))
            ub = min(filter(lambda x: x>=key, m.keys()))
            v = m[lb]
            if lb != ub:
                v = _key_to_closest_pixel(
                    key,
                    low_x = lb,
                    high_x = ub,
                    low_y = m[lb],
                    high_y = m[ub],
                )
            self.km[key] = v

    def key_to_pixel(self, key):
        return self.km[key]


def gen_mapping(fn):
    m = {}
    with open(fn, 'w') as f:
        for key in range(KeyboardConfig.low_note, KeyboardConfig.high_note + 1):
            m[key] = _key_to_closest_pixel(key)
        f.write(json.dumps(m, indent=4))
