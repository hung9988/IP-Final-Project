#!/usr/bin/env python3
"""
Main script to run the Multi-AS Network with Mininet and FRR
"""

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info

from topology import NetworkTopo


def run():
    """Start the network and FRR daemons"""
    topo = NetworkTopo()
    net = Mininet(topo=topo, controller=None)
    
    net.start()
    
    # List of all routers
    routers = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9']
    
    # Start FRR on each router
    info('\n*** Starting FRR on routers ***\n')
    for router in routers:
        info(f'Starting FRR on {router}...\n')
        result = net[router].cmd(f"/usr/lib/frr/frrinit.sh start '{router}'")
        info(f'{router}: {result}\n')
    
    info('\n*** Network is ready ***\n')
    info('*** You can test connectivity with: pc1 ping pc4 ***\n\n')
    
    CLI(net)

    # Stop FRR on each router
    info('\n*** Stopping FRR on routers ***\n')
    for router in routers:
        info(f'Stopping FRR on {router}...\n')
        net[router].cmd(f"/usr/lib/frr/frrinit.sh stop '{router}'")

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
