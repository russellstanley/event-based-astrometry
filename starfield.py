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
DEFAULT_FRAME_WIDTH = 1280
DEFAULT_FRAME_HEIGHT = 720

class raw_to_starfield:
    accumulation_time_us = 200000
    duration_us = 1e7
    start_ts = 0
    start_frame = None 
    end_frame= None
    end_ts = 0

    def __init__(self, path):
        self.path = path
    
    # Get start and end event frames over a specified duration and accumulation time.
    def get_frames(self, fps = 0.0):
        # Events iterator on RAW file
        mv_iterator = EventsIterator(input_path=self.path, max_duration=self.duration_us)
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
        # Set the inital guess for the velocity
        translation = np.eye(2,3,dtype=np.float32)

        # Determine the time difference in microseconds
        time_dif_us = (self.end_ts - self.start_ts)

        start_gray = cv2.cvtColor(self.start_frame, COLOR_BGR2GRAY)
        end_gray = cv2.cvtColor(self.end_frame, COLOR_BGR2GRAY)
        shape = self.start_frame.shape

        start_gray_blur = cv2.blur(start_gray, (9,9))
        end_gray_blur = cv2.blur(end_gray, (9,9))

        # Rough transform with filtered images.
        (cc, translation) = cv2.findTransformECC(start_gray_blur, end_gray_blur, translation, cv2.MOTION_TRANSLATION)

        # Fine transform with original images.
        (cc, translation) = cv2.findTransformECC(start_gray, end_gray, translation, cv2.MOTION_TRANSLATION)

        v_x = translation[0,2]*(1/time_dif_us)
        v_y = translation[1,2]*(1/time_dif_us)

        # Debugging
        # end_aligned = cv2.warpAffine(end_gray, translation, (shape[1],shape[0]))
        # cv2.imwrite("start_grey.jpg", start_gray)
        # cv2.imwrite("end_gray.jpg", end_gray)
        # cv2.imwrite("aligned.jpg", end_aligned)

        return [v_x,v_y]

    # Generate a star-field using event data over a given duration.
    def generate_star_field(self, duration_us):
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
                    image[y_coord, x_coord] = image[y_coord, x_coord] + 1 #TODO Determine best value to increase by

        cv2.imwrite("output.jpg", image)

    # Helper function
    def write_frames(self):
        cv2.imwrite("start.jpg", self.start_frame)
        cv2.imwrite("end.jpg", self.end_frame)


player = raw_to_starfield(path)
player.generate_star_field(30*ONE_SECOND)