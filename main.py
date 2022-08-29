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

    player = noise.find_hot_pixels(blank_path, "DVX_CSV")
    player.write_hot_pixels(100)

start_time = time.time()

player = starfield.csv_to_starfield(file_path, "DVX")
player.generate_star_field(30*starfield.ONE_SECOND, file_path + ".jpg", hot_pixels_path=noise.FILE_PATH)

print("total: %s sec" % (time.time() - start_time))