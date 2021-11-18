from machine import Pin
from time import sleep
import dht

sensor = dht.DHT11(Pin(4))

def dht11():
    sensor.measure()
    temp = sensor.temperature()
    return temp


