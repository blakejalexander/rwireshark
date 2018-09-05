#!/usr/bin/env python3


import argparse
import subprocess
import shlex
import os


def spawn_tcpdump_ssh(user, host, port, interface):

    if user is None or user == '':
        ssh_cmd = "ssh %s" % host
    else:
        ssh_cmd = "ssh %s@%s" % (user, host)

    # If a non-default ssh port has been given, specify it on the command line
    if port != 22:
        ssh_cmd = "%s -p %d" % (ssh_cmd, port)

    if interface is not None and interface != '':
        interface_opt = '--interface=%s' % interface
    else:
        interface_opt = ''

    # Filter ssh traffic at the capture level to avoid accidentally
    # amplification-attacking ourselves
    tcpdump_cmd = "tcpdump -s0 --packet-buffered -w - " \
        "'not tcp port %d' %s" % (port, interface_opt)

    cmd = "%s %s" % (ssh_cmd, tcpdump_cmd)

    return subprocess.Popen(shlex.split(cmd),
        stdin=None, stdout=subprocess.PIPE, stderr=None)


def spawn_wireshark(stdin=None, stdout=None, stderr=None):

    wireshark_cmd = "wireshark -k -i -"

    return subprocess.Popen(shlex.split(wireshark_cmd), stdin=stdin,
        stdout=stdout, stderr=stderr)


def main():

    parser = argparse.ArgumentParser(prog="rwireshark")

    parser.add_argument("host", type=str)
    parser.add_argument("-p", "--port", default=22, type=int)
    parser.add_argument("-i", "--interface", default=None)

    args = parser.parse_args()

    user, sep, host = args.host.partition('@')

    if sep == '':
        host, user = user, ''

    # spawn an ssh process, connects to target, executes tcpdump and creates
    # a pipe on stdout for usage by this program.
    tcpdump = spawn_tcpdump_ssh(user, host, args.port, args.interface)

    # spawn wireshark process, capturing immediately from stdin, route
    # stdout, stderr to /dev/null to avoid polluting terminal with GUI related
    # errors and messages.
    wireshark = spawn_wireshark(stdin=tcpdump.stdout,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Wait for any child process (tcp or wireshark) to terminate
    # NOTE: different behaviour on Windows, pid<=0 causes an exception
    pid, status = os.waitpid(-1, 0)

    return 0


if __name__ == "__main__":
    main()