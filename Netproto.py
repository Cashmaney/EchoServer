import struct

const_sync_bytes = 1437226410


def send_msg(sock, msg, udp=False, addr=None):
    if msg is None:
        raise TypeError('msg is none')

    # Prefix each message with a 4-byte length (network byte order)
    sync_bytes = bytearray(b'\x55\xAA\x55\xAA')
    # And 4 bytes of the length of the data
    msg = sync_bytes + struct.pack('>I', len(msg)) + msg

    if udp:
        sock.sendto(msg, addr)
    else:
        sock.sendall(msg)


def recv_msg(sock, udp=False):

    if not udp:
        # Read message length and unpack it into an integer
        raw_msglen = recvall(sock, 8)
        if not raw_msglen:
            return None
        sync_bytes, msglen = struct.unpack('>II', raw_msglen)

        # Sync bytes sanity check
        if sync_bytes != const_sync_bytes:
            print(sync_bytes)
            return None

        # Read the rest of the message data now that we know how long to expect
        return recvall(sock, msglen)
    else:
        # UDP doesn't allow us to call recv multiple times per packet, so just receive it all
        raw_msg, caddr = sock.recvfrom(65507)
        sync_bytes = raw_msg[:4]
        # if int(sync_bytes) != const_sync_bytes:
        # print(sync_bytes)
        # return None
        # Extract the expected length - we might need additional packets
        msglen = raw_msg[4:8]
        raw_msg = raw_msg[8:len(raw_msg)]

        # Receive the rest of the data if needed
        while msglen < len(raw_msg):
            packet = sock.recv(65507)
            if not packet:
                return None
            raw_msg += packet

        return raw_msg, caddr


# Helper function to recv n bytes or return None if EOF is hit
def recvall(sock, msglen):
    data = ''
    while len(data) < msglen:
        packet = sock.recv(msglen - len(data))
        if not packet:
            return None
        data += packet
    return data