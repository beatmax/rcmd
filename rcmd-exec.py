#!/usr/bin/env python3

import argparse
import os
import pickle
import socket
import sys

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 10000
HEADERSIZE = 10
BUFSIZE = 1024


def remote_exec(host, port, workdir, cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    msg = pickle.dumps((workdir, cmd))
    msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8') + msg
    s.sendall(msg)
    while True:
        chunk = s.recv(BUFSIZE)
        if len(chunk) == 0:
            break
        sys.stdout.buffer.write(chunk)
        sys.stdout.buffer.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='execute command on remote command server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-H', '--host', default=DEFAULT_HOST, help='remote host')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help='remote port')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-w', '--workdir', metavar='WD', help='working directory')
    group.add_argument('-l', '--localdir', action='store_true', help='use local current directory')
    parser.add_argument('cmd')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.localdir:
        args.workdir = os.getcwd()
    try:
        remote_exec(args.host, args.port, args.workdir, [args.cmd] + args.args);
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
