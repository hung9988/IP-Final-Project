#!/bin/bash
# Setup FRR configuration directories for each router

ROUTERS="r1 r2 r3 r4 r5 r6 r7 r8 r9"

for NODE in $ROUTERS
do
    echo "Setting up FRR for $NODE..."
    
    # Create log directory
    sudo install -m 775 -o frr -g frr -d /var/log/frr/${NODE}
    
    # Create config directory
    sudo install -m 775 -o frr -g frrvty -d /etc/frr/${NODE}
    
    # Clean existing configs
    sudo rm -f /etc/frr/${NODE}/*
    
    # Install configuration files
    sudo install -m 640 -o frr -g frrvty ${NODE}/vtysh.conf \
        /etc/frr/${NODE}/vtysh.conf
    sudo install -m 640 -o frr -g frr ${NODE}/frr.conf \
        /etc/frr/${NODE}/frr.conf
    sudo install -m 640 -o frr -g frr ${NODE}/daemons \
        /etc/frr/${NODE}/daemons
    
    echo "Done with $NODE"
done

echo ""
echo "FRR setup complete for all routers!"
echo "You can now run: sudo python3 run.py"
