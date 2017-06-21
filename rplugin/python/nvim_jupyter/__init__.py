"""
Flexible [neovim] - [Jupyter] kernel interaction. Augments [neovim] with the
following functionality:

- `(c) JKernel [-e/--existing [filehint]]` - **first connect to kernel**

  connect to new or existing kernel (using the `[-e/--existing [filehint]]`)
  argument, where `[filehint]` is either the `*` (star) in `kernel-*.json`
  or the absolute path of the connection file. If `JKernel` is used without any
  arguments then it starts a new kernel. If `-e/--existing` is provided
  (without the optional [filehint]) then an attempt to connect to an existing
  kernel is made. If kernel is not found then it doesn't create a new kernel.
  If [filehint] is given and not found, again, it doesn't create a kernel.

- `(c) [range]JExecute`

  send current line to be executed by the kernel or if `[range]` is given
  execute the appropriate lines. This also works with visual selections
  (including block selections). Example:
  ```
  bla bla bla print('test') more bla
  some bla    test = 5; test
  ```
  it is possible here (for whatever reason) to select the text made out of
  `print('test')` and `test = 5; test` and it will execute as if it were
  two lines of code (think of `IPython`). This works because the selection
  doesn't have any leading whitespace. In the more usual case, `print('test')`
  and `test = 5; test` can be selected one at a time and the execution proceeds
  as expected. _This upgrade of `JExecute` doesn't add new functions or
  commands to [neovim] so it is quite natural to use_

Legend `(c)` = command

[neovim]: http://neovim.io/
[Jupyter]: https://jupyter.org/
"""
import os
import sys
import logging.config

from collections import OrderedDict
import re

from .plugin import NVimJupyter

__all__ = ['plugin']

args_to_set = {
    'JKernel': {('-e', '--existing'): {'nargs': '?',
                                       'const': 'kernel-*.json'}}
}

messages = OrderedDict(
    [('in', 'In [{execution_count}]: {code}'),
     ('out', 'Out[{execution_count}]: {data[text/plain]}'),
     ('stdout', '{text}'),
     ('err', '{traceback}')]
)

msg_types = ['error', 'execute_input', 'execute_result', 'stream']

color_regex = re.compile(r'\x1b\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|k]',
                         re.IGNORECASE)

logger_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'local': {
            'format': '%(asctime)s %(message)s',
        }
    },
    'handlers': {
        'file': {'class': 'logging.FileHandler',
                 'formatter': 'local',
                 'level': 'DEBUG',
                 'filename': os.path.join(
                     os.path.dirname(sys.modules[__name__].__file__),
                     'nvim_jupyter.log')
                 }
    },
    'loggers': {'': {'handlers': ['file'],
                     'level': 'DEBUG'}},
}

logging.config.dictConfig(logger_config)
