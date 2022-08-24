import cv2

from astropy.stats import sigma_clipped_stats
from photutils.detection import find_peaks
from photutils.centroids import *
from photutils.datasets import make_100gaussians_image

import numpy as np
import matplotlib.pyplot as plt
from astropy.visualization import simple_norm
from astropy.visualization.mpl_normalize import ImageNormalize
from photutils.aperture import CircularAperture

data = cv2.imread("sample_data/sample_1.jpg", cv2.IMREAD_GRAYSCALE)
mean, median, std = sigma_clipped_stats(data, sigma=3.0)
cv2.imwrite("gaussian.jpg", data)

threshold = median + (10. * std)

tbl = find_peaks(data, threshold, box_size=11)

tbl['peak_value'].info.format = '%.8g'  # for consistent table output

print(tbl[:10])  # print only the first 10 peaks

positions = np.transpose((tbl['x_peak'], tbl['y_peak']))
apertures = CircularAperture(positions, r=5.)
norm = simple_norm(data, 'sqrt', percent=99.9)

plt.imshow(data, cmap='Greys_r', origin='lower', norm=norm, interpolation='nearest')
apertures.plot(color='#0547f9', lw=1.5)
plt.xlim(0, data.shape[1] - 1)
plt.ylim(0, data.shape[0] - 1)
plt.show()