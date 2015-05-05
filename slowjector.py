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
SHOW_DELTA_TEXT = False
MIRROR_SOURCE_IMAGE = True

def displayThread(framequeue):
  # Open a window in which to display the images
  display_window_name = "now view"
  cv2.namedWindow(display_window_name, cv2.CV_WINDOW_AUTOSIZE)
  last_delta_count = 0
  while True:
    time.sleep(0.001) # Small amount of sleeping for thread-switching
    data = framequeue.get()
    # Source thread will put None if it receives c-C; if this happens, exit the
    # loop and shut off the display.
    if data is None:
      break
    # Otherwise, it puts a tuple (delta_count, image)
    delta_count, image = data

    # Draw the image
    cv2.imshow(display_window_name, image)

    # Optionally, catch up to the live feed after seeing some motion stop by
    # popping all images off of the queue.
    if (QUICK_CATCHUP_TO_REALITY and
        # TODO(peter): 100 -> variable
        delta_count <= 100 and last_delta_count >= 100):
      while not framequeue.empty():
        framequeue.get()
    last_delta_count = delta_count
  # Clean up by closing the window used to display images.
  cv2.destroyWindow(display_window_name)


def slowjector(device_id=0,
               src_width=640,
               src_height=480,
               motion_threshold_ratio=0.01,
               max_slowmo_frames=16):
  cam = cv2.VideoCapture(device_id)
  cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, src_width)
  cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, src_height)
  total_pixels = src_width * src_height
  motion_threshold_pixels = int(motion_threshold_ratio * total_pixels)

  # Stabilize the detector by letting the camera warm up and
  # seeding the first frames.
  current_frame = cam.read()[1]
  current_frame = cam.read()[1]
  current_frame = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)
  current_frame = cv2.blur(current_frame, (BLUR_SIZE, BLUR_SIZE))
  previous_frame = current_frame

  last_frame_delta = 1
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

    # Advance the frames.
    current_frame = cam.read()[1]
    current_frame = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)
    current_frame = cv2.blur(current_frame, (BLUR_SIZE, BLUR_SIZE))
    frame_delta = cv2.absdiff(previous_frame, current_frame)
    frame_delta = cv2.threshold(frame_delta, NOISE_CUTOFF, 255, 3)[1]
    delta_count = cv2.countNonZero(frame_delta)

    # Visual detection statistics output.
    # Normalize improves brightness and contrast.
    # Mirror view makes self display more intuitive.
    cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)
    if MIRROR_SOURCE_IMAGE:
      frame_delta = cv2.flip(frame_delta, 1)
      processed_image = cv2.flip(current_frame, 1)
    else:
      processed_image = current_frame

    processed_image = cv2.addWeighted(processed_image, 1.0, frame_delta, 0.9, 0)
    if SHOW_DELTA_TEXT:
      cv2.putText(processed_image, "DELTA: %d" % (delta_count),
          (5, 15), cv2.FONT_HERSHEY_PLAIN, 0.8, (255, 255, 255))

    # Add frame to queue, more times if there's more motion.
    if delta_count < motion_threshold_pixels:
      frame_count = 1
    else:
      frame_count = min(delta_count / motion_threshold_pixels,
                        max_slowmo_frames)
    for i in xrange(frame_count):
      framequeue.put((delta_count, processed_image))

    last_frame_delta = delta_count
    previous_frame = current_frame

if __name__ == '__main__':
  slowjector()
