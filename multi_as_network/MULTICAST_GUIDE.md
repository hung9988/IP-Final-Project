# Multicast IPTV Service Implementation

## Overview

**Scenario**: A TV streaming server in Tier 1 (AS 100) connected to R5 needs to multicast to all PCs across all ASes.

**Multicast Group**: 239.1.1.1 (IPTV channel)
**Source**: TV Server at 10.100.5.10 (connected to R5)
**Receivers**: PC1, PC2, PC3, PC4

## Multicast Topology

```
                    Tier 1 (AS 100)
                         R5
                          │
                    [TV Server]
                   10.100.5.10
                   Group: 239.1.1.1
                          │
              ┌───────────┴───────────┐
              │                       │
            R4                       R6
              │                       │
        ┌─────┴─────┐           ┌────┴────┐
        │           │           │         │
       R2          R1          R7        R8
        │           │           │         │
       PC2         PC1         PC3       PC4
    (receiver)  (receiver)  (receiver) (receiver)
```

## Multicast Protocols

### 1. PIM-SM (Protocol Independent Multicast - Sparse Mode)
- **Best for**: Internet-scale multicast
- **How it works**: Receivers explicitly join groups
- **Requires**: Rendezvous Point (RP)
- **Our choice**: ✅ Use this

### 2. PIM-DM (Dense Mode)
- **Best for**: Small networks with many receivers
- **How it works**: Flood and prune
- **Not suitable**: Too much overhead for our topology

## Implementation Strategy

### Step 1: Enable Multicast Routing
Enable on all routers: R1-R9

### Step 2: Configure PIM-SM
- **RP (Rendezvous Point)**: R5 (central location in Tier 1)
- **PIM interfaces**: All router-to-router links
- **IGMP**: On host-facing interfaces (for PC subscriptions)

### Step 3: Add TV Server
- Connect to R5
- IP: 10.100.5.10/24
- Streams to: 239.1.1.1

### Step 4: Configure IGMP on Edge Routers
- R1, R3, R8, R9 (routers with PCs)
- Enable IGMP on PC-facing interfaces

## Configuration Details

### Multicast Addressing

**Multicast IP Range**: 224.0.0.0 - 239.255.255.255
- 224.0.0.0/24: Reserved (link-local)
- 239.0.0.0/8: Administratively scoped (our choice)

**Our IPTV Service**:
- Group: 239.1.1.1 (IPTV Channel 1)
- Source: 10.100.5.10 (TV Server)

### PIM Configuration

#### R5 (Rendezvous Point + TV Server)

```
interface r5-eth2
 description TV Server Network
 ip address 10.100.5.1/24
 ip pim sm
exit

router pim
 rp 10.100.5.1 239.0.0.0/8
 join-prune-interval 60
exit

interface r5-eth0
 ip pim sm
exit

interface r5-eth1
 ip pim sm
exit
```

#### R1 (Edge Router with PC1)

```
interface r1-eth0
 description Link to R2
 ip pim sm
exit

interface r1-eth1
 description PC1 Network
 ip address 192.168.1.1/24
 ip igmp
 ip pim sm
exit

router pim
 rp 10.100.5.1 239.0.0.0/8
exit
```

#### R2 (Transit Router)

```
interface r2-eth0
 description Link to R1
 ip pim sm
exit

interface r2-eth1
 description Link to R3
 ip pim sm
exit

interface r2-eth2
 description Link to R4
 ip pim sm
exit

interface r2-eth3
 description Peering to R7
 ip pim sm
exit

router pim
 rp 10.100.5.1 239.0.0.0/8
exit
```

### IGMP Configuration

