import sys
import time
import board
import neopixel

n = int(sys.argv[1])
pixels = neopixel.NeoPixel(board.D18, n)
pixels.fill((0, 0, 0))
pixels[n-1] = 0, 0, 255
