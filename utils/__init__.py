import math
from . import julian


def az_to_octant(azimuth):
    octants = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    idx = azimuth / (2*math.pi/8)
    return octants[int(round(idx)) % 8]
