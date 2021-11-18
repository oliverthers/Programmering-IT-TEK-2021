import umqtt_robust2 as lib
import GPSfunk
import LED_ring
import distance
from machine import Pin
from time import sleep_ms, sleep, ticks_ms
import mp3
import DHT11
# ATGM336H-5N <--> ESP32 
# GPS til ESP32 kredsløb
# GPS VCC --> ESP32 3v3
# GPS GND --> ESP32 GND
# GPS TX  --> ESP32 GPIO 16

# button objekt
button = Pin(17, Pin.IN)
# vibrator objekt
vibrator = Pin(4, Pin.OUT)


# opret feeds til io.adafruit
mapFeed = bytes('{:s}/feeds/{:s}'.format(b'oliverthers', b'mapfeed/csv'), 'utf-8')
speedFeed = bytes('{:s}/feeds/{:s}'.format(b'oliverthers', b'speedfeed/csv'), 'utf-8')
distanceFeed = bytes('{:s}/feeds/{:s}'.format(b'oliverthers', b'distancefeed/csv'), 'utf-8')
timeFeed = bytes('{:s}/feeds/{:s}'.format(b'oliverthers', b'timefeed/csv'), 'utf-8')
tempfeed = bytes('{:s}/feeds/{:s}'.format(b'oliverthers', b'tempfeed/csv'), 'utf-8')

#Variabler til at kunne køre non blocking delays
previousTimeLed = 0
previousTimeVib = 0
intervalLed = 10000
intervalVib = 1000

#variabler
vibratorIsOn = False
ledColorRed = False
isOn = False
dist = 0
mp3count = 0


#løkke der tjekker om knap bliver trykket
while True:
    buttonPressed = button.value()
    if not buttonPressed: #Knap er konstant 1, derfor if not
        print("buttonPressed")
        isOn = True
        ledColorRed = True
        LED_ring.set_color(255, 0, 0)
        
    if lib.besked == "1":
        print(lib.besked)
        if mp3count < 1:
            mp3.mp3()
            mp3count = mp3count+1
        
    
        
    count = 0
    latLonList = []
    #Når knap er trykket sættes isOn til True og vi komme ind i isOn løkken
    while isOn:
        mp3.stop()
        currentTime = ticks_ms()
        
        #non blocking delay
        if (currentTime - previousTimeLed > intervalLed):
            previousTimeLed = currentTime
            #Hvis LED er rød, sættes den til grøn og kører 10 sek.
            if ledColorRed:
                LED_ring.set_color(0,250,0)
                ledColorRed = False
                vibrator.on()
                vibtratorIsOn = True
                #publisher til adafruit
                lib.c.publish(topic=distanceFeed, msg=str(dist))
                lib.c.publish(topic=tempfeed, msg=str(DHT11.dht11()))
                #lib.c.publish(topic=timeFeed, msg=str(dist))
            else:
                LED_ring.set_color(255,0,0)
                ledColorRed = True
                vibrator.on()
                vibtratorIsOn = True
                lib.c.publish(topic=distanceFeed, msg=str(dist))
                lib.c.publish(topic=tempfeed, msg=str(DHT11.dht11()))
                #lib.c.publish(topic=timeFeed, msg=str(dist))

            gpsReturn = GPSfunk.main()
            if lib.c.is_conn_issue():
                while lib.c.is_conn_issue():
                    # hvis der forbindes returnere is_conn_issue metoden ingen fejlmeddelse
                    lib.c.reconnect()
                else:
                    lib.c.resubscribe()
            try:
                lib.c.publish(topic=mapFeed, msg=gpsReturn[0])
                speed = gpsReturn[0]
                speed = speed[:4]
                print("speed: ", speed)
                print("lat: ",gpsReturn[1])
                print("lon:", gpsReturn[2])
        
                latLonList.append(float(gpsReturn[1]))
                latLonList.append(float(gpsReturn[2]))
                print("list", latLonList)
                count +=1
                lib.c.publish(topic=speedFeed, msg=speed)
                if count > 1:
                    dist = distance.calculateDistance(latLonList[0], latLonList[1],latLonList[-2],latLonList[-1])
                    print(dist)
            
            except KeyboardInterrupt:
                print('Ctrl-C pressed...exiting')
                lib.c.disconnect()
                lib.wifi.active(False)
                lib.sys.exit()
            except OSError as e:
                print('Failed to read sensor.')
            #except NameError as e:
                #print('NameError')
            except TypeError as e:
                print('TypeError')
            
        
        if (currentTime - previousTimeVib > intervalVib):
            previousTimeVib = currentTime
            if vibratorIsOn and previousTimeVib - previousTimeLed > 1000:
                #Pin(4, Pin.OUT, value = 0)
                vibrator.off()
                vibtratorIsOn = False
        
        buttonPressed = button.value()
        if not buttonPressed:
            isOn = False
            LED_ring.set_color(0,0,0)
            break



        
    lib.c.check_msg() # needed when publish(qos=1), ping(), subscribe()
    lib.c.send_queue()  # needed when using the caching capabilities for unsent messages
lib.c.disconnect()
