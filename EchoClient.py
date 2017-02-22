import socket

# custom packages
import BinObjects
import Netproto


def handle(connection, data):
        Netproto.send_msg(connection, data)
        result = Netproto.recv_msg(connection)
        if result == "":
            return None
        return result


if __name__ == "__main__":
    import logging
    import time
    logging.basicConfig(level=logging.INFO)

    logging.debug("Creating socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    files = BinObjects.BinaryList("/home/bob/PycharmProjects/PingPong/Files", "/home/bob/PycharmProjects/PingPong/Files")

    target = "localhost"
    port = 9000

    logging.debug("Connecting to: %s, %r", target, port)

    sock.connect((target, port))
    t2 = 0
    for file in files.list:
        logging.info("Starting to send file: %s", file.path)
        t0 = time.clock()
        handle(sock, file.data)
        t1 = time.clock()

        ns = (t1 - t0) * 1000
        bytes = len(file.data)

        logging.info(" File: %s (%d bytes) took %.2f [ns] \n\t\t   This equates to a bitrate of %d Mb/s", file.path, bytes, ns, bytes * 1024**2 * 8/ (ns / 10**-9))
    sock.close()