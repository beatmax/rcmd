#!/usr/bin/env python3

import argparse
import os
import socket
import pickle
import signal
import sys


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 10000
HEADERSIZE = 10
BUFSIZE = 1024


def recv_msg(s):
    chunk = s.recv(BUFSIZE)
    msglen = int(chunk[:HEADERSIZE])
    msg = chunk[HEADERSIZE:]
    while len(msg) < msglen:
        msg += s.recv(BUFSIZE)
    return msg


def run_cmd(workdir, cmd, s, close_fds):
    pid = os.fork()
    if pid == 0:
        close_fds()
        if workdir:
            os.chdir(workdir)
        os.close(sys.__stdin__.fileno())
        os.close(sys.__stdout__.fileno())
        os.close(sys.__stderr__.fileno())
        os.dup2(s.fileno(), sys.__stdin__.fileno())
        os.dup2(s.fileno(), sys.__stdout__.fileno())
        os.dup2(s.fileno(), sys.__stderr__.fileno())
        os.execvp(cmd[0], cmd)


def run_server(host, port):
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()

    def close_fds():
        s.close()

    while True:
        clientsocket, address = s.accept()
        try:
            (wd, cmd) = pickle.loads(recv_msg(clientsocket))
            if len(cmd) > 0:
                run_cmd(wd, cmd, clientsocket, close_fds)
        except Exception as e:
            print('{}: {}'.format(address, e), file=sys.stderr)
        finally:
            clientsocket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='command server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-H', '--host', default=DEFAULT_HOST, help="listen host ('*' = any)")
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help='listen port')
    args = parser.parse_args()
    if args.host == '*':
        args.host = ''
    try:
        run_server(args.host, args.port)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
