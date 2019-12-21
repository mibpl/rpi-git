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

def connect():
    for host in [
        '192.168.1.184',
        '127.0.0.1'
    ]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, 6666))
            return s
        except Exception as e:
            print(f"Connection to {host} failed: {e}")
    raise Exception("No server found")

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

class Compositor:
    BLUE = (0, 0, 255)
    LIGHT_BLUE = (0, 0, 10)

    GREEN = (0, 255, 0)
    LIGHT_GREEN = (0, 10, 0)

    YELLOW = (0, 10, 10)

    def __init__(self):
        self.canvas = LEDConfig.total_lights * [(0, 0, 0)]
        self.pressed_keys = []
        self.hl_keys = []

    def add_pressed_keys(self, keys):
        self.pressed_keys = keys

    def add_hl_keys(self, keys):
        self.hl_keys = keys

    def overlay_blurred(self, keys, normal_color, light_color):
        for key in keys:
            n = key_to_closest_pixel(key)
            color = None
            if KeyboardConfig.is_black_key(key):
                color = Compositor.YELLOW
            self.canvas[n] = color or normal_color

            try:
                self.canvas[n + 1] = color or light_color
                self.canvas[n - 1] = color or light_color
            except IndexError:
                pass

    def as_state_event(self):
        self.overlay_blurred(self.pressed_keys, normal_color=Compositor.BLUE, light_color=Compositor.LIGHT_BLUE)
        self.overlay_blurred(self.hl_keys, normal_color=Compositor.GREEN, light_color=Compositor.LIGHT_GREEN)

        return protocol.SetStateEvent(
            {
                i: self.canvas[i] for i in range(len(self.canvas))
            }
        )

def key_to_normalized_position(note):
    return (note - KeyboardConfig.low_note) / (KeyboardConfig.high_note - KeyboardConfig.low_note + 1)

def key_to_closest_pixel(note):
    ratio = key_to_normalized_position(note)
    n = round(ratio * (LEDConfig.high_light - LEDConfig.low_light + 1) + LEDConfig.low_light)
    return int(n)

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