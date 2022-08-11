import numpy as np
import sys

if (len(sys.argv) > 1):
    path = sys.argv[1]
else:
    exit()

if len(sys.argv) > 2:
    format = sys.argv[2]
else:
    format = ""

class find_hot_pixels:
    frame_height = 1280
    frame_width = 720

    def __init__(self, path):
        self.path = path

        # Read events from file. Skip the first 2 entries as for some files these will be headers.
        self.events = np.genfromtxt(path, delimiter=",", dtype=int, skip_header=2)
        self.format()

    def format(self):
        if format == "DVX":
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

        elif format != "":
            print("Error: invalid format")
            return

    # get_hot_pixels will generate a file of hot pixels. The number hot pixels written is dependant on the percentage threshold.
    def get_hot_pixels(self, threshold):
        dict = {}

        # Read each event and count the events at each pixel
        for (x, y, p, t) in self.events:
            key = str(x) + "," + str(y)

            if dict.get(key) == None:
                dict.update({key:1})
            else:
                value = dict.get(key) + 1
                dict.update({key:value})

        file = open("hot_pixels.csv", "w")
        pixels = self.frame_height*self.frame_width
        count = 0
        limit = pixels * (threshold/100)
        print(limit)

        for i in sorted(dict, key=dict.get, reverse=True):
            file.write("%s,%s\n" % (i, dict[i]))
            count = count + 1

            if count > limit:
                break


player = find_hot_pixels(path)
player.get_hot_pixels(50)