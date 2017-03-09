#! /usr/bin/env python2

import socket

import BinObjects
import Netproto


# can throw exceptions, but honestly we don't care, and would rather avoid the try/catch overhead
def net_handle(recv_sock, send_sock, data, udp=False, addr=None):

    Netproto.send_msg(send_sock, data, udp, addr)
    result = Netproto.recv_msg(recv_sock, udp)

    if result == "":
        return None
    return result


def handle_args():
    import argparse
    parser = argparse.ArgumentParser(description='Simple echoing server. Used to either resend a message, '
                                                 'or send your own')
    parser.add_argument('-u', '--udp', action="store_true"
                        ,help="Use UDP sockets")
    parser.add_argument('-p', '--port',
                        type=int, default=9000
                        ,help="Remote port to connect to")
    parser.add_argument('-d', '--debug', action="store_true"
                        ,help="Set logging level to debug")
    parser.add_argument('-r', '--remote',
                        type=str, default='127.0.0.1'
                        , help="Remote IP address to connect to")
    parser.add_argument('-i','--input',
                        type=str, default="Files/"
                        , help="Path to input files -- files that should be sent by this endpoint")
    parser.add_argument('-o', '--output',
                        type=str, default=None
                        , help="Path to output files -- these are the expected answers from the remote endpoint")

    args = parser.parse_args()

    # todo: replace this with something that actually works
    try:
        socket.inet_aton(args.remote)
    except socket.error:
        raise TypeError('Argument is not valid IPv4 address',args.remote)

    if args.port > 65535 or args.port < 0:
        raise TypeError('Argument isn\'t a valid port number',args.port)

    return args


def main():
    import logging
    import time
    import sys

    try:
        args = handle_args()
    except TypeError as e:
        e_msg, e_val = e.args
        print(e_msg + '-' + e_val)
        sys.exit()

    target = args.remote
    port = args.port

    if args.debug is True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.debug("Creating socket")

    files = BinObjects.BinaryList(args.input)
    if args.output is not None:
        out_binobj = BinObjects.BinaryList(args.output)
    else:
        out_binobj = None
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not args.udp:
        try:
            sock.connect((target, port))
        except socket.error as e:
            e_num, e_msg = e.args
            print("Socket connect error - " + e_msg)
            sys.exit()
        logging.debug("Connecting to %s - %r", target, port)
        send_sock = sock
        recv_sock = sock
    else:
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            recv_sock.bind(('0.0.0.0', port))
        except socket.error as e:
            e_num, e_msg = e.args
            print("Socket connect error - " + e_msg)
            sys.exit()

        logging.debug("Binding localhost - %r", port)


    t2 = 0
    for binfile in files.list:
        logging.info("Starting to send file: %s", binfile.path)
        t0 = time.clock()
        net_handle(recv_sock, send_sock, binfile.data, args.udp, (target, port))
        t1 = time.clock()

        ns = (t1 - t0) * 1000
        bytes = len(binfile.data)

        logging.info(" File: %s (%d bytes) took %.2f [ns] \n\t\t   This equates to a bitrate of %d Mb/s", binfile.path, bytes, ns, bytes * 1024**2 * 8/ (ns / 10**-9))

    if not args.udp:
        sock.close()


if __name__ == "__main__":
    main()
