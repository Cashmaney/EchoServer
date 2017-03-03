import struct

const_sync_bytes = 1437226410

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    if msg is None:
        raise TypeError('msg is none')
    sync_bytes = bytearray(b'\x55\xAA\x55\xAA')
    msg = sync_bytes + struct.pack('>I', len(msg)) + msg
    #msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 8)
    if not raw_msglen:
        return None
    sync_bytes, msglen = struct.unpack('>II', raw_msglen)

    if sync_bytes != const_sync_bytes:
        print(sync_bytes)
        return None

    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, msglen):
    # Helper function to recv n bytes or return None if EOF is hit
    data = ''
    while len(data) < msglen:
        packet = sock.recv(msglen - len(data))
        if not packet:
            return None
        data += packet
    return data