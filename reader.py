import time
import numpy as np
#import dv
from metavision_core.event_io import RawReader

class read_events():
    def __init__(self, path, format):
        start_time = time.time()
        self.path = path

        # Read events from file.
        self.format(format)

        print("load time: %s sec" % (time.time() - start_time))

    # generate_key generates a standard key for the hot pixel map.
    def generate_key(self, x, y):
        return str(x) + "," + str(y)

    def format(self, format):
        print("Format: " + format)

        if format == "PRO_CSV":
            self.events = np.loadtxt(self.path, delimiter=",", dtype=int)
            return

        elif format == "DVX_CSV":
            self.events = np.loadtxt(self.path, delimiter=",", dtype=int, skiprows=2)
            events_copy = np.copy(self.events)
            offset = self.events[0,0]

            # Convert unix time to microseconds.
            for i in self.events:
                i[0] = i[0]-offset

            events_copy[:,0] = self.events[:,1]
            events_copy[:,1] = self.events[:,2]
            events_copy[:,2] = self.events[:,3]
            events_copy[:,3] = self.events[:,0]
            self.events = events_copy
            self.frame_height = 480
            self.frame_width = 640

        elif format == "DVX":
            f = dv.AedatFile(self.path)
            events = np.hstack([[packet['x'], packet['y'], packet['polarity'], packet['timestamp']] for packet in f['events'].numpy()])

            self.events = np.transpose(events.astype(int))
            offset = events[3][0]

            print(self.events)

            # Convert unix time to microseconds.
            for i in self.events:
                i[3] = i[3]-offset

            self.frame_height = 480
            self.frame_width = 640
            return

        elif format == "PRO":
            record_raw = RawReader(self.path)
            self.events = np.empty((0,4), dtype=int)

            while not record_raw.is_done():
                # load the next 50 ms worth of events
                packet = record_raw.load_delta_t(50000)

                events = np.array([packet['x'], packet['y'], packet['p'], packet['t']])
                events = np.transpose(events)

                self.events = np.vstack((self.events, events))
            return

        else:
            print("Error: invalid format")
            return
