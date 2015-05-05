#!/usr/bin/env python
# coding: utf-8
import cv2
import signal
import sys
import time
import traceback
from threading import Thread
from Queue import Queue


QUICK_CATCHUP_TO_REALITY = True
QUICK_CATCHUP_DELTA_LIMIT = 100
SHOW_DELTA_TEXT = True
MIRROR_SOURCE_IMAGE = True
PROCESS_BLUR = True
RAW_FRAME_OUTPUT = False
INCLUDE_DELTA_IN_OUTPUT = True


# From Noah's movement.py code:
#   The two main parameters that affect movement detection sensitivity are
#   BLUR_SIZE and NOISE_CUTOFF. Both have little direct effect on CPU usage. In
#   theory a smaller BLUR_SIZE should use less CPU, but for the range of values
#   that are effective the difference is negligible. The default values are
#   effective with on most light conditions with the cameras I have tested. At
#   these levels the detectory can easily trigger on eye blinks, yet not
#   trigger if the subject remains still without blinking. These levels will
#   likely be useless outdoors.
BLUR_SIZE = 3
NOISE_CUTOFF = 12

def process_frame_for_comparison(raw_frame):
  processed_frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2GRAY)
  if PROCESS_BLUR:
    processed_frame = cv2.blur(processed_frame, (BLUR_SIZE, BLUR_SIZE))
  return processed_frame

def compare_frames(previous_frame, current_frame):
  frame_delta = cv2.absdiff(previous_frame, current_frame)
  _, frame_delta = cv2.threshold(frame_delta, NOISE_CUTOFF, 255, 3)
  delta_count = cv2.countNonZero(frame_delta)
  return frame_delta, delta_count

def displayThread(framequeue):
  # Open a window in which to display the images
  display_window_name = "slowjector"
  cv2.namedWindow(display_window_name, cv2.cv.CV_WINDOW_NORMAL)
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
        delta_count <= QUICK_CATCHUP_DELTA_LIMIT and
        last_delta_count > QUICK_CATCHUP_DELTA_LIMIT):
      print 'catching up...'
      num_frames_skipped = 0
      while not framequeue.empty():
        framequeue.get()
        num_frames_skipped += 1
      print 'skipped %d frames' % num_frames_skipped
    last_delta_count = delta_count

  # Clean up by closing the window used to display images.
  cv2.destroyWindow(display_window_name)


def slowjector(device_id=0,
               src_width=640,
               src_height=480,
               motion_threshold_ratio=0.06,
               motion_unit_ratio=0.01,
               max_slowmo_frames=16):
  cam = cv2.VideoCapture(device_id)
  cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, src_width)
  cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, src_height)
  total_pixels = src_width * src_height
  motion_threshold_pixels = int(motion_threshold_ratio * total_pixels)
  motion_unit_pixels = int(motion_unit_ratio * total_pixels)

  # Set up the display thread that draws images on the screen.
  framequeue = Queue()
  display_thread = Thread(target=displayThread, args=(framequeue,))

  # Enable quitting via c-C.
  def control_c(*_):
    print ''
    if display_thread.is_alive():
      framequeue.put(None)  # Signals to the display thread to clean itself up.
      display_thread.join() # Wait for the cleanup to happen.
    sys.exit(0)

  signal.signal(signal.SIGINT, control_c)

  def source_loop():
    # Set up variables used for comparing values against the previous frame.
    last_frame_delta = 0
    previous_frame = None
    current_frame = None

    # Stabilize the detector by letting the camera warm up and seeding the first
    # frame.
    while previous_frame is None:
      previous_frame = current_frame
      _, raw_frame = cam.read()
      current_frame = process_frame_for_comparison(raw_frame)

    # Start the external display thread
    display_thread.start()
    while True:
      time.sleep(0.001) # Small amount of sleeping for thread-switching

      # Advance the frames.
      _, raw_frame = cam.read()
      current_frame = process_frame_for_comparison(raw_frame)
      frame_delta, delta_count = compare_frames(previous_frame, current_frame)

      # Visual detection statistics output.
      # Normalize improves brightness and contrast.
      # Mirror view makes self display more intuitive.
      cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)

      output_image = current_frame
      if RAW_FRAME_OUTPUT:
        output_image = raw_frame

      if MIRROR_SOURCE_IMAGE:
        frame_delta = cv2.flip(frame_delta, 1)
        output_image = cv2.flip(output_image, 1)

      if INCLUDE_DELTA_IN_OUTPUT:
        if RAW_FRAME_OUTPUT:
          matched_frame_delta = cv2.cvtColor(frame_delta, cv2.COLOR_GRAY2RGB)
        else:
          matched_frame_delta = frame_delta
        output_image = cv2.addWeighted(
            output_image, 1.0, matched_frame_delta, 0.9, 0)

      if SHOW_DELTA_TEXT:
        cv2.putText(
            output_image,
            "DELTA: %.2f%% (%d/%d)" % (float(delta_count) / total_pixels * 100,
                                       delta_count,
                                       total_pixels),
            (5, 15),
            cv2.FONT_HERSHEY_PLAIN,
            0.8,
            (255, 255, 255))

      # Add frame to queue, more times if there's more motion.
      if delta_count <= motion_threshold_pixels:
        frame_count = 1
      else:
        frame_count = min(delta_count / motion_unit_pixels,
                          max_slowmo_frames)
      for i in xrange(frame_count):
        framequeue.put((delta_count, output_image))

      last_frame_delta = delta_count
      previous_frame = current_frame

  # Run the source loop in a wrapper that cleans up if an exception occurs.
  try:
    source_loop()
  except Exception as exception:
    traceback.print_exc(exception)
    control_c()


if __name__ == '__main__':
  slowjector()
