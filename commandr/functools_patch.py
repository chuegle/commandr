"""Monkey-patch for functools 'wraps' and 'update_wrapper' that add an
additional property to each wrapper containing the original wrapped object.
"""

import functools

_update_wrapper_original = functools.update_wrapper

def update_wrapper_plus(wrapper, wrapped, *args, **kwargs):
  wrapper = _update_wrapper_original(wrapper, wrapped, *args, **kwargs)
  setattr(wrapper, '__wrapped__', wrapped)
  return wrapper

functools.update_wrapper = update_wrapper_plus
