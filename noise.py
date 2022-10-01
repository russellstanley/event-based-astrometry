import reader
from metavision_core.event_io import RawReader

FILE_PATH = "hot_pixels.csv"

class find_hot_pixels(reader.read_events):
    # write_hot_pixels will generate a file of hot pixels. The number hot pixels written is dependant on the percentage threshold.
    def write_hot_pixels(self, threshold):
        dict = {}
        record_raw = RawReader(self.path)

        while not record_raw.is_done():
            # load the next 10 ms worth of events
            packet = record_raw.load_delta_t(10000)

            # Read each event and count the events at each pixel
            for (x, y, p, t) in packet:
                key = self.generate_key(x,y)

                if dict.get(key) == None:
                    dict.update({key:1})
                else:
                    value = dict.get(key) + 1
                    dict.update({key:value})

        file = open(FILE_PATH, "w")
        count = 0
        limit = int(len(dict) * (threshold/100))
        print("Writing: %s/%s(%s%%) of hot pixels identified" % (limit, len(dict), threshold))

        for i in sorted(dict, key=dict.get, reverse=True):
            file.write("%s,%s\n" % (i, dict[i]))
            count = count + 1

            if count > limit:
                break
