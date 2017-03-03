#! /usr/bin/env python2

import socket

# custom packages
import BinObjects
import Netproto


# can throw exceptions, but honestly we don't care, and would rather avoid the try/catch overhead
def net_handle(connection, data):
        Netproto.send_msg(connection, data)
        result = Netproto.recv_msg(connection)
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
    parser.add_argument('-r', '--remote',
                        type=str, default='127.0.0.1'
                        , help="Remote IP address to connect to")
    parser.add_argument('-i','--input',
                        type=str , default="Files/"
                        , help="Path to input files -- files that should be sent by this endpoint")
    parser.add_argument('-o', '--output',
                        type=str, default="Files/"
                        , help="Path to output files -- these are the expected answers from the remote endpoint")
    #parser.add_argument('arg', nargs='*') # use '+' for 1 or more args (instead of 0 or more)
    #parsed = parser.parse_args()
    # NOTE: args with '-' have it replaced with '_'
    #print('Args:',  vars(parsed))

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
        e_msg , e_val = e.args
        print(e_msg + '-' + e_val)
        sys.exit()

    logging.basicConfig(level=logging.INFO)

    logging.debug("Creating socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    files = BinObjects.BinaryList(args.input, args.output)

    #target = "localhost"
    #port = 9000
    target = args.remote
    port = args.port

    logging.debug("Connecting to: %s, %r", target, port)
    try:
        sock.connect((target, port))
    except socket.error as e:
        e_num,e_msg = e.args
        print("Socket connect error - " + e_msg)
        sys.exit()

    t2 = 0
    for binfile in files.list:
        logging.info("Starting to send file: %s", binfile.path)
        t0 = time.clock()
        net_handle(sock, binfile.data)
        t1 = time.clock()

        ns = (t1 - t0) * 1000
        bytes = len(binfile.data)

        logging.info(" File: %s (%d bytes) took %.2f [ns] \n\t\t   This equates to a bitrate of %d Mb/s", binfile.path, bytes, ns, bytes * 1024**2 * 8/ (ns / 10**-9))
    sock.close()


if __name__ == "__main__":
    main()
