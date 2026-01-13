#!/usr/bin/env python3
"""
Multicast IPTV Sender (TV Server)
Sends video stream to multicast group 239.1.1.1
"""

import socket
import struct
import time
import sys

MCAST_GRP = '239.1.1.1'
MCAST_PORT = 5007
MULTICAST_TTL = 32

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    
    print(f"📺 TV Server starting...")
    print(f"   Multicast Group: {MCAST_GRP}")
    print(f"   Port: {MCAST_PORT}")
    print(f"   TTL: {MULTICAST_TTL}")
    print(f"   Press Ctrl+C to stop")
    print("")
    
    frame_number = 0
    try:
        while True:
            message = f"IPTV Frame #{frame_number} - Timestamp: {time.time():.2f}".encode('utf-8')
            sock.sendto(message, (MCAST_GRP, MCAST_PORT))
            
            if frame_number % 10 == 0:
                print(f"✓ Sent frame {frame_number}")
            
            frame_number += 1
            time.sleep(0.1)  # 10 frames per second
            
    except KeyboardInterrupt:
        print("\n📺 TV Server stopped")
        sock.close()

if __name__ == '__main__':
    main()
