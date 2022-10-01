import sys
import time
import starfield
import noise
import centroid
import glob

# DVX Format
#t(Unix), x, y, p

# Load event file path
if (len(sys.argv) > 1):
    path = sys.argv[1]
    if path.endswith(".raw"):
        # Single file
        files = [path]
    else:
        # Add directory
        files = glob.glob(path + "/*.raw")
else:
    exit()

# Load blank event file path
if (len(sys.argv) > 2):
    blank_path = sys.argv[2]

    player = noise.find_hot_pixels(blank_path)
    player.write_hot_pixels(95)

start_time = time.time()

for file_path in files:
    image_file = file_path[:len(file_path) - 4] + ".jpg"

    player = starfield.csv_to_starfield(file_path)
    data = player.generate_star_field(30*starfield.ONE_SECOND, image_file, hot_pixels_path=noise.FILE_PATH)


print("total: %s sec" % (time.time() - start_time))