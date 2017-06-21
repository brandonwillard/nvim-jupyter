r"""
For logging, start with

    NVIM_PYTHON_LOG_FILE=logfile NVIM_PYTHON_LOG_LEVEL=DEBUG nvim /tmp/test.py

Send blocks in a vim session by yanking the following and running the Ex command `:@"`
(or open a python term and send it).

    python << EOL
    ...
    EOL

"""

import neovim
import os

import nvim_jupyter

#
# Create an nvim connection so we can script editor testing steps.
#
nvim_address = os.environ['NVIM_LISTEN_ADDRESS']

nvim = neovim.attach('socket', path=nvim_address)

#
# Manually spawn a jupyter-console session in nvim.
#
# nvim.command(':split | term jupyter-console --debug', async=False)
nvim.command(':new')
term_job_id = nvim.funcs.termopen('jupyter-console --debug', async=False)
buf = nvim.current.buffer
buf.options["swapfile"] = False
# term_job_id = buf.api.get_var('terminal_job_id')
con_file_cmd = "print(get_ipython().config['IPKernelApp']['connection_file'])"
nvim.funcs.jobsend(term_job_id, [con_file_cmd, "\n"], async=False)
# Wait a sec to do this.  Need to figure out blocking calls--or callbacks.
connection_file = buf[-3]

#
# Let's mess with nvim plugins...
#
# We would love to simply run `:UpdateRemotePlugin` and have everything
# work, but it doesn't.
# TODO: Check that `rplugin/python[3]` is in the `runtimepath`; otherwise the
# plugin won't be found.
rtp_vals = nvim.funcs.nvim_get_option('runtimepath', async=False)
rtp_vals = ','.join([rtp_vals, os.getcwd().rsplit('/', 2)[0]])

nvim.funcs.nvim_set_option('runtimepath', rtp_vals, async=False)
nvim.command('UpdateRemotePlugins')

# plugin_commands = [{'name': 'JExecute',
#                     'type': 'function',
#                     'opts': {},
#                     'sync': False}]
# # Host should probably be 'python3', but that errs.
# nvim.call('remote#host#RegisterPlugin', 'python',
#           os.path.join(os.getcwd(), 'nvim_jupyter'),
#           plugin_commands)
# nvim.call('remote#host#PluginsForHost', 'python3')

#
# Create our plugin object manually and test.
#
ipy_obj = nvim_jupyter.NVimJupyter(nvim)

# %debug -b nvim_jupyter/plugin.py:47 ipy_obj.connect_handler("-e")
ipy_obj.connect_handler(["-e", connection_file])
print("hi")
ipy_obj.execute_handler([43, 44])

# msg_id = ipy_obj.kc.execute("z = 2\nprint('hi')\n{'bye': 1}")
# msg = ipy_obj._get_iopub_msg(msg_id)


# TODO: The problem is how to get IPython's `[Terminal]InteractiveShell`
# to display remote output *automatically*.  There's a `show_rewritten_input`
# option, but that's not enough.
# A simple hack might involve passing a `pass` after execution of the remote
# command (which we track within the nvim plugin).
# For example:
msg_id = ipy_obj.kc.execute_interactive("z = 2\nprint('hi')\n{'bye': 1}",
                                        output_hook=lambda *a, **k: "")
nvim.call('jobsend', term_job_id, ["pass", "\n"])

# from ipykernel.zmqshell import ZMQInteractiveShell, InteractiveShell

# TODO: We have enough to implement completion.
line = ipy_obj.nvim.current.line
pos = ipy_obj.nvim.funcs.col('.') - 1
cmp_msg = ipy_obj.kc.complete(line, pos, reply=True)
cmp_msg['content']['matches']
crs_start = cmp_msg['content']["cursor_start"] + 1
ipy_obj.nvim.funcs.complete(crs_start, cmp_msg['content']['matches'])

@neovim.function("IPyOmniFunc", sync=True)
def ipy_omnifunc(args):
    pass

# See:
# omnifunc=pythoncomplete#Complete
# or from the `nvim-ipy` plugin:
#
#    @neovim.function("IPyComplete")
#    def ipy_complete(self, args):
#        line = self.vim.current.line
#        # FIXME: (upstream) this sometimes get wrong if
#        # completing just after entering insert mode:
#        #pos = self.vim.current.buffer.mark(".")[1]+1
#        pos = self.vim.funcs.col('.') - 1
#
#        reply = self.waitfor(self.kc.complete(line, pos))
#        content = reply["content"]
#        # TODO: check if position is still valid
#        start = content["cursor_start"] + 1
#        self.vim.funcs.complete(start, content['matches'])
#
#    @neovim.function("IPyOmniFunc", sync=True)
#    def ipy_omnifunc(self, args):
#        findstart, base = args
#        if findstart:
#            if not self.has_connection:
#                return False
#            line = self.vim.current.line
#            pos = self.vim.funcs.col('.') - 1
#
#            reply = self.waitfor(self.kc.complete(line, pos))
#            content = reply["content"]
#            start = content["cursor_start"]
#            self._matches = content['matches']
#            return start
#        else:
#            return self._matches
#
#    @neovim.function("IPyObjInfo")
#    def ipy_objinfo(self, args):
#        word, level = args
#        # TODO: send entire line
#        reply = self.waitfor(self.kc.inspect(word, None, level))
#
#        c = reply['content']
#        if not c['found']:
#            self.append_outbuf("not found: {}\n".format(c['name']))
#            return
#        self.append_outbuf("\n" + c['data']['text/plain'] + "\n")
