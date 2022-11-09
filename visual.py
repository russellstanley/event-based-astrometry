import matplotlib.pyplot as plt
import cv2
import sys
import numpy as np
import reader
import time
import noise

from metavision_core.event_io import RawReader

if (len(sys.argv) > 1):
    path = sys.argv[1]

ONE_SECOND = 1e6
DEFAULT_FRAME_WIDTH = 1280 # pixels
DEFAULT_FRAME_HEIGHT = 720 # pixels

class simple_accumulation(reader.read_events):
    path = ""
    frame_height = DEFAULT_FRAME_HEIGHT
    frame_width = DEFAULT_FRAME_WIDTH

    def __init__(self, path):
        self.path = path

    def scatter(self, start_us, end_us, remove_noise=True):
        record_raw = RawReader(self.path)
        record_raw.seek_time(start_us)
        data = record_raw.load_delta_t(end_us - start_us)

        self.load_noise(noise.FILE_PATH)

        x = data['x']
        y = data['y']
        t = data['t']
        p = data['p']

        mask = np.ones(len(x), dtype=bool)
        if (remove_noise == True):
            for i in range(len(data)):
                x_i = x[i]
                y_i = y[i]

                if (self.hot_pixels.get(self.generate_key(x_i,y_i)) != None):
                    mask[i] = False

        fig = plt.figure(figsize=(10,10))
        ax = plt.axes(projection='3d')
        ax.set_ylim((0,1280))
        ax.set_zlim((0,720))
        ax.set_xlabel("time(sec)", fontsize=14)
        ax.set_ylabel("x", fontsize=14)
        ax.set_zlabel("y",fontsize=14)

        scatter = ax.scatter((t[mask]/ONE_SECOND),x[mask],y[mask], c=p[mask], cmap='rainbow', linewidth=0.5)

        legend = ax.legend(*scatter.legend_elements())
        ax.add_artist(legend)

        ax.view_init(elev=30, azim=45)
        plt.savefig('scatter3d.jpg', dpi=250)
        

    def generate_image(self, duration_us, name, hot_pixels_path=""):
        record_raw = RawReader(self.path)

        # Generate noise map if a path is given
        if hot_pixels_path != "":
            self.load_noise(hot_pixels_path)

        image = np.zeros((self.frame_height, self.frame_width))

        start_time = time.time()
        # Read each 'ON' event and determine the sky coordinates.
        while not record_raw.is_done() and record_raw.current_time < duration_us:
            # load the next 10 ms worth of events
            packet = record_raw.load_delta_t(10000)
            for (x, y, p, t) in packet:
                if (p==1 and self.hot_pixels.get(self.generate_key(x,y)) == None):
                    image[y, x] = image[y, x] + 1 #TODO Determine best value to increase by

        print("image_generation: %s sec" % (time.time() - start_time))

        cv2.imwrite(name, self.normalize(image))
        return self.normalize(image)


art = simple_accumulation(path)
art.scatter(0.1*ONE_SECOND, 30*ONE_SECOND, True)