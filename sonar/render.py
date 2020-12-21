from test import synth
from data import data
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

W = []
a = 0
b = 0
c = 0

for (f, _, frames) in data:
  w, a = synth(f, a, frames)
  h2, b = synth(f*2, b, frames)
  h3, c = synth(f*3, c, frames)
  W.append(2*w)

w = (np.concatenate(W, axis=None) * 30000).astype(np.int16)
write("foo.wav", 44100, w)
#sd.play(w, 44100, blocking=True)
