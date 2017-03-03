#! /usr/bin/env python2

import multiprocessing
import socket

# custom packages
import Netproto
import BinObjects


def net_handle(connection, address, binlist=None):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            data = Netproto.recv_msg(connection)
            if data is None:
                logger.debug("Socket closed remotely")
                break

            logger.debug("Received data %r", data)
            logger.debug("Echoing data to client")
            if binlist is None:
                Netproto.send_msg(connection, data)
            else:
                if len(binlist.list) != 0:
                    Netproto.send_msg(connection, binlist.peek().data)
                    logger.info("Done sending data - %d bytes", len(binlist.pop().data))
                else:
                    Netproto.send_msg(connection, data)
                    logger.info("Done sending data - %d bytes", len(data))
            logger.debug("Sent data")

    except connection:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        connection.close()


class Server(object):
    def __init__(self, hostname, port):
        import logging
        self.logger = logging.getLogger("ServerObject")
        self.hostname = hostname
        self.port = port

    def start(self, binlist=None):
        self.logger.debug("Listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        while True:
            conn, address = self.socket.accept()
            self.logger.debug("Got connection")
            server_proc = multiprocessing.Process(target=net_handle, args=(conn, address, binlist))
            server_proc.daemon = True
            server_proc.start()
            self.logger.debug("Started process %r", server_proc)


def handle_args():
    import argparse
    parser = argparse.ArgumentParser(description='Simple echoing server. Used to either resend a message, '
                                                 'or send your own')
    parser.add_argument('-u', '--udp', action="store_true"
                        ,help="Use UDP sockets")
    parser.add_argument('-p', '--port',
                        type=int, default=9000
                        ,help="Local port to listen on")
    parser.add_argument('-i','--input',
                        type=str , default=None
                        , help="Path to input files -- files that should be sent by this endpoint")
    parser.add_argument('-o', '--output',
                        type=str, default=None
                        , help="Path to output files -- these are the expected answers from the remote endpoint")
    #parser.add_argument('arg', nargs='*') # use '+' for 1 or more args (instead of 0 or more)
    parsed = parser.parse_args()
    # NOTE: args with '-' have it replaced with '_'
    print('Args:',  vars(parsed))

    args = parser.parse_args()
    return args


def main():

    import logging

    args = handle_args()

    logging.basicConfig(level=logging.DEBUG)

    server = Server("0.0.0.0", args.port)
    if args.input is not None and args.output is not None:
        binobj = BinObjects.BinaryList(args.input, args.output, logger)
    else:
        binobj = None

    try:
        logging.info("Listening")
        server.start(binobj)
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