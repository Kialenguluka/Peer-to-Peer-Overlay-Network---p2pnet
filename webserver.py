#!/usr/bin/env python3
"""
Simple single-threaded TCP web server for the lab.

Listens on 0.0.0.0:6789 and serves `html/index.html` or `index.html`.
Logs basic TCP events to stdout to help with packet analysis.
"""
import socket
import os

HOST = '0.0.0.0'
PORT = 6789


def load_index():
    paths = [os.path.join('html', 'index.html'), 'index.html']
    for p in paths:
        if os.path.exists(p):
            with open(p, 'rb') as f:
                return f.read()
    return b"<html><body><h1>It works</h1></body></html>"


def handle_connection(conn, addr, index_bytes):
    print('Connection from {}:{}'.format(addr[0], addr[1]))
    try:
        data = conn.recv(4096)
        if not data:
            print('  (no data received)')
            return
        print('  Received {} bytes'.format(len(data)))
        try:
            first_line = data.splitlines()[0].decode(errors='replace')
            print('  Request line: {}'.format(first_line))
            parts = first_line.split()
            if len(parts) >= 2:
                path = parts[1]
            else:
                path = '/'
        except Exception:
            path = '/'

        if path == '/' or path == '/index.html':
            body = index_bytes
            headers = (
                'HTTP/1.1 200 OK\r\n'
                'Content-Type: text/html; charset=utf-8\r\n'
                'Content-Length: {}\r\n'
                'Connection: close\r\n\r\n'
            ).format(len(body)).encode()
            conn.sendall(headers + body)
            print('  Sent {} bytes (200 OK)'.format(len(headers) + len(body)))
        else:
            body = b'<html><body><h1>404 Not Found</h1></body></html>'
            headers = (
                'HTTP/1.1 404 Not Found\r\n'
                'Content-Type: text/html; charset=utf-8\r\n'
                'Content-Length: {}\r\n'
                'Connection: close\r\n\r\n'
            ).format(len(body)).encode()
            conn.sendall(headers + body)
            print('  Sent {} bytes (404)'.format(len(headers) + len(body)))
    finally:
        conn.close()
        print('  Connection closed')


def run():
    index_bytes = load_index()
    print('Serving {} bytes on {}:{}'.format(len(index_bytes), HOST, PORT))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        try:
            while True:
                conn, addr = s.accept()
                handle_connection(conn, addr, index_bytes)
        except KeyboardInterrupt:
            print('\nServer stopped')


if __name__ == '__main__':
    run()
