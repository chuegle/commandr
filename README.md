commandr
========

commandr is a simple tool for making Python functions accessible from the
command line. Essentially you add a command decorator and you are off to
the races.

Example
-------
In example.py:
```python
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

  if __name__ == '__main__':
    Run()
````

The command can them be invoked on the command line with:
```bash
  $ python example.py greet --name=John
  Hi Mr. John!

  # Invoke with short parameter names
  $ python example.py greet -n=Nick -t=Dr. -c
  Hi, Dr. Nick!

  # Invoke with positional arguments
  $ python example.py greet Smith Ms.
  Hi Ms. Smith!

  # Combined explicit and positional arguments. In this case, 'Julie' will
  # match the first unspecified argument 'name'
  # 'caps_lock' is capital 'C' because 'comma' came first.  If a third argument
  # started with 'c', it would have no short option.
  # Equal signs are also optional.
  $ python example.py greet --title Engineer -c -C Julie
  HI, ENGINEER JULIE!
```

Installation
------------

To install commandr, simply:
```bash
$ pip install commandr
```
or
```bash
$ easy_install commandr
```

Features
--------

commandr creates command-line interfaces to Python functions through a decorator
that uses reflection to automatically convert a function's signature into a
command line parser.

The following script will be used to show examples of the features:

```python
  from commandr import command, Run

  @command('get', category='Database')
  def DoGet(key, timeout=10, cache=True):
    """Get an item from the database
    Arguments:
      key - Database key to get.
      timeout - Seconds to wait.
      cache - Whether to get from the local cache first.
    """
    ...

  @command('put', category='Database')
  def DoPut(key, value, timeout=10, transaction=False):
    """Put an item in the database.
    Arguments:
      key - Database key to put.
      value - String value to put.
      timeout - Seconds to wait.
      transaction - Whether to perform the put in a transaction
    """
    ...

  @command('status')
  def GetStatus(service=None):
    """Get the status of service, or all services.
    Arguments:
      service - If not None, get the status of this service, otherwise, get
                the status of all services.
    """
    ...

  @command('version')
  def GetVersion(host_name, dev=False):
    ...

  if __name__ == '__main__':
    Run()
```

### Parser Generation

The command-line interface to a function is generated based on the arguments in
the function's signature. Both regular and keyword arguments are supported.
Arguments can be bound on the command line explicitly by name, by the first
letter in the argument's name (limited to the first unique instance of that
letter), the capitalized letter of the first letter in the argument's name
(limited to the second unique instance of that letter) or positionally. For
example, the following are valid ways to invoke the 'put' command:
```bash
$ python features.py put --key=somekey --value somevalue
$ python features.py put -k somekey -v somevalue
$ python features.py put somekey somevalue -t 5
```
Note that the '=' signs are optional.

### Underscores

Underscores ('_') in parameter names can be automatically converted to dashes
('-'). When enabled, both form of the argument are allowed. For example, both
of the following are correct:
```bash
$ python features.py version --host-name localhost
$ python features.py version --host_name localhost
```

This feature is enabled by default. See the Options section below for details
on how to adjust this behavior.

### Defaults and Types

Keyword argument defaults are respected, and are used to infer types for those
parameters. For non-keyword arguments and keyword arguments where the default
is None, the default type is str. The generated parser automatically casts
and checks types. For example, the following will not validate, and will print
usage help:
```bash
$ python features.py get somekey --timeout=blah
```
In the body of DoGet e.g., the 'timeout' parameter will always be an int.

### Boolean Parameters

Boolean parameters are treated specially. The generated parser converts boolean
keyword parameters into single flags which, when specified on the command-line,
sets the argument to the opposite of the default.

For example, the 'dev' argument of the 'version' command can be set to True by:
```bash
$ python features.py version --dev
```
When a boolean parameter default is True, the generated switch is the parameter
name with "no_" prefixed. For example, to set 'cache' to False for 'get':
```bash
$ python features.py get somekey --no-cache
```

### List Parameters

If a parameter has a default value that is a list, Commandr will accept multiple
values for the parameter, joining them together to form a list.  The type for
the values in the list will be string.

Multiple values can be specified by repeating the switch:
```
my-command --arg value1 --arg value2 --arg value3
```
will lead to:
arg=[value1, value2, value3]

### Documentation Generation

Command help is automatically generated, using the signature and docstring of
decorated functions.

Running a commandr script directly gives a list of available commands, grouped
by the category specified in each decorator.
```bash
$ python features.py
> Command must be specified
>
> General Commands:
>   status
>   version
> Database Commands:
>   get
>   put
```

Documentation for any command can be accessed by running the script with that
command and the -h or --help argument. This includes the function's docstring
(if any), argument names, and default values.
```bash
$ python features.py get -h
> Documentation for command 'get':
> ----------------------------------------
> Get an item from the database
>   Arguments:
>     key - Database key to get.
>     timeout - Seconds to wait.
>     cache - Whether to get from the local cache first.
>
> ----------------------------------------
>
> Usage: features.py command [options]
> Options without default values MUST be specified
>
> Options:
>   -h, --help
>   -k KEY, --key=KEY
>   -t TIMEOUT, --timeout=TIMEOUT
>                         [default: 10]
>   -n, --no-cache
```

If a command is invoked with incomplete arguments, or invalid values, the error
is printed, along with the usage documentation.

```bash
$ python features.py put somekey1 --transaction
> All options without default values must be specified
>
> Current Options:
>  --key=somekey1
>  --value=None
>  --timeout=10
>  --transaction=True
>
> Documentation for command 'put':
> ----------------------------------------
> Put an item in the database.
>   Arguments:
>     key - Database key to put.
>     value - String value to put.
>     timeout - Seconds to wait.
>     transaction - Whether to perform the put in a transaction
>
> ----------------------------------------
>
> Usage: features.py command [options]
> Options without default values MUST be specified
>
> Options:
>   -h, --help
>   -k KEY, --key=KEY
>   -v VALUE, --value=VALUE
>   -t TIMEOUT, --timeout=TIMEOUT
>                         [default: 10]
>   --transaction
```

To print the usage message after the command is called, call
commandr.Usage(message).  This will print the command usage and exit.

### Value Transformation

The value of an argument can be transformed before the command is called using
the transform option on command() and global Options. To transform a value
pass a dict with the argument name as a the key and a callable that accepts
key and value as arguments and returns the new value of the argument.  If the
value is None, transformation is not called.  Transformation will be called
before Value Validation.

An example:
```
def ConvertToDict(key, value):
  """Converts str of format 'a=b;c=d;e=f' to a dict."""
  if not isinstance(value, dict):
    return dict(kv.split('=', 1) for kv in value.split(';'))
  else:
    # if value is not returned here, the new value will be None
    return value