**IGMP (Internet Group Management Protocol)**:
- Used by hosts to join/leave multicast groups
- Version 2 or 3 (we'll use v2)

**On edge routers** (R1, R3, R8, R9):
```
interface <pc-facing-interface>
 ip igmp
 ip igmp version 2
exit
```

## Multicast Routing Flow

### Join Process (PC1 wants to watch TV)

1. **PC1** sends IGMP Join for 239.1.1.1
2. **R1** receives IGMP Join
3. **R1** sends PIM Join to RP (R5) via shortest path
4. **R2** forwards PIM Join to R4
5. **R4** forwards PIM Join to R5
6. **R5** (RP) registers the receiver
7. **Multicast tree** is built from R5 to R1

### Data Flow (TV Server streams)

1. **TV Server** sends to 239.1.1.1
2. **R5** receives multicast traffic
3. **R5** forwards down the multicast tree to all receivers
4. Traffic flows: R5 → R4 → R2 → R1 → PC1
5. Same for other PCs via their paths

## Topology Updates Needed

### Add TV Server to Mininet Topology

```python
# In topology.py, add TV server
tv_server = self.addHost('tv_server', 
                         ip='10.100.5.10/24',
                         defaultRoute='via 10.100.5.1')

# Link TV server to R5
self.addLink(tv_server, r5,
             intfName2='r5-eth2',
             params2={'ip': '10.100.5.1/24'})
```

## FRR Configuration Files

### Enable PIM Daemon

In `daemons` file for all routers:
```
pimd=yes
```

### FRR Config Structure

```
frr version 8.1
frr defaults traditional
hostname r5
!
interface r5-eth0
 ip pim sm
exit
!
interface r5-eth1
 ip pim sm
exit
!
interface r5-eth2
 description TV Server Network
 ip address 10.100.5.1/24
 ip pim sm
exit
!
router pim
 rp 10.100.5.1 239.0.0.0/8
 join-prune-interval 60
exit
!
```

## Testing Multicast

### 1. Start Multicast Server (TV Server)

```bash
# On TV server host
# Install iperf3 or use VLC for streaming
iperf3 -s -B 239.1.1.1 -p 5001

# Or use a simple Python multicast sender
python3 multicast_sender.py
```

### 2. Join Multicast Group (PCs)

```bash
# On PC1
ip route add 224.0.0.0/4 dev pc1-eth0
echo "1" > /proc/sys/net/ipv4/ip_forward
iperf3 -c 239.1.1.1 -p 5001 -B 192.168.1.2

# Or use multicast receiver
python3 multicast_receiver.py
```

### 3. Verify PIM Neighbors

```bash
# On any router
vtysh -c "show ip pim neighbor"

# Should show PIM neighbors on all interfaces
```

### 4. Verify Multicast Routes

```bash
# On R5 (RP)
vtysh -c "show ip pim rp-info"
vtysh -c "show ip mroute"

# Should show:
# - RP address
# - Multicast routes for 239.1.1.1
# - Incoming/outgoing interfaces
```

### 5. Verify IGMP Groups

```bash
# On R1 (edge router)
vtysh -c "show ip igmp groups"

# Should show PC1 joined to 239.1.1.1
```

## Multicast Tree Optimization

### Shortest Path Tree (SPT) Switchover

By default, PIM-SM uses:
1. **Shared Tree**: Source → RP → Receivers (initially)
2. **Source Tree**: Source → Receivers (optimized, after SPT switchover)

**SPT Threshold**: Configure when to switch
```
router pim
 spt-switchover infinity  # Stay on shared tree
 # OR
 # spt-switchover immediate  # Switch to source tree immediately
exit
```

### For IPTV, use immediate SPT switchover:
- Lower latency
- Better bandwidth utilization
- Direct path from R5 to each receiver

## Inter-AS Multicast Considerations

### MSDP (Multicast Source Discovery Protocol)

For multicast across AS boundaries, you might need MSDP:

```
router pim
 msdp peer 10.0.3.2 source 10.0.3.1  # R2 peers with R4
 msdp peer 10.0.6.1 source 10.0.6.2  # R7 peers with R6
exit
```

**However**, since our RP (R5) is in Tier 1 and all ASes connect to it, MSDP may not be necessary.

## Bandwidth Management

### Rate Limiting Multicast Traffic

```
interface r5-eth0
 ip multicast boundary 239.0.0.0/8
 # Limit bandwidth
 tc qdisc add dev r5-eth0 root tbf rate 10mbit burst 32kbit latency 400ms
exit
```

### QoS for IPTV

```
# Prioritize multicast traffic
ip access-list extended IPTV-TRAFFIC
 permit ip any 239.0.0.0 0.255.255.255
exit

class-map IPTV-CLASS
 match access-group IPTV-TRAFFIC
exit

policy-map IPTV-POLICY
 class IPTV-CLASS
  priority percent 50
exit
```

## Security Considerations

### Multicast Boundary

Prevent multicast leaking:
```
interface r2-eth3
 description Peering with ISP2
 ip multicast boundary 239.0.0.0/8 filter-autorp
exit
```

### Access Control

```
# Only allow specific sources
ip pim accept-register list ALLOWED-SOURCES
access-list ALLOWED-SOURCES permit 10.100.5.10
```

## Troubleshooting Commands

```bash
# Check PIM status
show ip pim interface
show ip pim neighbor
show ip pim rp-info

# Check multicast routes
show ip mroute
show ip mroute 239.1.1.1

# Check IGMP
show ip igmp groups
show ip igmp interface

# Check multicast forwarding
show ip mfib
show ip mfib 239.1.1.1

# Debug (use carefully)
debug pim packets
debug igmp packets
```

## Summary

| Component | Configuration |
|-----------|---------------|
| **RP** | R5 (10.100.5.1) |
| **Multicast Group** | 239.1.1.1 |
| **TV Server** | 10.100.5.10 on R5 |
| **Protocol** | PIM-SM |
| **IGMP** | Enabled on R1, R3, R8, R9 |
| **Receivers** | PC1, PC2, PC3, PC4 |

**Traffic Flow**:
TV Server → R5 (RP) → Multicast Tree → All PCs

This provides efficient, scalable multicast delivery across your multi-AS network!
