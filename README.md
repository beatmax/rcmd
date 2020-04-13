# rcmd - remote command execution
Simple Python TCP server and client for remote command execution.

The server (`rcmd-server.py`) listens on a TCP port and receives commands to execute.

The client (`rcmd-exec.py`) forwards its arguments to the server.

Example:
```
$ ./rcmd-exec.py echo "hello world"
hello world
```

TODO: Split stdout and stderr, forward stdin, optionally allocate pseudo-tty.
