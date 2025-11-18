#!/usr/bin/env python3
"""
test_runner.py

Inicia `webserver.run()` numa thread e invoca `client.run()` para testar
localmente sem necessidade de Vagrant. Útil para validar rapidamente os
scripts antes de executar nas VMs.
"""
import threading
import time

import webserver
import client


def run_test():
    # Start server in daemon thread
    t = threading.Thread(target=webserver.run, daemon=True)
    t.start()
    # Wait a moment for server to bind
    time.sleep(0.5)
    # Run client against localhost
    try:
        resp = client.run('127.0.0.1', 6789, '/index.html')
        print('Client received {} bytes'.format(len(resp)))
    except Exception as e:
        print('Error running client:', e)


if __name__ == '__main__':
    run_test()
