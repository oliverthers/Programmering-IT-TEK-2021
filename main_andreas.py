import umqtt_robust2
import GPSfunk
from machine import Pin
import LED_ring
import distance
import time
from time import sleep_ms, sleep
from time import ticks_ms
# ATGM336H-5N <--> ESP32 
# GPS til ESP32 kredsløb
# GPS VCC --> ESP32 3v3
# GPS GND --> ESP32 GND
# GPS TX  --> ESP32 GPIO 16

# button objekt
button = Pin(34, Pin.IN, Pin.PULL_UP)


lib = umqtt_robust2
# opret en ny feed kaldet map_gps indo på io.adafruit
mapFeed = bytes('{:s}/feeds/{:s}'.format(b'oliverthers', b'mapfeed/csv'), 'utf-8')
# opret en ny feed kaldet speed_gps indo på io.adafruit
speedFeed = bytes('{:s}/feeds/{:s}'.format(b'oliverthers', b'speedfeed/csv'), 'utf-8')
distanceFeed = bytes('{:s}/feeds/{:s}'.format(b'oliverthers', b'distancefeed/csv'), 'utf-8')

ison = False
isoff = True
interval01 = 10000
previousTimeBuzz01 = 0
interval02 = 1000
previousTimeBuzz02 = 0
interval03 = 10000
previousTimeGPS01 = 0
previousTimeGPS02 = 0
previousTimeLed = 0

dist = 0

while True:
    buttonPressed = button.value()
    if not buttonPressed and not ison:
        ison = True
        if ison:
            print('Button pressed!')
            print(buttonPressed)
    sleep(0.2)
    
    count = 0
    latLonList = []
    vibratorIsOn = False
    

    while ison:
        currentTime = ticks_ms()
        
        LED_ring.set_color(255,0,0)
        ledColorRed = True
        
       
        Pin(33, Pin.OUT, value=1)
        vibtratorIsOn = True
        #sleep(1)
        Pin(33, Pin.OUT, value=0)
        vibratorIsOn = False
        

        
        gpsReturn = GPSfunk.main()
        if lib.c.is_conn_issue():
            while lib.c.is_conn_issue():
                # hvis der forbindes returnere is_conn_issue metoden ingen fejlmeddelse
                lib.c.reconnect()
            else:
                lib.c.resubscribe()
        try:
            if (currentTime - previousTimeGPS01 > interval01):
                previousTimeGPS01 = currentTime
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
                

        
        # Stopper programmet når der trykkes Ctrl + c
        except KeyboardInterrupt:
            print('Ctrl-C pressed...exiting')
            lib.c.disconnect()
            lib.wifi.active(False)
            lib.sys.exit()
        except OSError as e:
            print('Failed to read sensor.')
        except NameError as e:
            print('NameError')
        #except TypeError as e:
            #print('TypeError')
            
        #sleep(1)
        
        if (currentTime - previousTimeLed > interval03):
            previousTimeLed = currentTime
            if ledColorRed:
                LED_ring.set_color(0,250,0)
                ledColorRed = False
            #lib.c.publish(topic=distanceFeed, msg=str(dist))
            else:
                LED_ring.set_color(255,0,0)
            #lib.c.publish(topic=distanceFeed, msg=str(dist))
            
            
        Pin(33, Pin.OUT, value=1)
        vibtratorIsOn = True
        if (currentTime - previousTimeBuzz02 > interval02):
            previousTimeBuzz02 = currentTime
            Pin(33, Pin.OUT, value=0)
            vibratorIsOn = False
        
        gpsReturn = GPSfunk.main()
        if lib.c.is_conn_issue():
            while lib.c.is_conn_issue():
                # hvis der forbindes returnere is_conn_issue metoden ingen fejlmeddelse
                lib.c.reconnect()
            else:
                lib.c.resubscribe()
        try:
            if (currentTime - previousTimeGPS02 > interval03):
                previousTimeGPS02 = currentTime
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
             
             
        # Stopper programmet når der trykkes Ctrl + c
        except KeyboardInterrupt:
            print('Ctrl-C pressed...exiting')
            lib.c.disconnect()
            lib.wifi.active(False)
            lib.sys.exit()
        except OSError as e:
            print('Failed to read sensor.')
        except NameError as e:
            print('NameError')
        #except TypeError as e:
            #print('TypeError')
        
        #sleep(1)
        
        buttonPressed = button.value()  
        if not buttonPressed and ison:
            ison = False
            LED_ring.set_color(0,0,0)
            print("STOP")
            print(buttonPressed)
        sleep(0.2)
         

lib.c.check_msg() # needed when publish(qos=1), ping(), subscribe()
lib.c.send_queue()  # needed when using the caching capabilities for unsent messages

lib.c.disconnect()