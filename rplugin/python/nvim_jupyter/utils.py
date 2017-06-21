import argparse
import logging

import nvim_jupyter as nj


def set_argparser(args_to_set):
    argp = argparse.ArgumentParser(prog='NVimJupyter')
    argps = argp.add_subparsers()
    for command in args_to_set:
        subparser = argps.add_parser(command)
        for arg, opts in args_to_set[command].items():
            subparser.add_argument(*arg, **opts)
    return argp


def format_msg(msg):
    r""" Pretty format the message for output to `neovim` buffer.
    """
    logging.debug('FORMAT {}'.format(msg))
    formatted_msg = dict(msg)
    formatted_msg['code'] = (
        msg['code'][:1] +
        '\n{whitespace}...: '
        .format(whitespace=' ' * (2 + len(str(msg['execution_count']))))
        .join(msg['code'][1:].splitlines())
    )

    for key in nj.messages:
        try:
            formatted_msg[key] = (
                nj.color_regex.sub('',
                                   nj.messages[key].format(**formatted_msg))
                .strip().splitlines()
            )
            if key != 'in':
                formatted_msg[key] += ['']
        except KeyError:
            pass
    logging.debug('FORMATTED {}'.format(formatted_msg))
    return formatted_msg


def decode_args(nvim, args):
    r""" Helper function to decode from `bytes` to `str`.

    FYI: `neovim` has some issues with encoding in Python3.
    """
    encoding = nvim.eval('&encoding')
    return [arg.decode(encoding) if isinstance(arg, bytes) else arg
            for arg in args]
