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


def callback(outdata, frames, time, status):
  t = time.currentTime
  start = t * sample_rate
  f = 400
  sample_index = np.arange(start, start + frames, dtype=np.int32)
  wave = volume * np.sin(2.0 / sample_rate * np.pi * sample_index * f)

  outdata[:, 0] = wave

stream = sd.OutputStream(samplerate=sample_rate, callback=callback, channels=1, dtype=np.float32)

stream.start()
time.sleep(5)
