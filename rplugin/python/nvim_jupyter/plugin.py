import sys
import logging
from collections import Iterable
from operator import methodcaller

import neovim as nv

import jupyter_client as jc

import nvim_jupyter
from nvim_jupyter import utils


@nv.plugin
class NVimJupyter:
    def __init__(self, nvim):
        """Initialize NVimJupyter plugin

        Parameters
        ---------
        nvim: object
            The `neovim` communication channel.
        """
        # TODO: Does this mean we don't need to decode manually?
        self.nvim = nvim.with_decode()
        self.argp = utils.set_argparser(nvim_jupyter.args_to_set)
        self.new_kernel_started = None
        self.buffer = None
        self.window = None
        self.kc = None

    @nv.command('JKernel', nargs='*', sync=True)
    def connect_handler(self, args):
        """ Connect to a new or existing kernel.

        Parameters
        ----------
        args: list of str
            Arguments passed from `neovim`.

        Notes
        -----
        There's a problem: `neovim` passes a `list` of `bytes` instead of
        `str`. Need to manually decode them.
        """
        # allow only one connection
        if self.kc is not None:
            return

        if isinstance(args, str) or not isinstance(args, Iterable):
            args = [args]

        args = map(methodcaller('decode', self.nvim.eval('&encoding')),
                   args)
        args = self.argp.parse_args(['JKernel'] + args)
        try:
            self.kc, self.new_kernel_started = self._connect_to_kernel(args)

            # self.buffer, self.window = self._set_buffer_and_window()

            # consume first iopub message (starting)
            self.kc.get_iopub_msg()
            shell_msg = self.kc.get_shell_msg()

            logging.debug('KERNEL BEFORE SHELL {}', self.new_kernel_started)
            # self._print_to_buffer(
            #     ['Jupyter {implementation_version} /'
            #      ' Python {language_info[version]}'
            #      .format(**shell_msg['content']),
            #      '']
            # )
        except OSError:
            self._error(msg='Could not find connection file. Not connected!',
                        prefix='[JKernel]: ')
            logging.debug('KERNEL EXCEPT')

    @nv.command('JExecute', range='')
    def execute_handler(self, r):
        """`neovim` command for executing code

        It either executes current line or the visual selection.

        Parameters
        ----------
        r: list
            A list of two numbers representing the beginning and finish of the
            `neovim` range object.
        """
        (y0, x0), (y1, x1) = (self.nvim.current.buffer.mark('<'),
                              self.nvim.current.buffer.mark('>'))
        x0, x1 = min(x0, x1), max(x0, x1)
        logging.debug('MARKS {}'.format((x0, x1, y0, y1)))
        # it's enough to verify that the rows are `(0, 0)` because
        # `neovim` valid row numbering starts at 1
        if y0 == y1 == 0:
            (y0, y1), (x0, x1) = r, (0, sys.maxsize)
        else:
            # for the time being deleting the marks will have to do (but only
            # in case there is an initial selection)
            self.nvim.command('delmarks <>')
        x1, y0 = x1 + 1, y0 - 1
        code = '\n'.join(line[x0:x1].strip()
                         if y1 - y0 == 1 else
                         line[x0:x1].rstrip()
                         for line in self.nvim.current.buffer[y0:y1])

        msg_id = self.kc.execute(code)
        msg = self._get_iopub_msg(msg_id)
        # self._print_to_buffer(msg)

    @nv.shutdown_hook
    def shutdown(self):
        """Don't know what this hook does...
        """
        logging.debug('shutdown hook')
        if self.new_kernel_started is True:
            self.kc.shutdown()

    def _set_buffer_and_window(self):
        """Create new scratch buffer in neovim for feedback from kernel

        Returns
        -------
        buffer: `neovim` buffer
            The newly created buffer object.
        window: `neovim` window
            The window associated with `buffer`.
        """
        self.nvim.command('{height}new'.format(
            height=int(self.nvim.current.window.height * 0.3))
        )
        # TODO: these will need to be changed based on the response from
        #       the kernel
        self.nvim.current.buffer.name = '[IPython]'
        self.nvim.current.buffer.options['buftype'] = 'nofile'
        self.nvim.current.buffer.options['bufhidden'] = 'hide'
        self.nvim.current.buffer.options['swapfile'] = False
        self.nvim.current.buffer.options['readonly'] = True
        self.nvim.current.buffer.options['filetype'] = 'python'
        self.nvim.current.buffer.options['syntax'] = 'python'
        self.nvim.command('syntax enable')
        buffer = self.nvim.current.buffer
        window = self.nvim.current.window
        self.nvim.command('wincmd j')
        return buffer, window

    def _connect_to_kernel(self, args):
        """Start new or connect to existing `Jupyter` kernel

        Parameters
        ----------
        args: argparse.ArgumentParser parsed arguments
            Arguments given to `JKernel` command through `neovim`.

        Returns
        -------
        kc: jupyter_client.KernelClient
            The kernel client in charge of negotiating communication between
            `neovim` and the `Jupyter` kernel.
        new_kernel_started: bool
            Flag to keep track of new / existing kernel.
        """
        logging.debug('ARGS {}'.format(args))
        if args.existing is not None:
            connection_file = jc.find_connection_file(filename=args.existing)
            logging.debug('CONNECT {}, {}'.format(connection_file, args.existing))
            km = jc.KernelManager(connection_file=connection_file)
            km.load_connection_file()
            new_kernel_started = False
        else:
            km = jc.KernelManager()
            km.start_kernel()
            new_kernel_started = True
        kc = km.client()
        kc.start_channels()
        return kc, new_kernel_started

    def _get_iopub_msg(self, msg_id):
        '''Get the iopub socket message after execution
        '''
        msg = {}
        while True:
            iopub_msg = self.kc.get_iopub_msg()
            logging.debug('IOPUB {}'.format(iopub_msg))
            if (
                iopub_msg['parent_header']['msg_id'] == msg_id and
                iopub_msg['msg_type'] in nvim_jupyter.msg_types
            ):
                for key in iopub_msg['content']:
                    msg[key] = iopub_msg['content'][key]
                    if isinstance(msg[key], list):
                        msg[key] = '\n'.join(msg[key])
            if (
                iopub_msg['parent_header']['msg_type'] != 'kernel_info_request' and
                iopub_msg['msg_type'] == 'status' and
                iopub_msg['content']['execution_state'] == 'idle'
            ):
                break
        return msg

    def _print_to_buffer(self, msg):
        self.buffer.options['readonly'] = False
        if isinstance(msg, (str, list)):
            self.buffer.append(msg)
        else:
            self.buffer[len(self.buffer)] = None
            msg = utils.format_msg(msg)
            for key in nvim_jupyter.messages:
                try:
                    self.buffer.append(msg[key])
                except KeyError:
                    pass
        self.buffer.append('In [ ]')
        self.buffer.options['readonly'] = True
        self.window.cursor = len(self.buffer), 0

    def _echo(self, msg, prefix='', hl='NormalMsg'):
        self.nvim.command('echohl {hl} | echom "{prefix}{msg}" |'
                          ' echohl NormalMsg'
                          .format(msg=msg, prefix=prefix, hl=hl))

    def _warning(self, msg, prefix=''):
        self._echo(msg, prefix=prefix, hl='WarningMsg')

    def _error(self, msg, prefix=''):
        self._echo(msg, prefix=prefix, hl='ErrorMsg')
