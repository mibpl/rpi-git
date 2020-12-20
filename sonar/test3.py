import numpy as np
import sounddevice as sd

sample_rate = 44100
duration = 500.0 / 1000
volume = 0.3



def play(f):
   sample_index = np.arange(duration * sample_rate)
   return volume * np.sin(2 * np.pi * sample_index * f / sample_rate)

import time
import random


iii = 0
fff = 260


def callback(outdata, frames, time, status):
  global iii
  start = iii
  
  sample_index = np.arange(frames, dtype=np.int32)
  reindexed = (2.0 / sample_rate * np.pi * sample_index * fff) + iii
  wave = volume * np.sin(reindexed)
  iii = reindexed[-1]

  outdata[:, 0] = wave

stream = sd.OutputStream(samplerate=sample_rate, callback=callback, channels=1, dtype=np.float32)

stream.start()

for f in (400, 260, 300, 400, 260, 300, 240, 420, 260, 500):
  fff = f
  time.sleep(0.06)

