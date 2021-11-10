from machine import Pin
import neopixel
import time


n = 12
p = 15

np = neopixel.NeoPixel(Pin(p), n)

def set_color(r, g, b):
    for i in range(n):
        np[i] = (r, g , b)
    np.write()

def clear():
    for i in range(n):
        np[i] = (0, 0, 0)
        np.write()


    