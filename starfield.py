import cv2
import sys
import numpy as np

if (len(sys.argv) > 1):
    path = sys.argv[1]
else:
    exit()

if len(sys.argv) > 2:
    format = sys.argv[2]
else:
    format = ""

# DVX Format
#t(Unix), x, y, p


ONE_SECOND = 1e6
DEFAULT_FRAME_WIDTH = 1280 # pixels
DEFAULT_FRAME_HEIGHT = 720 # pixels

class raw_to_starfield:
    accumulation_time_us = 200000
    frame_delay_us = 8*ONE_SECOND # Time delay between the start and end frame
    start_ts = 0
    end_ts = 0
    frame_height = DEFAULT_FRAME_HEIGHT
    frame_width = DEFAULT_FRAME_WIDTH
    start_frame = None 
    end_frame= None

    def __init__(self, path):
        self.path = path

        # Read events from file. Skip the first 2 entries as for some files these will be headers.
        self.events = np.genfromtxt(path, delimiter=",", dtype=int, skip_header=2)
        self.format()

    def format(self):
        print("Format: " + format)
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

    
    # Get start and end event frames over a specified duration and accumulation time.
    def get_frames(self):
        time_offset = self.events[0][2]
        times_us = self.events[:,3]

        # Get the start frame.
        low_bound = time_offset
        up_bound = time_offset + self.accumulation_time_us
        mask = ((times_us > low_bound) & (times_us < up_bound))
        self.start_frame = self.frame_generator(self.events[mask])
        self.start_ts = int(time_offset)

        # Get the end frame.
        low_bound = self.frame_delay_us - self.accumulation_time_us + time_offset
        up_bound = self.frame_delay_us + time_offset
        mask = ((times_us > low_bound) & (times_us < up_bound))
        self.end_frame = self.frame_generator(self.events[mask])
        self.end_ts = int(self.frame_delay_us + time_offset)

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

    #TODO Improve robustness of the velocity estimation
    def get_velocity(self):
        # Determine the time difference in microseconds
        time_dif_us = (self.end_ts - self.start_ts)
        
        # Blur images
        start_blur = cv2.blur(self.start_frame, (9,9))
        end_blur = cv2.blur(self.end_frame, (9,9))

        # Set the inital guess for the velocity
        translation = self.intial_guess(start_blur, end_blur)
        print(translation)

        # Rough transform with filtered images.
        (cc, translation) = cv2.findTransformECC(start_blur, end_blur, translation, cv2.MOTION_TRANSLATION)
        print(translation)

        # Fine transform with original images.
        (cc, translation) = cv2.findTransformECC(self.start_frame, self.end_frame, translation, cv2.MOTION_TRANSLATION)
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

        width = self.frame_width + int(abs(velocity[0])*(duration_us+10*ONE_SECOND))
        height = self.frame_height + int(abs(velocity[1])*(duration_us+10*ONE_SECOND))
        image = np.zeros((height, width))
        print(image.shape)

        # Read each 'ON' event and determine the sky coordinates.
        for (x, y, p, t) in self.events:
            if (p==1):
                x_coord = int(x - velocity[0]*t)
                y_coord = int(y - velocity[1]*t)
                image[y_coord, x_coord] = image[y_coord, x_coord] + 0.5 #TODO Determine best value to increase by

            if (t > duration_us):
                break

        cv2.imwrite(name, image)

    # Helper function
    def write_frames(self):
        cv2.imwrite("start.jpg", self.start_frame)
        cv2.imwrite("end.jpg", self.end_frame)


player = raw_to_starfield(path)
player.generate_star_field(30*ONE_SECOND, path + ".jpg")