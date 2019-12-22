#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from collections import defaultdict
import socket
import sys
import asyncio
from rtmidi.midiutil import open_midiinput
from rtmidi.midiutil import list_input_ports
import mido
import collections
from led_config import LEDConfig
import protocol
import itertools
from keyboard_config import KeyboardConfig
from compositor import Compositor
from client import connect

class Tracker:
    def __init__(self):
        self.wipe()
    
    def midi_event(self, event):
        if event.type == 'note_on':
            self.down(event.note)
        elif event.type == 'note_off':
            self.up(event.note)

    def down(self, k):
        self.m[k] = True
    
    def up(self, k):
        self.m[k] = False

    def wipe(self):
        self.m = collections.defaultdict(bool)

    def get(self):
        return (k for k, v in self.m.items() if v)

class EventHandler:
    def __init__(self, s):
        self.s = s
        self.light_tracker = Tracker()
        self.player_tracker = Tracker()
    
    def on_midi_event(self, event, data):
        event, dt = event
        event = mido.parse(event)
        print(event, data)
        if event.channel == KeyboardConfig.light_channel:
            self.light_tracker.midi_event(event)
        else:
            self.player_tracker.midi_event(event)
        
        compositor = Compositor()
        compositor.add_pressed_keys(self.player_tracker.get())
        compositor.add_hl_keys(self.light_tracker.get())
        wire_event = compositor.as_state_event()
        payload = wire_event.serialize().encode()
        print("payload", payload)
        self.s.sendall(payload)

def main():
    s = connect()

    print(f"Connected. Starting handlers.")

    eh = EventHandler(s)
    midi_input, port_name = open_midiinput(port="aurora")
    midi_input.set_callback(eh.on_midi_event)
    print(midi_input)

    try:
        while True:
            time.sleep(4)
    except KeyboardInterrupt:
        pass
    finally:
        midi_input.close_port()
        del midi_input


if __name__ == '__main__':
    main()