import sys
import time
from RPi import GPIO


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


def main():
  setup()
  time.sleep(2)
  try:
    while True:
      d = ping()
      draw_ui(d)
      time.sleep(60.0 / 1000)
  except:
    GPIO.cleanup()
    raise


if __name__ == "__main__":
  main()
