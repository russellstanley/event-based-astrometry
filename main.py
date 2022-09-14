import sys
import time
import starfield
import noise

# DVX Format
#t(Unix), x, y, p

# Load event file path
if (len(sys.argv) > 1):
    file_path = sys.argv[1]
else:
    exit()

# Load blank event file path
if (len(sys.argv) > 2):
    blank_path = sys.argv[2]

    player = noise.find_hot_pixels(blank_path, "PRO")
    player.write_hot_pixels(95)

start_time = time.time()

player = starfield.csv_to_starfield(file_path, "PRO_CSV")
data = player.generate_star_field(30*starfield.ONE_SECOND, file_path + ".jpg", hot_pixels_path=noise.FILE_PATH)

print("total: %s sec" % (time.time() - start_time))