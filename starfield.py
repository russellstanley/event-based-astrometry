from tkinter import ON
import cv2
import numpy as np
import reader
import time

# DVX Format
#t(Unix), x, y, p

ONE_SECOND = 1e6
DEFAULT_FRAME_WIDTH = 1280 # pixels
DEFAULT_FRAME_HEIGHT = 720 # pixels

class csv_to_starfield(reader.read_events):
    accumulation_time_us = 200000
    start_ts = 0
    end_ts = 0
    frame_height = DEFAULT_FRAME_HEIGHT
    frame_width = DEFAULT_FRAME_WIDTH
    start_frame = None 
    end_frame= None
    hot_pixels = {}

    # load_noise will generate a map of hot pixel coordinates and their respective scale. 
    def load_noise(self, path):
        pixels = np.loadtxt(path, delimiter=",", dtype=int)
        self.hot_pixels = {}

        for (x, y, scale) in pixels:
            key = self.generate_key(x,y)
            self.hot_pixels.update({key:scale})
    
    # Get start and end event frames over a specified duration and accumulation time.
    def get_frames(self, frame_delay_us):
        time_offset = self.events[0][2]
        times_us = self.events[:,3]

        # Get the start frame.
        low_bound = time_offset
        up_bound = time_offset + self.accumulation_time_us
        mask = ((times_us > low_bound) & (times_us < up_bound))
        self.start_frame = self.frame_generator(self.events[mask])
        self.start_ts = int(time_offset)

        # Get the end frame.
        low_bound = frame_delay_us - self.accumulation_time_us + time_offset
        up_bound = frame_delay_us + time_offset
        mask = ((times_us > low_bound) & (times_us < up_bound))
        self.end_frame = self.frame_generator(self.events[mask])
        self.end_ts = int(frame_delay_us + time_offset)

    # Output an event frame for the input events
    def frame_generator(self, events):
        image = np.zeros((self.frame_height, self.frame_width),np.uint8)

        for (x, y, p, t) in events:
            if (p==0):
                image[y, x] = 128
            elif(p==1):
                image[y, x] = 255
            else:
                return image

        return image

    # Find the velocity which the stars are moving at. This is given in as the horizontal and vertical movement per microseconds(us)
    def get_velocity(self, duration_us):
        translation = np.eye(2,3,dtype=np.float32)

        increment = int(duration_us/30)
        halfway = duration_us*0.5
        start = int(halfway-(increment*5))
        end = int(halfway+((increment*5)))

        print(start)
        print(end)

        for delay in range(start, end, increment):


            print(delay)

            self.get_frames(delay)
            
            # Blur images
            start_blur = cv2.blur(self.start_frame, (9,9))
            end_blur = cv2.blur(self.end_frame, (9,9))

            # Set the inital guess for the velocity
            guess = self.intial_guess(start_blur, end_blur)

            if (abs(guess[0,2]) >= 1.0 or abs(guess[1,2]) >= 1.0):
                translation = guess
                time_dif_us = (self.end_ts - self.start_ts)

        print(translation[:, 2])
        if translation[0,2] == 0 and translation[1,2] == 0:
            print("Error: could not find translation")
            return [0,0]

        # Transform with filtered images.
        (cc, translation) = cv2.findTransformECC(start_blur, end_blur, translation, cv2.MOTION_TRANSLATION)
        print(translation[:, 2])

        # Debugging
        # shape = self.start_frame.shape
        # end_aligned = cv2.warpAffine(start_blur, translation, (shape[1],shape[0]))
        # cv2.imwrite("output/start_blur.jpg", start_blur)
        # cv2.imwrite("output/end_blur.jpg", end_blur)
        # cv2.imwrite("output/aligned.jpg", end_aligned)

        v_x = translation[0,2]*(1/time_dif_us)
        v_y = translation[1,2]*(1/time_dif_us)

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

    def normalize(self, image):
        max_pixel = np.max(image)
        min_pixel = np.min(image)

        for i in range(len(image)):
            for j in range(len(image[i])):
                image[i,j] = ((image[i,j] - min_pixel)/(max_pixel - min_pixel))*255

        return image

    # Generate a star-field using event data over a given duration.
    def generate_star_field(self, duration_us, name, hot_pixels_path=""):

        # Generate noise map if a path is given
        if hot_pixels_path != "":
            self.load_noise(hot_pixels_path)

        start_time = time.time()
        velocity = self.get_velocity(duration_us)
        if velocity[0] == 0 and velocity[1] == 0:
            return
        print("get_velocity: %s sec" % (time.time() - start_time))

        width = self.frame_width + int(abs(velocity[0])*(duration_us+10*ONE_SECOND))
        height = self.frame_height + int(abs(velocity[1])*(duration_us+10*ONE_SECOND))
        image = np.zeros((height, width))

        start_time = time.time()
        # Read each 'ON' event and determine the sky coordinates.
        for (x, y, p, t) in self.events:
            if (p==1 and self.hot_pixels.get(self.generate_key(x,y)) == None):
                x_coord = int(x - velocity[0]*t)
                y_coord = int(y - velocity[1]*t)
                image[y_coord, x_coord] = image[y_coord, x_coord] + 1 #TODO Determine best value to increase by

            if (t > duration_us):
                break
        print("image_generation: %s sec" % (time.time() - start_time))

        cv2.imwrite(name, image)


    # Helper function
    def write_frames(self):
        cv2.imwrite("start.jpg", self.start_frame)
        cv2.imwrite("end.jpg", self.end_frame)