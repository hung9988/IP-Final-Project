#!/bin/bash
# run_on_node.sh - Execute commands on Mininet nodes from external terminal

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <node> <command> [args...]"
    echo ""
    echo "Examples:"
    echo "  $0 pc1 ifconfig"
    echo "  $0 tv_server python3 multicast_sender.py"
    echo "  $0 pc2 'python3 multicast_receiver.py &'"
    echo "  $0 r5 'show ip pim neighbor'  # For routers, vtysh is automatic"
    echo ""
    echo "Available nodes:"
    ps aux | grep "mininet:" | grep -v grep | sed 's/.*mininet://g' | awk '{print "  - " $1}' | sort -u
    exit 1
fi

NODE=$1
shift
CMD="$@"

# Check if this is a router node and command looks like a vtysh command
if [[ $NODE =~ ^r[0-9]+$ ]] && [[ ! $CMD =~ ^vtysh ]]; then
    # If command doesn't start with vtysh but looks like a show command, wrap it
    if [[ $CMD =~ ^show ]] || [[ $CMD =~ ^conf ]]; then
        echo "✓ Auto-wrapping with vtysh for router $NODE"
        CMD="vtysh -N $NODE -c \"$CMD\""
    fi
fi

# For router nodes using vtysh, use direct vtysh with -N flag instead of mnexec
if [[ $NODE =~ ^r[0-9]+$ ]] && [[ $CMD =~ ^vtysh ]]; then
    # Extract the vtysh command and add -N flag if not present
    if [[ ! $CMD =~ -N ]]; then
        CMD=$(echo "$CMD" | sed "s/vtysh/vtysh -N $NODE/")
    fi
    echo "✓ Running vtysh command on $NODE: $CMD"
    sudo bash -c "$CMD"
    exit $?
fi

PID=$(ps aux | grep "mininet:$NODE" | grep -v grep | awk '{print $2}' | head -1)

if [ -z "$PID" ]; then
    echo "❌ Error: Node '$NODE' not found or not running"
    echo ""
    echo "Make sure Mininet is running with: sudo python3 run.py"
    echo ""
    echo "Available nodes:"
    ps aux | grep "mininet:" | grep -v grep | sed 's/.*mininet://g' | awk '{print "  - " $1}' | sort -u
    exit 1
fi

echo "✓ Running on $NODE (PID: $PID): $CMD"
sudo mnexec -a $PID bash -c "$CMD"
