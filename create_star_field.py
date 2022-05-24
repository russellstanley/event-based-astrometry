from metavision_core.event_io import EventsIterator
import sys

if (len(sys.argv) > 1):
    path = sys.argv[1]
else:
    exit()


class raw_to_starfield:

    def __init__(self, path):
        # Events iterator on Camera or RAW file
        mv_iterator = EventsIterator(input_path=path, delta_t=1000)

        with open('cd.csv', 'w') as csv_file:

            # Read formatted CD events from EventsIterator & write to CSV
            for evs in mv_iterator:
                for (x, y, p, t) in evs:
                    csv_file.write("%d,%d,%d,%d\n" % (x, y, p, t))


raw_to_starfield(path)
