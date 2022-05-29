from metavision_core.event_io import EventsIterator
from metavision_sdk_core import PeriodicFrameGenerationAlgorithm

import cv2
from cv2 import COLOR_BGR2GRAY

import sys
import numpy as np

if (len(sys.argv) > 1):
    path = sys.argv[1]
else:
    exit()

ONE_SECOND = 1e6
DEFAULT_FRAME_WIDTH = 1280 # pixels
DEFAULT_FRAME_HEIGHT = 720 # pixels

class raw_to_starfield:
    accumulation_time_us = 200000
    frame_delay_us = 4*ONE_SECOND # Time delay between the start and end frame
    start_ts = 0
    end_ts = 0
    start_frame = None 
    end_frame= None

    def __init__(self, path):
        self.path = path
    
    # Get start and end event frames over a specified duration and accumulation time.
    def get_frames(self, fps = 0.0):
        # Events iterator
        mv_iterator = EventsIterator(input_path=self.path, max_duration=self.frame_delay_us)
        height, width = mv_iterator.get_size()

        # Event Frame Generator
        event_frame_gen = PeriodicFrameGenerationAlgorithm(width, height, self.accumulation_time_us, fps)
        event_frame_gen.set_output_callback(self.on_cd_frame_cb)

        # Process events
        for evs in mv_iterator:
            event_frame_gen.process_events(evs)

    # Callback function to store frames
    def on_cd_frame_cb(self, ts, cd_frame):
        if ts <= self.accumulation_time_us:
            self.start_frame = cd_frame
            self.start_ts = ts
        else:
            self.end_frame = cd_frame
            self.end_ts = ts

    # Find the velocity which the stars are moving at. This is given in as the horizontal and vertical movement per microseconds(us)

    #TODO Improve robustness of the velocity estimation
    def get_velocity(self):
        # Determine the time difference in microseconds
        time_dif_us = (self.end_ts - self.start_ts)

        # Convert to grayscale
        start_gray = cv2.cvtColor(self.start_frame, COLOR_BGR2GRAY)
        end_gray = cv2.cvtColor(self.end_frame, COLOR_BGR2GRAY)
        
        # Blur images
        start_blur = cv2.blur(start_gray, (9,9))
        end_blur = cv2.blur(end_gray, (9,9))

        # Set the inital guess for the velocity
        translation = self.intial_guess(start_blur, end_blur)
        print(translation)

        # Rough transform with filtered images.
        (cc, translation) = cv2.findTransformECC(start_blur, end_blur, translation, cv2.MOTION_TRANSLATION)
        print(translation)

        # Fine transform with original images.
        (cc, translation) = cv2.findTransformECC(start_gray, end_gray, translation, cv2.MOTION_TRANSLATION)
        print(translation)

        v_x = translation[0,2]*(1/time_dif_us)
        v_y = translation[1,2]*(1/time_dif_us)

        # Debugging
        # shape = self.start_frame.shape
        # end_aligned = cv2.warpAffine(start_blur, translation, (shape[1],shape[0]))
        # cv2.imwrite("output/start_blur.jpg", start_blur)
        # cv2.imwrite("output/end_blur.jpg", end_blur)
        # cv2.imwrite("output/aligned.jpg", end_aligned)

        return [v_x,v_y]

    def top_k_pixels(self, k, image):
        max = np.max(image)

        for i in range(len(image)):
            for j in range(len(image[i])):
                if image[i,j] < (max - k*max):
                    image[i,j] = 0
                else:
                    image[i,j] = 1000

        return image

    # Generate an initial guess for the transformation, This is done by finding the distance between the brightest pixels in each image.
    def intial_guess(self, image1, image2):
        p1 = np.unravel_index(np.argmax(image1), image1.shape)
        p2 = np.unravel_index(np.argmax(image2), image2.shape)
        x = p2[1]-p1[1]
        y = p2[0]-p1[0]

        # If the initial guess is infeasible. Return standard guess
        if (abs(x) > 100 or abs(y) > 100):
            return np.eye(2,3,dtype=np.float32)

        out = np.array([[1.0,0.0,x],[0.0,1.0,y]], dtype=np.float32)
        return out

    # Generate a star-field using event data over a given duration.
    def generate_star_field(self, duration_us, name):
        self.get_frames()
        velocity = self.get_velocity()
        print(velocity)

        width = DEFAULT_FRAME_WIDTH + int(abs(velocity[0])*(duration_us+10*ONE_SECOND))
        height = DEFAULT_FRAME_HEIGHT + int(abs(velocity[1])*(duration_us+10*ONE_SECOND))
        image = np.zeros((height, width))
        print(image.shape)

        mv_iterator = EventsIterator(input_path=self.path, max_duration=duration_us)

        # Read each 'ON' event and determine the sky coordinates.
        for evs in mv_iterator:
            for (x, y, p, t) in evs:
                if (p==1):
                    x_coord = int(x - velocity[0]*t)
                    y_coord = int(y - velocity[1]*t)
                    image[y_coord, x_coord] = image[y_coord, x_coord] + 0.5 #TODO Determine best value to increase by

        cv2.imwrite(name, image)

    # Helper function
    def write_frames(self):
        cv2.imwrite("start.jpg", self.start_frame)
        cv2.imwrite("end.jpg", self.end_frame)


player = raw_to_starfield(path)
player.generate_star_field(30*ONE_SECOND, "output.jpg")