import sys
import os
import time
from RPi import GPIO
import sounddevice as sd
import numpy as np


TRIG_PORT = 23
ECHO_PORT = 24
TRIG_LENGTH = 0.00001
SCALE = 17000


def setup():
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(TRIG_PORT, GPIO.OUT)
  GPIO.setup(ECHO_PORT, GPIO.IN)
  GPIO.output(TRIG_PORT, False)


def trigger():
  GPIO.output(TRIG_PORT, True)
  time.sleep(TRIG_LENGTH)
  GPIO.output(TRIG_PORT, False)


def wait_for(state: bool, timeout=10) -> float:
  wait_start = time.time()
  now = wait_start
  while GPIO.input(ECHO_PORT) != state:
    now = time.time()
    if now - wait_start > timeout:
      raise Exception(f"Timeout waiting for signal {state} after {timeout}s")
  return now


def ping() -> float:
  trigger()
  start = wait_for(1)
  end = wait_for(0)
  return (end - start) * SCALE


sample_rate = 44100
volume = 0.3


cb_state_freq = 260
cb_state_i = 0
cb_state_log = []


def synth(f, i, frames):
  sample_index = np.arange(frames, dtype=np.int32)
  reindexed = (2.0 / sample_rate * np.pi * sample_index * f) + i
  
  return volume * np.sin(reindexed), reindexed[-1]


def callback(outdata, frames, time, status):
  global cb_state_i
  cb_state_log.append((cb_state_freq, cb_state_i, frames))

  outdata[:, 0], cb_state_i = synth(cb_state_freq, cb_state_i, frames)


def draw_ui(d: float):
  if d > 60:
    return
  
  p = '{:6.2f}  {:3.0f}  '.format(d, cb_state_freq)
  s = "#" * int(d)
  
  print("\r{:100}".format(p + s), end='')
  sys.stdout.flush()


def main():
  setup()
  time.sleep(1)
  stream = sd.OutputStream(
    samplerate=sample_rate,
    callback=callback,
    channels=1,
    dtype=np.float32
  )
  stream.start()

  try:
    while True:
      d = ping()
      
      if 5 < d < 45:
        f = int(
          ((d - 5) / 40.0) * (700 - 400) + 400
        )

        global cb_state_freq
        cb_state_freq = f

      draw_ui(d)
      time.sleep(60.0 / 1000)
  except:
    GPIO.cleanup()
    with open("/tmp/sonar.log", 'w') as f:
      f.write(repr(cb_state_log))
    raise


if __name__ == "__main__":
  main()