@command(tranform={'extra':ConvertToDict},
         validate={'extra':lambda k,v: 'msg' in extra})
def MyFunction(name, extra={'msg':'Hi'}):
```

### Value Validation

To validate the values passed as part of the argument parsing, pass a dict
object to the command() function with key/value pairs where the value is
either a list containing the passed value or a callable that accepts the
argument name and argument value and returns True if the argument passes
or False if it does not.  If the value is None, validation is not called.

An example:
```
def IsCapitalized(key, name):
  return name == str(name).capitalize()

@command(validate={'title':['Mr', 'Mrs', 'Sir', 'Madam'],
                   'first_name':IsCapitalized,
                   'last_name':IsCapitalized})
def MyFunction(title, first_name, last_name):
  ...
```

It is also possible to declare a validation dict as a global option.  If it is
set globally, any command that is run by Commandr will use the global
validation if one of its arguments is in that dictionary.  However, A local
validate for a @command will override the global validation.  See Options
section for details on how to set Options.

### Options

There are several options that can be set to modify the behavior of the parser
generation. These options can be set by calling the SetOptions() function, or
as parameters to the Run() function. Values set by Run() take precedence.

The available parameters are:

##### ignore_self:
If True, arguments named "self" will be ignored when building the parser
for functions. This is useful when using member functions as commands.
Default is False.

##### main_docs:
If True, __main__.__doc__ and __main__.__copyright__ will be printed if
the command is run with no arguments or help.  Default is True.

##### main:
If set, Commandr will use the supplied value as the command name to run
if no command name is supplied.  It will override any previous values.

##### validate:
If set, Commandr will use the provided dict to set global Validation for any
command that has an argument with a key in the dict.  If a global validate
dict is set a second time, it will override all values in the original dict.
If a command() passes a validate dict, it will only override values present
in the local dict.   See the Validation section for details off the argument.

##### transform:
Sets the Global options for transformation (see Value Transformation).
If set multiple times, the all values will be overridden by the last global
option.  command(transform=..) options will override global options only for
the values set in the local options.

##### hyphenate:
If True (default), then any argument containing an underscore ('_') will be
parsable with dashes ('-') in their place (both variants will be allowed).
If False, then only the original argument name will be accepted.

Note that if hyphenate is enabled, partial arguments will result in a
conflict error. For example, if --caps is supplied for --caps-lock and
--caps_lock, a conflict error will occur.

#####show_all_help_variants:
If False (default), then only one argument name variant will be displayed
in the help text (all forms will remain accepted as arguments).
Specifically, when hyphenate is True, only the hyphenated variant will be
displayed in the help text.

* * *

For example, disabling hyphenation:
```python
from commandr import command, Run, SetOptions

...

if __name__ == '__main__':
  SetOptions(hyphenate=False)
  Run()
```

The options main and ignore_self can also be passed to the Command() decorator
as boolean options for the function being decorated.

Multiple Decorators
-------------------

It is possible to use 'stacked' decorators with commandr, with a few caveats.
First, the @command decorator only sees, and therefore can only execute, the
function as passed to it. This usually means that the @command decorator should
be at the top of the stack. Second, any decorator below @command in the stack
which wraps the original function (i.e. returns a function other than the
original being decorated) must attach special meta-data to the wrapper. This
can be accomplished using commandr.wraps, which has the same semantics as
functools.wraps. (There is also commandr.update_wrapper which has the same
semantics as functools.update_wrapper). e.g.:

```python
from commandr import command, Run, wraps

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

Run()
```

Without this additional meta-data, commandr will inspect the wrapper's signature
to build the parser, which is probably not the intended effect.

If working with decorators that use functools.wraps, commandr provides a
mechanism to monkey-patch functools. Calling commandr.MonkeyPatchFunctools()
updates functools.wraps and functools.update_wrapper so that they also attach
the meta-data commandr needs. e.g.:

```python
from commandr import command, Run, MonkeyPatchFunctools
MonkeyPatchFunctools()

@command('test_decorated')
@some_legacy_wrapping_decorator
def DecoratedFunction(arg1, arg2=1):
  print arg1, arg2

Run()
```

Note that @command itself is not a wrapping decorator -- the original function
is left intact.

Authors
-------
commandr was developed at TellApart by [Kevin Ballard](https://github.com/kevinballard) and [Chris Huegle](https://github.com/chuegle).
