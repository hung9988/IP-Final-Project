#!/usr/bin/env python3
"""
Multi-AS Network Topology with Mininet and FRR

Topology:
- Tier 1 (AS 100): R4, R5, R6 - OSPF
- ISP #1 (AS 200): R1, R2, R3 - RIP
- ISP #2 (AS 300): R7, R8, R9 - OSPF

BGP Connections:
- R2 (ISP#1) <-> R4 (Tier1)
- R6 (Tier1) <-> R7 (ISP#2)
- R2 (ISP#1) <-> R7 (ISP#2) - Peering

Hosts:
- PC1 connected to R1
- PC2 connected to R3
- PC3 connected to R8
- PC4 connected to R9
"""

from mininet.topo import Topo
from mininet.node import Node


class LinuxRouter(Node):
    """A Node with IP forwarding enabled."""

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    """
    Multi-AS Network Topology
    
    IP Addressing Scheme:
    - 10.0.X.0/24 for point-to-point links
    - 192.168.X.0/24 for host networks
    
    Link numbering:
    - 10.0.1.0/24: R1-R2
    - 10.0.2.0/24: R2-R3
    - 10.0.3.0/24: R2-R4 (BGP: ISP#1 to Tier1)
    - 10.0.4.0/24: R4-R5
    - 10.0.5.0/24: R5-R6
    - 10.0.6.0/24: R6-R7 (BGP: Tier1 to ISP#2)
    - 10.0.7.0/24: R7-R8
    - 10.0.8.0/24: R7-R9
    - 10.0.9.0/24: R2-R7 (Peering: ISP#1 to ISP#2)
    
    Host networks:
    - 192.168.1.0/24: PC1 on R1
    - 192.168.2.0/24: PC2 on R3
    - 192.168.3.0/24: PC3 on R8
    - 192.168.4.0/24: PC4 on R9
    """

    def build(self):
        # Create routers
        # ISP #1 (AS 200) - RIP
        r1 = self.addNode('r1', cls=LinuxRouter, ip=None)
        r2 = self.addNode('r2', cls=LinuxRouter, ip=None)
        r3 = self.addNode('r3', cls=LinuxRouter, ip=None)
        
        # Tier 1 (AS 100) - OSPF
        r4 = self.addNode('r4', cls=LinuxRouter, ip=None)
        r5 = self.addNode('r5', cls=LinuxRouter, ip=None)
        r6 = self.addNode('r6', cls=LinuxRouter, ip=None)
        
        # ISP #2 (AS 300) - OSPF
        r7 = self.addNode('r7', cls=LinuxRouter, ip=None)
        r8 = self.addNode('r8', cls=LinuxRouter, ip=None)
        r9 = self.addNode('r9', cls=LinuxRouter, ip=None)

        # Create hosts
        pc1 = self.addHost('pc1', ip='192.168.1.2/24', defaultRoute='via 192.168.1.1')
        pc2 = self.addHost('pc2', ip='192.168.2.2/24', defaultRoute='via 192.168.2.1')
        pc3 = self.addHost('pc3', ip='192.168.3.2/24', defaultRoute='via 192.168.3.1')
        pc4 = self.addHost('pc4', ip='192.168.4.2/24', defaultRoute='via 192.168.4.1')
        
        # TV Server for multicast IPTV service (connected to R5 in Tier 1)
        tv_server = self.addHost('tv_server', ip='10.100.5.10/24', defaultRoute='via 10.100.5.1')

        # ISP #1 internal links (RIP)
        # R1 - R2: 10.0.1.0/24
        self.addLink(r1, r2,
                     intfName1='r1-eth0', params1={'ip': '10.0.1.1/24'},
                     intfName2='r2-eth0', params2={'ip': '10.0.1.2/24'})
        
        # R2 - R3: 10.0.2.0/24
        self.addLink(r2, r3,
                     intfName1='r2-eth1', params1={'ip': '10.0.2.1/24'},
                     intfName2='r3-eth0', params2={'ip': '10.0.2.2/24'})

        # Tier 1 internal links (OSPF)
        # R4 - R5: 10.0.4.0/24
        self.addLink(r4, r5,
                     intfName1='r4-eth0', params1={'ip': '10.0.4.1/24'},
                     intfName2='r5-eth0', params2={'ip': '10.0.4.2/24'})
        
        # R5 - R6: 10.0.5.0/24
        self.addLink(r5, r6,
                     intfName1='r5-eth1', params1={'ip': '10.0.5.1/24'},
                     intfName2='r6-eth0', params2={'ip': '10.0.5.2/24'})

        # ISP #2 internal links (OSPF)
        # R7 - R8: 10.0.7.0/24
        self.addLink(r7, r8,
                     intfName1='r7-eth0', params1={'ip': '10.0.7.1/24'},
                     intfName2='r8-eth0', params2={'ip': '10.0.7.2/24'})
        
        # R7 - R9: 10.0.8.0/24
        self.addLink(r7, r9,
                     intfName1='r7-eth1', params1={'ip': '10.0.8.1/24'},
                     intfName2='r9-eth0', params2={'ip': '10.0.8.2/24'})

        # BGP links
        # R2 - R4 (ISP#1 to Tier1): 10.0.3.0/24
        self.addLink(r2, r4,
                     intfName1='r2-eth2', params1={'ip': '10.0.3.1/24'},
                     intfName2='r4-eth1', params2={'ip': '10.0.3.2/24'})
        
        # R6 - R7 (Tier1 to ISP#2): 10.0.6.0/24
        self.addLink(r6, r7,
                     intfName1='r6-eth1', params1={'ip': '10.0.6.1/24'},
                     intfName2='r7-eth2', params2={'ip': '10.0.6.2/24'})

        # Peering link
        # R2 - R7 (ISP#1 to ISP#2 peering): 10.0.9.0/24
        self.addLink(r2, r7,
                     intfName1='r2-eth3', params1={'ip': '10.0.9.1/24'},
                     intfName2='r7-eth3', params2={'ip': '10.0.9.2/24'})

        # Host links
        # PC1 - R1: 192.168.1.0/24
        self.addLink(pc1, r1,
                     intfName2='r1-eth1', params2={'ip': '192.168.1.1/24'})
        
        # PC2 - R3: 192.168.2.0/24
        self.addLink(pc2, r3,
                     intfName2='r3-eth1', params2={'ip': '192.168.2.1/24'})
        
        # PC3 - R8: 192.168.3.0/24
        self.addLink(pc3, r8,
                     intfName2='r8-eth1', params2={'ip': '192.168.3.1/24'})
        
        # PC4 - R9: 192.168.4.0/24
        self.addLink(pc4, r9,
                     intfName2='r9-eth1', params2={'ip': '192.168.4.1/24'})
        
        # TV Server - R5: 10.100.5.0/24 (for multicast IPTV)
        self.addLink(tv_server, r5,
                     intfName2='r5-eth2', params2={'ip': '10.100.5.1/24'})
