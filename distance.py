import math

def calculateDistance(lat1, lon1, lat2, lon2):
    dist = math.sqrt((lat1 - lon2)**2 + (lat2 - lon2)**2)
    return dist
#print calculateDistance(x1, y1, x2, y2)
