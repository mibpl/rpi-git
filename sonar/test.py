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


def draw_ui(d: float):
  if d > 80:
    return
  p = '{:6.2f}  '.format(d)
  s = "#" * int(d)
  print("\r{:90}".format(p + s), end='')
  sys.stdout.flush()




sample_rate = 44100
volume = 0.3


def play(f):
	duration = 500.0 / 1000

	sample_index = np.arange(duration * sample_rate)
	wave = volume * np.sin(2 * np.pi * sample_index * f / sample_rate)

	# sd.stop()
	sd.play(wave, sample_rate, blocking=False)


fff = 260


def callback(outdata, frames, time, status):
  t = time.currentTime
  start = t * sample_rate
  global fff
  sample_index = np.arange(start, start + frames, dtype=np.int32)
  wave = volume * np.sin(2.0 / sample_rate * np.pi * sample_index * fff)
  outdata[:, 0] = wave


def main():
  setup()
  time.sleep(1)
  stream = sd.OutputStream(samplerate=sample_rate, callback=callback, channels=1, dtype=np.float32, latency='low')
  stream.start()

  try:
    while True:
      d = ping()
      draw_ui(d)
      f = int(
        (min((d - 5), 40) / 40.0) * (523 - 261) + 261
      )
      global fff
      fff = f
      #play(f)
      time.sleep(60.0 / 1000)
  except:
    GPIO.cleanup()
    raise


if __name__ == "__main__":
  main()
