# Multinode Lab — Simple Web Server and Client

Files added for the lab:

- `webserver.py`: simple TCP HTTP server listening on port `6789`.
- `webclient.py`: minimal client to request a path and save the response.

Quick steps (on host or within VMs):

1. Start the Vagrant VMs:

```powershell
vagrant up
vagrant ssh webserver
```

2. On the `webserver` VM, run the server (ensure you're in project folder):

```powershell
python3 webserver.py
```

3. From the `client` VM, test with telnet (capture output as screenshot):

```powershell
telnet 192.168.56.21 6789
```

Then type a simple HTTP request, e.g. `GET /index.html HTTP/1.1` and press Enter twice.

4. Or use the Python client from the `client` VM (capture output):

```powershell
python3 webclient.py 192.168.56.21 6789 /index.html
```

5. Packet analysis hints:
- While performing the `telnet` test, capture traffic with `tcpdump` or Wireshark on either VM or the host.
- Look for the TCP three-way handshake (SYN, SYN-ACK, ACK), the GET request as a data segment, server response segments, and the connection close (FIN/ACK).

Deliverables for the lab memo:
- Modified `Vagrantfile` (already includes the `192.168.56.21` private IP).
- `webserver.py` and `webclient.py` (this repo).
- Screenshots of `telnet` and `python webclient.py` runs.
- Packet analysis write-ups describing TCP segments seen during `telnet` and `webclient` runs.
