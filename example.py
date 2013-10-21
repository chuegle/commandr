# Copyright 2013 TellApart, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# =============================================================================
"""Example usage of commandr."""

from commandr import command, Run, Usage, wraps

@command('greet')
def SayGreeting(name, title='Mr.', times=1, comma=False, caps_lock=False):
  """Greet someone.

  Arguments:
    name - Name to greet.
    title - Title of the person to greet.
    times - Number of time to say the greeting.
    comma - Whether to add a comma after the greeting.
    caps_lock - Whether to output in ALL CAPS.
  """
  message = 'Hi%s %s %s!' % (',' if comma else '', title, name)
  if caps_lock:
    message = message.upper()

  for _ in xrange(times):
    print message

@command
def simple_greet(name):
  """An example of @command without arguments and printing Usage.

  Arguments:
    name - Name to greet.
  """
  if name == 'John':
    Usage("We don't like John")
  print 'Hi %s!' % name

def ConvertToDict(key, value):
  """Converts str of format 'a=b;c=d;e=f' to a dict."""
  if not isinstance(value, dict):
    return dict(kv.split('=', 1) for kv in value.split(';'))
  else:
    # if value is not returned here, the new value will be None
    return value

@command(validate={'name':['Kevin', 'Nick', 'Mike', 'Wade']},
         transform={'name':lambda k,v: v.capitalize(),
                    'extra':ConvertToDict})
def another_simple_greet(name=None, extra={'hi':'Aloha', 'end':'!'}):
  """An example of @command(), specifying the possible values for name.

  This overrides the global capitalization check.

  Arguments:
    name - Name to greet.  It must be capitalized.
    extra - Containing the 'hi' message and the end of the sentence '!'.
            Format: --extra "hi=Hi;end=..."
  """
  print '%s %s%s' % (extra['hi'], name, extra['end'])

def some_decorator(fn):
  @wraps(fn)
  def _wrapper(*args, **kwargs):
    print 'Wrapper Here!'
    return fn(*args, **kwargs)
  return _wrapper

@command('test_decorated')
@some_decorator
def DecoratedFunction(arg1, arg2=1):
    """An example usage of stacked decorators."""
    print arg1, arg2

def NameCheck(arg_name, arg_value):
  """A name must be capitalized.

  This doc will be printed up to the first empty line if the check fails.
  """
  return arg_value == arg_value.capitalize()

if __name__ == '__main__':
  # This requires every command that uses 'name' as an argument to make sure
  # that name is capitalized, unless the possible_value is overridden.
  Run(hyphenate=True, validate={'name':NameCheck})
