#!/usr/bin/env python3
"""
Multicast IPTV Receiver (PC Client)
Receives video stream from multicast group 239.1.1.1
"""

import socket
import struct
import sys

MCAST_GRP = '239.1.1.1'
MCAST_PORT = 5007

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind to the multicast port
    sock.bind(('', MCAST_PORT))
    
    # Tell the kernel to add us to the multicast group
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    hostname = socket.gethostname()
    print(f"📺 IPTV Receiver starting on {hostname}...")
    print(f"   Multicast Group: {MCAST_GRP}")
    print(f"   Port: {MCAST_PORT}")
    print(f"   Waiting for stream...")
    print(f"   Press Ctrl+C to stop")
    print("")
    
    frame_count = 0
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            frame_count += 1
            
            if frame_count % 10 == 0:
                print(f"✓ Received frame {frame_count}: {data.decode('utf-8')}")
            
    except KeyboardInterrupt:
        print(f"\n📺 IPTV Receiver stopped (received {frame_count} frames)")
        sock.close()

if __name__ == '__main__':
    main()
