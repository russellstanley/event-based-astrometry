from metavision_core.event_io import EventsIterator
from metavision_sdk_core import PeriodicFrameGenerationAlgorithm
from metavision_sdk_ui import EventLoop, BaseWindow, Window, UIAction, UIKeyEvent

import sys

accumulation_time_us = 200000
fps = 30.0

if (len(sys.argv) > 1):
    path = sys.argv[1]
else:
    exit()

def main():
    mv_iterator = EventsIterator(input_path=path)
    height, width = mv_iterator.get_size()

    # Window - Graphical User Interface
    with Window(title="Metavision SDK Get Started", width=width, height=height, mode=BaseWindow.RenderMode.BGR) as window:
        def keyboard_cb(key, scancode, action, mods):
            if action != UIAction.RELEASE:
                return
            if key == UIKeyEvent.KEY_ESCAPE or key == UIKeyEvent.KEY_Q:
                window.set_close_flag()

        window.set_keyboard_callback(keyboard_cb)

        # Event Frame Generator
        event_frame_gen = PeriodicFrameGenerationAlgorithm(width, height, accumulation_time_us, fps)

        def on_cd_frame_cb(ts, cd_frame):
            window.show(cd_frame)

        event_frame_gen.set_output_callback(on_cd_frame_cb)

        # Process events
        for evs in mv_iterator:
            # Dispatch system events to the window
            EventLoop.poll_and_dispatch()
            event_frame_gen.process_events(evs)

            if window.should_close():
                break

main()