import umqtt_robust2
import GPSfunk
from machine import Pin
import LED_ring
import distance

# ATGM336H-5N <--> ESP32 
# GPS til ESP32 kredsløb
# GPS VCC --> ESP32 3v3
# GPS GND --> ESP32 GND
# GPS TX  --> ESP32 GPIO 16

LED_ring.set_color(250, 0, 0)

from time import sleep_ms, sleep
lib = umqtt_robust2
# opret en ny feed kaldet map_gps indo på io.adafruit
mapFeed = bytes('{:s}/feeds/{:s}'.format(b'oliverthers', b'mapfeed/csv'), 'utf-8')
# opret en ny feed kaldet speed_gps indo på io.adafruit
speedFeed = bytes('{:s}/feeds/{:s}'.format(b'oliverthers', b'speedfeed/csv'), 'utf-8')

count = 0
latLonList = []
while True:
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

        
        sleep(10) 
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
    lib.c.check_msg() # needed when publish(qos=1), ping(), subscribe()
    lib.c.send_queue()  # needed when using the caching capabilities for unsent messages

lib.c.disconnect()