import json

from keyboard_config import KeyboardConfig
from led_config import LEDConfig

from rtmidi.midiutil import open_midiinput
import mido
import time
import os
import sys
from compositor import Compositor
from client import connect
import compositor
from mapper import FN, KeyMapper


class Recorder:
    def __init__(self):
        pass

    def run(self):
        midi_input, _port_name = open_midiinput(port="aurora")
        midi_input.set_callback(self.callback)
        self.led_index = 0
        self.key = 0
        self.km = KeyMapper()
        self.m = dict(self.km.km)
        self.compositor = Compositor()
        self.s = connect()
        while True:
            time.sleep(0.05)
            frame = self.compositor.new_frame()
            wire_event = frame.as_state_event()
            payload = wire_event.serialize().encode()
            self.s.sendall(payload)
    
    def save_mapping(self):
        with open(FN, 'w') as f:
            f.write(json.dumps(self.m, indent=4))

    def callback(self, event, _):
        event, _ = event
        event = mido.parse(event)
        print(event)
        frame = self.compositor.new_frame()
        if event.type == 'control_change' and event.value == 0:
            if event.control == 102:
                self.led_index += 1
            if event.control == 103:
                self.led_index -= 1
            if event.control == 51:
                self.save_mapping()
            self.m[self.key] = self.led_index
            frame.effect_manager.spawn_led_selection_effects(self.led_index, palette=compositor.YELLOWS)
        
        if event.type != 'note_on':
            return
        self.key = event.note
        self.led_index = self.m[self.key]        
        frame.effect_manager.spawn_led_selection_effects(self.m[self.key], palette=compositor.GREENS)

        wire_event = frame.as_state_event()
        payload = wire_event.serialize().encode()
        print("payload", payload)
        self.s.sendall(payload)


if __name__ == '__main__':
    Recorder().run()
