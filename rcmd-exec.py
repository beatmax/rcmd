#!/usr/bin/env python3

import os
import pickle
import socket
import sys

PORT = 10000
HEADERSIZE = 10
BUFSIZE = 1024


def remote_exec(workdir, cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", PORT))

    msg = pickle.dumps((workdir, cmd))
    msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8')+msg
    s.sendall(msg)
    while True:
        chunk = s.recv(BUFSIZE)
        if len(chunk) == 0:
            break
        sys.stdout.buffer.write(chunk)
        sys.stdout.buffer.flush()


if __name__ == "__main__":
    # TODO args: --host (default localhost) --port (default 10000)
    #            -w,--workdir (default current)
    remote_exec(os.getcwd(), sys.argv[1:]);
