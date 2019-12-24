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
        self.compositor = Compositor()
    
    def on_parsed_event(self, event):
        channel = None
        if hasattr(event, 'channel'):
            channel = event.channel

        if channel == KeyboardConfig.light_channel:
            self.light_tracker.midi_event(event)
        else:
            self.player_tracker.midi_event(event)
        
        frame = self.compositor.new_frame()
        frame.add_pressed_keys(self.player_tracker.get())
        frame.add_hl_keys(self.light_tracker.get())

        if channel != KeyboardConfig.light_channel:
            if event.type == 'note_on':
                frame.on_press(event.note)
            if event.type == 'note_off':
                frame.on_release(event.note)

        wire_event = frame.as_state_event()
        payload = wire_event.serialize().encode()
        print("payload", payload)
        self.s.sendall(payload)

    def on_midi_event(self, event, data):
        event, dt = event
        event = mido.parse(event)
        print(event, data)
        self.on_parsed_event(event)

def main():
    s = connect()

    print(f"Connected. Starting handlers.")

    eh = EventHandler(s)
    midi_input, _port_name = open_midiinput(port="aurora")
    midi_input.set_callback(eh.on_midi_event)
    print(midi_input)

    try:
        while True:
            time.sleep(0.05)
            eh.on_parsed_event(mido.Message("clock"))
    except KeyboardInterrupt:
        pass
    finally:
        midi_input.close_port()
        del midi_input


if __name__ == '__main__':
    main()