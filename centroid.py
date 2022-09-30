import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
import sys

from astropy.visualization import simple_norm

from photutils.detection import find_peaks
from photutils.segmentation import detect_threshold
from photutils.centroids import centroid_com
from photutils.aperture import CircularAperture

FOCAL_LENGTH = 400 # millimeters

class centroid:
    data = None
    positions = None

    def __init__(self, file_path):
        self.file_path = file_path

    def get_peaks(self):
        # Load data.
        self.data = cv2.imread(self.file_path, cv2.IMREAD_GRAYSCALE)
        threshold = detect_threshold(self.data, nsigma=12.0)

        # Find centroid in starfield.
        tbl = find_peaks(self.data, threshold, box_size=11, npeaks=50, centroid_func=centroid_com)

        self.positions = np.transpose((tbl['x_centroid'], tbl['y_centroid']))


    def draw(self, circles=True):
        apertures = CircularAperture(self.positions, r=5.)
        norm = simple_norm(self.data, 'sqrt', percent=99.9)

        img = plt.imshow(self.data, cmap='Greys_r', origin='lower', norm=norm, interpolation='nearest')

        if (circles):
            apertures.plot(color='#0547f9', lw=1)

        plt.axis('off')

        plt.xlim(0, self.data.shape[1] - 1)
        plt.ylim(0, self.data.shape[0] - 1)
        plt.savefig(self.file_path[0:len(self.file_path)-4] + "_boosted.jpg", dpi=500, bbox_inches="tight", pad_inches=0.0)

    def get_body_vectors(self):
        cx, cy = self.data.shape
        cx = int(cx/2)
        cy = int(cy/2)
        result = np.ones((0,3))

        for (i,j) in self.positions:
            x = i - cx
            y = j - cy

            azimuth = math.pi - math.atan2(y,x)
            elevation = math.pi/2 - math.atan((math.sqrt(x**2+y**2))/FOCAL_LENGTH)

            vx = math.cos(azimuth)*math.cos(elevation)
            vy = math.sin(azimuth)*math.cos(elevation)
            vz = math.sin(elevation)

            result = np.vstack((result, np.array([vx, vy, vz])))

        print(result)
        return result