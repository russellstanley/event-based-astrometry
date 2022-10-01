import time
import numpy as np

# TODO: Add an interface to create a univerisal iterator which 
# can handle both event file types

class read_events():
    hot_pixels = {}

    def __init__(self, path):
        start_time = time.time()
        self.path = path

        print("load time: %s sec" % (time.time() - start_time))

    hot_pixels = {}

    # load_noise will generate a map of hot pixel coordinates and their respective scale. 
    def load_noise(self, path):
        pixels = np.loadtxt(path, delimiter=",", dtype=int)
        self.hot_pixels = {}

        for (x, y, scale) in pixels:
            key = self.generate_key(x,y)
            self.hot_pixels.update({key:scale})

    # generate_key generates a standard key for the hot pixel map.
    def generate_key(self, x, y):
        return str(x) + "," + str(y)