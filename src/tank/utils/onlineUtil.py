from socket import socket


def recvAll(socket: socket):
    MAX_LEN = 1024
    data = b""
    while True:
        packet = socket.recv(MAX_LEN)
        data += packet
        if len(packet) < MAX_LEN:
            break
    return data
