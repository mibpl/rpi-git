import time
import board
import neopixel
pixels = neopixel.NeoPixel(board.D18, 30)
pixels.fill((0, 255, 0))

time.sleep(3600)
