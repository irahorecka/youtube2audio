import errno
import os
import signal
from functools import wraps


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    """A wrapper for request methods. Default time before
    timeout is 10 seconds - change as necessary. This wrapper
    will only work in the main thread."""

    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator
