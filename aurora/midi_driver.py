#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from collections import defaultdict
import socket
import sys
import asyncio
from rtmidi.midiconstants import (CONTROL_CHANGE, DATA_DECREMENT,
                                  DATA_ENTRY_LSB, DATA_ENTRY_MSB,
                                  DATA_INCREMENT, RPN_LSB, RPN_MSB)
from rtmidi.midiutil import open_midiinput
from rtmidi.midiutil import list_input_ports
import mido
import collections
from led_config import LEDConfig
import protocol
import itertools

class KeyboardConfig:
    low_note = 36
    high_note = 96
    light_channel = 9


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

def note_to_leds(note):
    ratio = (note - KeyboardConfig.low_note) / (KeyboardConfig.high_note - KeyboardConfig.low_note + 1)
    n = round(ratio * (LEDConfig.high_light - LEDConfig.low_light + 1) + LEDConfig.low_light)
    return (int(n),)

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
        
        wire_event = protocol.SetStateEvent(
            {
                led: (0, 0, 255) for led in itertools.chain(
                    *[note_to_leds(note) for note in self.player_tracker.get()]
                )
            }
        )
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