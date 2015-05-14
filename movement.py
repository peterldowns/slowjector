# coding: utf-8
import cv2


# From Noah's movement.py code:
#   The two main parameters that affect movement detection sensitivity are
#   BLUR_SIZE and NOISE_CUTOFF. Both have little direct effect on CPU usage. In
#   theory a smaller BLUR_SIZE should use less CPU, but for the range of values
#   that are effective the difference is negligible. The default values are
#   effective with on most light conditions with the cameras I have tested. At
#   these levels the detectory can easily trigger on eye blinks, yet not
#   trigger if the subject remains still without blinking. These levels will
#   likely be useless outdoors.
def process_frame_for_comparison(raw_frame):
  blur_size = 3
  processed_frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2GRAY)
  processed_frame = cv2.blur(processed_frame, (blur_size, blur_size))
  return processed_frame


def compare_frames(previous_frame, current_frame):
  noise_cutoff = 12
  frame_delta = cv2.absdiff(previous_frame, current_frame)
  _, frame_delta = cv2.threshold(frame_delta, noise_cutoff, 255, 3)
  delta_count = cv2.countNonZero(frame_delta)
  return frame_delta, delta_count
