#!/usr/bin/env python3

import os
import socket
import pickle
import signal
import sys


PORT = 10000
HEADERSIZE = 10
BUFSIZE = 1024


def recv_msg(s):
    # TODO handle disconnection
    chunk = s.recv(BUFSIZE)
    msglen = int(chunk[:HEADERSIZE])
    msg = chunk[HEADERSIZE:]
    while len(msg) < msglen:
        msg += s.recv(BUFSIZE)
    return msg


def run_cmd(workdir, cmd, s):
    pid = os.fork()
    if pid == 0:
        os.chdir(workdir)
        os.close(sys.__stdin__.fileno())
        os.close(sys.__stdout__.fileno())
        os.close(sys.__stderr__.fileno())
        os.dup2(s.fileno(), sys.__stdin__.fileno())
        os.dup2(s.fileno(), sys.__stdout__.fileno())
        os.dup2(s.fileno(), sys.__stderr__.fileno())
        os.execvp(cmd[0], cmd)


def run_server():
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', PORT))
    s.listen()

    while True:
        clientsocket, address = s.accept()
        (wd, cmd) = pickle.loads(recv_msg(clientsocket))
        if len(cmd) > 0:
            run_cmd(wd, cmd, clientsocket)
        clientsocket.close()


if __name__ == "__main__":
    # TODO args: --port (default 10000)
    try:
        run_server()
    except KeyboardInterrupt:
        pass
