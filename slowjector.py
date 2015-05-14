# coding: utf-8
from Queue import Queue
from threading import Thread
from time import sleep

import click
import cv2

from control_c import control_c_protect
from control_c import make_control_c_handler
from movement import compare_frames
from movement import process_frame_for_comparison


def slowjector(
    device_id=0,
    src_width=640,
    src_height=480,
    motion_threshold_ratio=0.005,
    motion_unit_ratio=0.005,
    max_frame_count=24,
    quick_catchup=True,
    quick_catchup_ratio=0.002,
    show_delta_text=False,
    mirror_src=True,
    raw_output=False,
    sparkle_motion=True):
  total_pixels = src_width * src_height
  motion_threshold_pixels = int(motion_threshold_ratio * total_pixels)
  motion_unit_pixels = int(motion_unit_ratio * total_pixels)
  quick_catchup_pixels = int(quick_catchup_ratio * total_pixels)

  vidya = cv2.VideoCapture(device_id)
  vidya.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, src_width)
  vidya.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, src_height)

  # Set up the display thread that draws images on the screen.
  framequeue = Queue()
  display_thread = Thread(
      target=display_loop,
      args=(framequeue, quick_catchup, quick_catchup_pixels))
  display_thread.daemon = True

  # Run the source loop in a wrapper that cleans up if an exception occurs.
  cc_handler = make_control_c_handler(framequeue, display_thread)
  source_loop = control_c_protect(
      make_source_loop(raw_output,
                       mirror_src,
                       sparkle_motion,
                       show_delta_text,
                       motion_threshold_pixels,
                       motion_unit_pixels,
                       max_frame_count),
      cc_handler)

  # Start the external display thread
  display_thread.start()
  # Start reading from the camera
  source_loop(vidya, total_pixels, framequeue)


def display_loop(framequeue, quick_catchup, quick_catchup_pixels):
  # Open a window in which to display the images
  display_window_name = "slowjector"
  cv2.namedWindow(display_window_name, cv2.cv.CV_WINDOW_NORMAL)
  last_delta_count = 0
  listq = []
  while True:
    sleep(0.001) # Small amount of sleeping for thread-switching
    data = framequeue.get()
    # Source thread will put None if it receives c-C; if this happens, exit the
    # loop and shut off the display.
    if data is None:
      break

    listq.append(data)
    data = listq.pop(0)

    # Otherwise, it puts a tuple (delta_count, image)
    delta_count, image = data

    # Draw the image
    cv2.imshow(display_window_name, image)

    # Optionally, catch up to the live feed after seeing some motion stop by
    # popping all images off of the queue.
    if (quick_catchup and
        delta_count <= quick_catchup_pixels and
        last_delta_count > quick_catchup_pixels):
      listqueue = []
    last_delta_count = delta_count

  # Clean up by closing the window used to display images.
  cv2.destroyWindow(display_window_name)


def make_source_loop(raw_output,
                     mirror_src,
                     sparkle_motion,
                     show_delta_text,
                     motion_threshold_pixels,
                     motion_unit_pixels,
                     max_frame_count):
  def source_loop(vidya, total_pixels, framequeue):
    # Set up variables used for comparing values against the previous frame.
    last_frame_delta = 0
    previous_frame = None
    current_frame = None

    # Stabilize the detector by letting the camera warm up and seeding the first
    # frame.
    while previous_frame is None:
      previous_frame = current_frame
      _, raw_frame = vidya.read()
      current_frame = process_frame_for_comparison(raw_frame)

    # The main loop.
    while True:
      sleep(0.001) # Small amount of sleeping for thread-switching

      # Advance the frames.
      _, raw_frame = vidya.read()
      current_frame = process_frame_for_comparison(raw_frame)
      frame_delta, delta_count = compare_frames(previous_frame, current_frame)

      # Visual detection statistics output.
      # Normalize improves brightness and contrast.
      # Mirror view makes self display more intuitive.
      cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)

      output_image = current_frame
      if raw_output:
        output_image = raw_frame

      if mirror_src:
        frame_delta = cv2.flip(frame_delta, 1)
        output_image = cv2.flip(output_image, 1)

      if sparkle_motion:
        if raw_output:
          matched_frame_delta = cv2.cvtColor(frame_delta, cv2.COLOR_GRAY2RGB)
        else:
          matched_frame_delta = frame_delta
        output_image = cv2.addWeighted(
            output_image, 1.0, matched_frame_delta, 0.9, 0)

      if show_delta_text:
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
                          max_frame_count)
      for i in xrange(frame_count):
        framequeue.put((delta_count, output_image))

      last_frame_delta = delta_count
      previous_frame = current_frame
  return source_loop
