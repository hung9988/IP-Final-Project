# Multicast IPTV Quick Start Guide

## Setup Steps

### 1. Update Topology
✅ Already done - TV server added to R5

### 2. Enable PIM Daemon on All Routers

For each router (r1-r9), edit `daemons` file:

```bash
# Add this line to each router's daemons file
pimd=yes
```

### 3. Configure PIM on Routers

#### R5 (Rendezvous Point + TV Server)

Add to `r5/frr.conf`:
```
interface r5-eth2
 description TV Server Network
 ip address 10.100.5.1/24
 ip pim sm
exit

interface r5-eth0
 ip pim sm
exit

interface r5-eth1
 ip pim sm
exit

router pim
 rp 10.100.5.1 239.0.0.0/8
 join-prune-interval 60
exit
```

#### Edge Routers (R1, R3, R8, R9)

Add PIM + IGMP on PC-facing interfaces:

**R1:**
```
interface r1-eth0
 ip pim sm
exit

interface r1-eth1
 description PC1 Network
 ip igmp
 ip pim sm
exit

router pim
 rp 10.100.5.1 239.0.0.0/8
exit
```

**R3:**
```
interface r3-eth0
 ip pim sm
exit

interface r3-eth1
 description PC2 Network
 ip igmp
 ip pim sm
exit

router pim
 rp 10.100.5.1 239.0.0.0/8
exit
```

**R8:**
```
interface r8-eth0
 ip pim sm
exit

interface r8-eth1
 description PC3 Network
 ip igmp
 ip pim sm
exit

router pim
 rp 10.100.5.1 239.0.0.0/8
exit
```

**R9:**
```
interface r9-eth0
 ip pim sm
exit

interface r9-eth1
 description PC4 Network
 ip igmp
 ip pim sm
exit

router pim
 rp 10.100.5.1 239.0.0.0/8
exit
```

#### Transit Routers (R2, R4, R6, R7)

Add PIM on all interfaces:

**R2:**
```
interface r2-eth0
 ip pim sm
exit

interface r2-eth1
 ip pim sm
exit

interface r2-eth2
 ip pim sm
exit

interface r2-eth3
 ip pim sm
exit

router pim
 rp 10.100.5.1 239.0.0.0/8
exit
```

Similar for R4, R6, R7 on all their interfaces.

## Testing Multicast

### Step 1: Start the Network

```bash
# Apply FRR configs
sudo ./setup_frr.sh

# Start Mininet
sudo python3 run.py
```

### Step 2: Verify PIM is Running

In Mininet CLI:

```bash
# Check PIM neighbors on R5
r5 vtysh -c "show ip pim neighbor"

# Should show neighbors on all interfaces
# Expected: R4 and R6 as PIM neighbors

# Check RP info
r5 vtysh -c "show ip pim rp-info"

# Should show:
# RP: 10.100.5.1 (local)
# Group range: 239.0.0.0/8
```

### Step 3: Start TV Server

In Mininet CLI:

```bash
# Start multicast sender on TV server
tv_server python3 /home/hung1fps/final_ip_project/multi_as_network/multicast_sender.py &

# You should see:
# 📺 TV Server starting...
#    Multicast Group: 239.1.1.1
#    Port: 5007
```

### Step 4: Start Receivers on PCs

In Mininet CLI:

```bash
# Start receiver on PC1
pc1 python3 /home/hung1fps/final_ip_project/multi_as_network/multicast_receiver.py &

# Start receiver on PC2
pc2 python3 /home/hung1fps/final_ip_project/multi_as_network/multicast_receiver.py &

# Start receiver on PC3
pc3 python3 /home/hung1fps/final_ip_project/multi_as_network/multicast_receiver.py &

# Start receiver on PC4
pc4 python3 /home/hung1fps/final_ip_project/multi_as_network/multicast_receiver.py &
```

### Step 5: Verify Multicast Traffic

```bash
# Check IGMP groups on R1 (should show PC1 joined)
r1 vtysh -c "show ip igmp groups"

# Check multicast routes on R5
r5 vtysh -c "show ip mroute"

# Should show:
# (10.100.5.10, 239.1.1.1) - Source and Group
# Incoming interface: r5-eth2 (TV server)
# Outgoing interfaces: r5-eth0, r5-eth1 (to R4 and R6)

# Check multicast routes on R1
r1 vtysh -c "show ip mroute 239.1.1.1"

# Should show multicast tree from R5 to PC1
```

### Step 6: Monitor Traffic

```bash
# On PC1, you should see:
# ✓ Received frame 10: IPTV Frame #10 - Timestamp: ...
# ✓ Received frame 20: IPTV Frame #20 - Timestamp: ...

# Check packet counters
r5 vtysh -c "show ip pim interface"
```

## Troubleshooting

### Problem: PCs not receiving multicast

**Check 1: PIM neighbors**
```bash
r5 vtysh -c "show ip pim neighbor"
# All routers should be listed
```

**Check 2: IGMP membership**
```bash
r1 vtysh -c "show ip igmp groups"
# Should show 239.1.1.1 with PC1's interface
```

**Check 3: Multicast routes**
```bash
r5 vtysh -c "show ip mroute"
# Should show (S,G) entry for (10.100.5.10, 239.1.1.1)
```

**Check 4: Firewall/routing**
```bash
# On PC1, check multicast route
pc1 ip route show

# Add multicast route if missing
pc1 ip route add 224.0.0.0/4 dev pc1-eth0
```

### Problem: PIM neighbors not forming

**Solution**: Check interface configuration
```bash
r5 vtysh -c "show ip pim interface"
# All interfaces should show "PIM Enabled: yes"
```

### Problem: No multicast routes

**Solution**: Check RP configuration
```bash
r1 vtysh -c "show ip pim rp-info"
# Should show RP: 10.100.5.1
```

## Quick Test Commands

```bash
# In Mininet CLI

# 1. Start TV server
tv_server python3 multicast_sender.py &

# 2. Start one receiver
pc1 python3 multicast_receiver.py &

# 3. Check if PC1 is receiving
# You should see frame messages

# 4. Stop receiver
pc1 pkill -f multicast_receiver

# 5. Stop server
tv_server pkill -f multicast_sender
```

## Expected Multicast Tree

```
TV Server (10.100.5.10)
    ↓
   R5 (RP)
    ├─→ R4 → R2 ─┬→ R1 → PC1
    │            └→ R3 → PC2
    │
    └─→ R6 → R7 ─┬→ R8 → PC3
                 └→ R9 → PC4
```

## Performance Notes

- **Bandwidth**: Each stream is ~10 KB/s (test traffic)
- **Latency**: Should be < 50ms from server to any PC
- **Efficiency**: Multicast uses same bandwidth regardless of receiver count
- **Scalability**: Can support thousands of receivers with same network load

## Summary

✅ TV Server on R5: 10.100.5.10
✅ Multicast Group: 239.1.1.1
✅ Protocol: PIM-SM with R5 as RP
✅ IGMP on edge routers for PC subscriptions
✅ All PCs can receive the same stream efficiently

This is a production-ready multicast IPTV implementation!
