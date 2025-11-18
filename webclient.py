#!/usr/bin/env python3
"""
Minimal web client for the lab.

Usage: python webclient.py <host> <port> <path>
Example: python webclient.py 192.168.56.21 6789 /index.html

This client opens a TCP connection, sends a simple HTTP GET, prints the response,
and saves the raw response to `last_response.txt` for later analysis.
"""
import socket
import sys


def usage():
    print('Usage: python webclient.py <host> <port> <path>')


def run(host, port, path):
    addr = (host, int(port))
    req = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'.format(path, host).encode()
    print('Connecting to {}:{} and requesting {}'.format(host, port, path))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(addr)
        s.sendall(req)
        data = bytearray()
        while True:
            part = s.recv(4096)
            if not part:
                break
            data.extend(part)
    text = data.decode(errors='replace')
    print('--- Response start ---')
    print(text)
    print('--- Response end ---')
    with open('last_response.txt', 'wb') as f:
        f.write(data)
    print('Saved raw response to last_response.txt')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        usage()
        sys.exit(1)
    run(sys.argv[1], sys.argv[2], sys.argv[3])
