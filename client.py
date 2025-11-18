#!/usr/bin/env python3
"""
client.py

Cliente simples usando sockets para enviar um pedido HTTP GET.

Uso (CLI):
  python client.py <host> <port> <path>

Também expõe a função `run(host, port, path)` para testes automáticos.
"""
import socket
import sys


def run(host: str, port: int, path: str) -> bytes:
    addr = (host, int(port))
    req = 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n'.format(path, host).encode()
    print('Connecting to {}:{} and requesting {}'.format(host, port, path))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(addr)
        s.sendall(req)
        resp = bytearray()
        while True:
            part = s.recv(4096)
            if not part:
                break
            resp.extend(part)
    try:
        text = resp.decode('utf-8')
    except Exception:
        text = resp.decode('utf-8', errors='replace')
    print('--- Response start ---')
    print(text)
    print('--- Response end ---')
    with open('last_response.txt', 'wb') as f:
        f.write(resp)
    print('Saved raw response to last_response.txt')
    return bytes(resp)


def usage():
    print('Usage: python client.py <host> <port> <path>')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        usage()
        sys.exit(1)
    run(sys.argv[1], sys.argv[2], sys.argv[3])
