import threading


""" Decorator to add app context to given function - used for the functions that run in separate thread
as they lose Flask's app's context """
def add_app_context(context):

  def middle(func):

    def wrapper(*args, **kwargs):
      context.push()
      return func(*args, **kwargs)

    return wrapper

  return middle


""" decorator to run the function in separate thread """
def run_in_thread(func):

  def wrapper(*args):
    thread = threading.Thread(daemon=True, target=func, args=args)
    thread.start()
  return wrapper
