# coding: utf-8
import signal
import sys
import traceback

def make_control_c_handler(queue, thread):
  def handler(*_):
    print ''
    if thread.is_alive():
      print 'putting None...'
      queue.put(None)
      print 'waiting for join()...'
      thread.join()
      print 'done.'
    sys.exit(0)
  return handler


def control_c_protect(fn, handler):
  signal.signal(signal.SIGINT, handler)
  def wrapper(*args, **kwargs):
    # Run the source loop in a wrapper that cleans up if an exception occurs.
    try:
      fn(*args, **kwargs)
    except Exception as exception:
      traceback.print_exc(exception)
      handler()
  return wrapper
