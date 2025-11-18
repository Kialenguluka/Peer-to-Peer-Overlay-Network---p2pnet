# Packet capture & analysis — template

Use this template in your lab memo to describe the TCP packets observed during the `telnet` and `webclient` tests.

Test: `telnet 192.168.56.21 6789`

- Capture setup: `sudo tcpdump -i any -w telnet_test.pcap` on the server or client VM.
- Observed sequence:
  - 1) Client -> Server: TCP SYN (client port X -> 6789)
  - 2) Server -> Client: TCP SYN-ACK (6789 -> client port X)
  - 3) Client -> Server: TCP ACK (client port X -> 6789) — handshake complete
  - 4) Client -> Server: TCP PSH, ACK containing `GET /index.html HTTP/1.1` (payload length Y)
  - 5) Server -> Client: TCP PSH, ACK containing HTTP response headers + body (may be in multiple segments)
  - 6) Connection termination: FIN/ACK exchange or RST depending on how client closed connection

Notes for analysis:
- Highlight the three-way handshake packets (SYN, SYN-ACK, ACK) and include timestamps and sequence numbers.
- Show the packet carrying the HTTP GET as a payload-bearing segment; quote the request line.
- Show one or more server response packets and indicate header fields (Content-Length, Connection).
- If using `telnet`, mention that `telnet` sends the request bytes interactively — timing between handshake and request depends on user typing.

Test: `python webclient.py 192.168.56.21 6789 /index.html`

- This automated client will connect and immediately send the GET request.
- Observed differences vs `telnet`:
  - The GET appears immediately after the handshake (shorter time delta).
  - The client closes the connection after receiving the response (Connection: close), usually resulting in FIN packets.

Include sample Wireshark screenshots showing:
- The three-way handshake
- The HTTP GET request packet
- The server response packet(s)
- The connection close (FIN/ACK)

Optional: Use `tshark -r telnet_test.pcap -T fields -e frame.time -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e tcp.flags -e tcp.seq -e tcp.ack -e tcp.len -e data-text-lines` to extract relevant fields for the memo.
