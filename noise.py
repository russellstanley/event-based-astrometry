import reader

FILE_PATH = "hot_pixels.csv"

class find_hot_pixels(reader.read_events):
    # write_hot_pixels will generate a file of hot pixels. The number hot pixels written is dependant on the percentage threshold.
    def write_hot_pixels(self, threshold):
        dict = {}

        # Read each event and count the events at each pixel
        for (x, y, p, t) in self.events:
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
