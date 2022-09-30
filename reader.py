import time

# TODO: Add an interface to create a univerisal iterator which 
# can handle both event file types

class read_events():
    def __init__(self, path):
        start_time = time.time()
        self.path = path

        print("load time: %s sec" % (time.time() - start_time))

    # generate_key generates a standard key for the hot pixel map.
    def generate_key(self, x, y):
        return str(x) + "," + str(y)