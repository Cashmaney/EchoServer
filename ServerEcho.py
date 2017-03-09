#! /usr/bin/env python2

import multiprocessing
import socket

import BinObjects
import Netproto


def net_handle(connection, address, udp, in_binlist=None, out_binlist=None):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("server-%r" % (address,))

    if udp:
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        send_sock = connection

    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            if udp:
                data, client_addr = Netproto.recv_msg(connection, udp)
                client = client_addr[0], address[1]
                logger.info("Got data from %r at %r", client[0], client[1])
            else:
                data = Netproto.recv_msg(connection)
                client = None

            logger.debug("Received data bytes - %r", data)
            if data is None:
                logger.debug("Socket closed remotely")
                break

            if out_binlist is not None and out_binlist.peek().path is not None:
                if out_binlist.peek().data == str(data):
                    logger.info("Success! Received same file than expected for %r", out_binlist.peek().path)
                else:
                    logger.info("Failure! Received different file than expected for %r", out_binlist.peek().path)
                out_binlist.pop()

            if in_binlist is None:
                Netproto.send_msg(send_sock, data, udp, client)
                logger.debug("Echoed message back to client")
            else:
                if len(in_binlist.list) != 0:
                    logger.debug("Found message in input list - sending...")
                    Netproto.send_msg(send_sock, in_binlist.peek().data, udp, client)
                    logger.info("Done sending data - %d bytes", len(in_binlist.pop().data))
                else:
                    logger.debug("No more messages found in input list... Echoing message back to client")
                    Netproto.send_msg(send_sock, data, udp, client)
                    logger.info("Done sending data - %d bytes", len(data))

    except connection:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        if not udp:
            connection.close()


class Server(object):
    def __init__(self, hostname, port):
        import logging
        self.logger = logging.getLogger("ServerObject")
        self.hostname = hostname
        self.port = port

    def start(self, udp=False, binlist=None, out_binlist=None):
        self.logger.debug("Listening")
        if not udp:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.hostname, self.port))
            self.socket.listen(1)
            while True:
                conn, address = self.socket.accept()
                self.logger.debug("Got connection")
                server_proc = multiprocessing.Process(target=net_handle, args=(conn, address, False, binlist, out_binlist))
                server_proc.daemon = True
                server_proc.start()
                self.logger.debug("Started process %r", server_proc)

        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.hostname, self.port))
            net_handle(self.socket, (self.hostname, self.port), True, binlist, out_binlist)


def handle_args():
    import argparse
    parser = argparse.ArgumentParser(description='Simple echoing server. Used to either resend a message, '
                                                 'or send your own')
    parser.add_argument('-u', '--udp', action="store_true"
                        ,help="Use UDP sockets")
    parser.add_argument('-d', '--debug', action="store_true"
                        ,help="Set logging level to debug")
    parser.add_argument('-p', '--port',
                        type=int, default=9000
                        ,help="Local port to listen on")
    parser.add_argument('-i','--input',
                        type=str , default=None
                        , help="Path to input files -- files that should be sent by this endpoint. If not set will echo"
                               " any data received")
    parser.add_argument('-o', '--output',
                        type=str, default=None
                        , help="Path to output files -- these are the expected answers from the remote endpoint. If not"
                               " set will not be checked")

    args = parser.parse_args()

    if args.port > 65535 or args.port < 0:
        raise TypeError('Argument isn\'t a valid port number',args.port)

    return args


def main():

    import logging, sys

    try:
        args = handle_args()
    except TypeError as e:
        e_msg, e_val = e.args
        print(e_msg + '-' + e_val)
        sys.exit()

    args.udp=True

    if args.debug is True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    server = Server("0.0.0.0", args.port)
    if args.input is not None:
        binobj = BinObjects.BinaryList(args.input)
    else:
        binobj = None

    if args.output is not None:
        out_binobj = BinObjects.BinaryList(args.output)
    else:
        out_binobj = None

    try:
        logging.info("Listening")
        server.start(args.udp, binobj, out_binobj)
    except KeyboardInterrupt:
        pass
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")

if __name__ == "__main__":
    main()