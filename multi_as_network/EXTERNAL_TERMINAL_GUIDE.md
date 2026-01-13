# Connecting to Mininet from Another Terminal

## Method 1: Using `mnexec` (Recommended)

This is the cleanest way to run commands on Mininet nodes from another terminal.

### Step 1: Find the Process ID (PID) of the node

In a new terminal:
```bash
# List all Mininet nodes and their PIDs
ps aux | grep "mininet:"

# Or more specifically for a node like pc1:
ps aux | grep "mininet:pc1"
```

You'll see output like:
```
root      12345  ... bash --norc -is mininet:pc1
```

The PID is `12345` in this example.

### Step 2: Execute command using mnexec

```bash
# Run command on pc1 using its PID
sudo mnexec -a 12345 python3 /home/hung1fps/final_ip_project/multi_as_network/multicast_receiver.py

# Or for background execution:
sudo mnexec -a 12345 python3 /home/hung1fps/final_ip_project/multi_as_network/multicast_receiver.py &
```

### Automated Script

Create a helper script to make this easier:

```bash
#!/bin/bash
# mn_exec.sh - Execute command on Mininet node from external terminal

NODE=$1
shift
COMMAND="$@"

if [ -z "$NODE" ] || [ -z "$COMMAND" ]; then
    echo "Usage: $0 <node_name> <command>"
    echo "Example: $0 pc1 python3 multicast_receiver.py"
    exit 1
fi

# Find the PID of the node
PID=$(ps aux | grep "mininet:$NODE" | grep -v grep | awk '{print $2}' | head -1)

if [ -z "$PID" ]; then
    echo "Error: Node '$NODE' not found"
    echo "Available nodes:"
    ps aux | grep "mininet:" | grep -v grep | sed 's/.*mininet://g' | awk '{print $1}'
    exit 1
fi

echo "Executing on $NODE (PID: $PID): $COMMAND"
sudo mnexec -a $PID $COMMAND
```

Usage:
```bash
chmod +x mn_exec.sh
./mn_exec.sh pc1 python3 multicast_receiver.py
```

## Method 2: Using `util/m` Script (If Available)

Mininet comes with a utility script:

```bash
# From Mininet source directory
sudo util/m pc1 python3 multicast_receiver.py
```

## Method 3: Using SSH/Screen/Tmux with xterm

If you started Mininet with xterm support:

```bash
# In main Mininet terminal
mininet> xterm pc1

# This opens a new terminal window for pc1
# Then in that window:
python3 multicast_receiver.py
```

## Method 4: Direct Network Namespace Access

Each Mininet node runs in its own network namespace:

```bash
# List network namespaces
sudo ip netns list

# Execute in namespace (if namespaces are used)
sudo ip netns exec <namespace> python3 multicast_receiver.py
```

**Note**: This might not work if Mininet isn't using network namespaces.

## Method 5: Using `screen` or `tmux` (Best for Multiple Terminals)

### Setup with tmux:

```bash
# Install tmux if not available
sudo apt-get install tmux

# Start tmux session
tmux new -s mininet

# In tmux, start Mininet
sudo python3 run.py

# Split terminal (Ctrl+b then ")
# In new pane, use mnexec method above
```

### Tmux Quick Commands:
- `Ctrl+b "` - Split horizontally
- `Ctrl+b %` - Split vertically
- `Ctrl+b arrow` - Navigate between panes
- `Ctrl+b d` - Detach from session
- `tmux attach -t mininet` - Reattach to session

## Practical Example: Running Multicast Test

### Terminal 1: Start Mininet
```bash
cd /home/hung1fps/final_ip_project/multi_as_network
sudo python3 run.py
# Wait for "*** Starting CLI:"
```

### Terminal 2: Start TV Server
```bash
# Find tv_server PID
TV_PID=$(ps aux | grep "mininet:tv_server" | grep -v grep | awk '{print $2}' | head -1)

# Start sender
sudo mnexec -a $TV_PID python3 /home/hung1fps/final_ip_project/multi_as_network/multicast_sender.py
```

### Terminal 3: Start PC1 Receiver
```bash
# Find pc1 PID
PC1_PID=$(ps aux | grep "mininet:pc1" | grep -v grep | awk '{print $2}' | head -1)

# Start receiver
sudo mnexec -a $PC1_PID python3 /home/hung1fps/final_ip_project/multi_as_network/multicast_receiver.py
```

### Terminal 4: Start PC2 Receiver
```bash
PC2_PID=$(ps aux | grep "mininet:pc2" | grep -v grep | awk '{print $2}' | head -1)
sudo mnexec -a $PC2_PID python3 /home/hung1fps/final_ip_project/multi_as_network/multicast_receiver.py
```

## Quick Reference Script

Save this as `run_on_node.sh`:

```bash
#!/bin/bash
# Quick script to run commands on Mininet nodes

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <node> <command> [args...]"
    echo ""
    echo "Examples:"
    echo "  $0 pc1 ifconfig"
    echo "  $0 tv_server python3 multicast_sender.py"
    echo "  $0 pc2 'python3 multicast_receiver.py &'"
    echo ""
    echo "Available nodes:"
    ps aux | grep "mininet:" | grep -v grep | sed 's/.*mininet://g' | awk '{print "  - " $1}' | sort -u
    exit 1
fi

NODE=$1
shift
CMD="$@"

PID=$(ps aux | grep "mininet:$NODE" | grep -v grep | awk '{print $2}' | head -1)

if [ -z "$PID" ]; then
    echo "❌ Error: Node '$NODE' not found or not running"
    exit 1
fi

echo "✓ Running on $NODE (PID: $PID)"
sudo mnexec -a $PID bash -c "$CMD"
```

Usage:
```bash
chmod +x run_on_node.sh

# Start TV server
./run_on_node.sh tv_server "python3 multicast_sender.py &"

# Start receivers
./run_on_node.sh pc1 "python3 multicast_receiver.py &"
./run_on_node.sh pc2 "python3 multicast_receiver.py &"
./run_on_node.sh pc3 "python3 multicast_receiver.py &"
./run_on_node.sh pc4 "python3 multicast_receiver.py &"
```

## Troubleshooting

### Issue: "Node not found"
**Solution**: Make sure Mininet is running and the node exists
```bash
ps aux | grep "mininet:" | grep -v grep
```

### Issue: "Permission denied"
**Solution**: Use `sudo` with mnexec
```bash
sudo mnexec -a <PID> <command>
```

### Issue: "Command not found: mnexec"
**Solution**: Install Mininet properly or use full path
```bash
/usr/bin/mnexec -a <PID> <command>
```

## Best Practice Workflow

1. **Terminal 1**: Run Mininet
   ```bash
   sudo python3 run.py
   ```

2. **Terminal 2**: Create helper script and run commands
   ```bash
   # Create the run_on_node.sh script above
   chmod +x run_on_node.sh
   
   # Use it to control nodes
   ./run_on_node.sh tv_server "python3 multicast_sender.py &"
   ./run_on_node.sh pc1 "python3 multicast_receiver.py"
   ```

3. **Terminal 3**: Monitor/debug
   ```bash
   # Check processes
   ps aux | grep multicast
   
   # Check network
   ./run_on_node.sh r5 "vtysh -c 'show ip pim neighbor'"
   ```

This gives you full control over your Mininet network from multiple terminals!
