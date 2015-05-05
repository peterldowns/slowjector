#!/usr/bin/env python
# coding: utf-8
# Based on http://noah.org/wiki/movement.py
# TODO(peter): restore license
import cv2
import sys
import signal
import time
from threading import Thread
from Queue import Queue

# The two main parameters that affect movement detection sensitivity
# are BLUR_SIZE and NOISE_CUTOFF. Both have little direct effect on
# CPU usage. In theory a smaller BLUR_SIZE should use less CPU, but
# for the range of values that are effective the difference is
# negligible. The default values are effective with on most light
# conditions with the cameras I have tested. At these levels the
# detectory can easily trigger on eye blinks, yet not trigger if the
# subject remains still without blinking. These levels will likely be
# useless outdoors.
BLUR_SIZE = 3
NOISE_CUTOFF = 12
# Ah, but the third main parameter that affects movement detection
# sensitivity is the time between frames. I like about 10 frames per
# second. Even 4 FPS is fine.
#FRAMES_PER_SECOND = 10

QUICK_CATCHUP_TO_REALITY = True

def displayThread(framequeue):
  # Open a window in which to display the images
  display_window_name = "now view"
  cv2.namedWindow(display_window_name, cv2.CV_WINDOW_AUTOSIZE)
  last_frame_delta = 0
  while True:
    time.sleep(0.001) # Small amount of sleeping for thread-switching
    data = framequeue.get()
    # Source thread will put None if it receives c-C; if this happens, exit the
    # loop and shut off the display.
    if data is None:
      break
    # Otherwise, it puts a tuple (frame_delta, image)
    frame_delta, image = data

    # Draw the image
    cv2.imshow(display_window_name, image)

    # Optionally, catch up to the live feed after seeing some motion stop by
    # popping all images off of the queue.
    if (QUICK_CATCHUP_TO_REALITY and
        frame_delta <= 100 and last_frame_delta >= 100):
      while not framequeue.empty():
        framequeue.get()

    last_frame_delta = frame_delta

  # Clean up by closing the window used to display images.
  cv2.destroyWindow(display_window_name)


def main():
  cam = cv2.VideoCapture(0)
  # 640*480 = 307200 pixels
  cam.set(3,640)
  cam.set(4,480)

  # Stabilize the detector by letting the camera warm up and
  # seeding the first frames.
  frame_now = cam.read()[1]
  frame_now = cam.read()[1]
  frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
  frame_now = cv2.blur(frame_now, (BLUR_SIZE, BLUR_SIZE))
  frame_prior = frame_now

  delta_count_last = 1
  framequeue = Queue()
  t = Thread(target=displayThread, args=(framequeue,))
  t.start()
  # Quit via c-C
  def signal_handler(signal, frame):
    framequeue.put(None)
    t.join()
    sys.exit(0)
  signal.signal(signal.SIGINT, signal_handler)

  while True:
    time.sleep(0.001) # Small amount of sleeping for thread-switching
    frame_delta = cv2.absdiff(frame_prior, frame_now)
    frame_delta = cv2.threshold(frame_delta, NOISE_CUTOFF, 255, 3)[1]
    delta_count = cv2.countNonZero(frame_delta)

    # Visual detection statistics output.
    # Normalize improves brightness and contrast.
    # Mirror view makes self display more intuitive.
    cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)
    frame_delta = cv2.flip(frame_delta, 1)
    cv2.putText(frame_delta, "DELTA: %d" % (delta_count),
        (5, 15), cv2.FONT_HERSHEY_PLAIN, 0.8, (255, 255, 255))

    dst = cv2.flip(frame_now, 1)
    dst = cv2.addWeighted(dst,1.0, frame_delta,0.9,0)

    # Add frame to queue
    if delta_count < 5000:
      duplicates = 1
    else:
      duplicates = max(delta_count / 5000, 1)
      duplicates = min(duplicates, 16)
    for i in xrange(duplicates):
      framequeue.put((delta_count_last, dst))

    delta_count_last = max(delta_count - 5000, 0)

    # Advance the frames.
    frame_prior = frame_now
    frame_now = cam.read()[1]
    frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
    frame_now = cv2.blur(frame_now, (BLUR_SIZE, BLUR_SIZE))
  print 'Read thread done.'

if __name__ == '__main__':
  main()
