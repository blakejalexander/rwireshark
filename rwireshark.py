#!/usr/bin/env python3


import argparse


def main():

    parser = argparse.ArgumentParser(prog="rwireshark")

    parser.add_argument("host", type=str)
    parser.add_argument("-p", "--port", default=22, type=int)
    parser.add_argument("-i", "--interface", default="eth0")

    args = parser.parse_args()

    user, sep, host = args.host.partition('@')

    if sep == '':
        host, user = user, ''


if __name__ == "__main__":
    main()