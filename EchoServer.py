import multiprocessing
import socket

# custom packages
import Netproto


def handle(connection, address):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            data = Netproto.recv_msg(connection)
            if data == "":
                logger.debug("Socket closed remotely")
                break
            logger.debug("Received data %r", data)
            logger.debug("Echoing data to client")
            Netproto.send_msg(connection, data)
            logger.debug("Sent data")
            logger.info("Done sending data - %d bytes", len(data))
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

    def start(self):
        self.logger.debug("Listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        while True:
            conn, address = self.socket.accept()
            self.logger.debug("Got connection")
            server_proc = multiprocessing.Process(target=handle, args=(conn, address))
            server_proc.daemon = True
            server_proc.start()
            self.logger.debug("Started process %r", server_proc)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    server = Server("0.0.0.0", 9000)

    try:
        logging.info("Listening")
        server.start()
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")