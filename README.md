# Multi-AS Network with Mininet and FRR

A complete implementation of a multi-Autonomous System (AS) network using Mininet and FRRouting (FRR), featuring BGP routing, multicast IPTV, and Quality of Service (QoS).

## 📋 Table of Contents

- [Overview](#overview)
- [Network Topology](#network-topology)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Testing Guide](#testing-guide)
  - [1. Basic Connectivity](#1-basic-connectivity-test)
  - [2. BGP Peering Policy](#2-bgp-peering-policy-test)
  - [3. Multicast IPTV](#3-multicast-iptv-test)
  - [4. Quality of Service](#4-quality-of-service-qos-test)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)

## 🌐 Overview

This project implements a realistic multi-AS network topology with:
- **3 Autonomous Systems**: Tier 1 (AS 100), ISP #1 (AS 200), ISP #2 (AS 300)
- **9 Routers**: Running FRRouting with OSPF, RIP, and BGP
- **4 End Hosts**: PC1, PC2, PC3, PC4
- **1 TV Server**: For multicast IPTV streaming

## 🗺️ Network Topology

```
                    ┌─────────────────────────────┐
                    │     Tier 1 (AS 100)         │
                    │         OSPF                │
                    │   R4 ──── R5 ──── R6        │
                    │    │              │         │
                    └────┼──────────────┼─────────┘
                         │ BGP      BGP │
                         │              │
        ┌────────────────┼──────────────┼────────────────┐
        │                │              │                │
        │  ISP #1        │              │     ISP #2     │
        │  (AS 200)      │              │     (AS 300)   │
        │   RIP          │              │      OSPF      │
        │                │              │                │
        │  R1 ── R2 ── R3│              │ R7 ── R8       │
        │  │      │    │ │              │ │      │       │
        │  │      │    │ │              │ │      │       │
        │ PC1    Peer  PC2              │ │     PC3      │
        │         │      │              │ R9             │
        │         └──────┼──────────────┘ │              │
        │                │                PC4            │
        └────────────────┴────────────────────────────────┘
                    Peering Link
```

### Network Details

| AS | Name | IGP | Routers | Hosts |
|----|------|-----|---------|-------|
| 100 | Tier 1 | OSPF | R4, R5, R6 | TV Server (on R5) |
| 200 | ISP #1 | RIP | R1, R2, R3 | PC1, PC2 |
| 300 | ISP #2 | OSPF | R7, R8, R9 | PC3, PC4 |

**BGP Connections:**
- R2 (ISP #1) ↔ R4 (Tier 1) - Transit
- R6 (Tier 1) ↔ R7 (ISP #2) - Transit
- R2 (ISP #1) ↔ R7 (ISP #2) - **Peering** (preferred path)

## ✨ Features

### 1. **Multi-AS BGP Routing**
- eBGP between ASes
- iBGP with Route Reflector (R5) in Tier 1
- BGP policy: Peering preferred over transit (Local Preference)

### 2. **Multicast IPTV**
- PIM-SM (Protocol Independent Multicast - Sparse Mode)
- R5 as Rendezvous Point (RP)
- IGMP on edge routers
- Dynamic source support

### 3. **Quality of Service (QoS)**
- HTB (Hierarchical Token Bucket) queuing
- Priority classes for customer vs infrastructure traffic
- Bandwidth guarantees and limits
- Traffic marking with iptables

### 4. **Network Visualization**
- Native Python GUI with Tkinter
- AS-based clustering
- Color-coded links and nodes
- Export to PNG/PDF

## 📦 Prerequisites

- **Operating System**: Ubuntu 20.04+ or Debian 10+
- **Privileges**: Root/sudo access
- **RAM**: Minimum 2GB
- **Disk Space**: 2GB free

## 🚀 Installation

### Step 1: Clone the Repository

```bash
cd /home/hung1fps/final_ip_project
cd multi_as_network
```

### Step 2: Install Dependencies

```bash
sudo ./install_dependencies.sh
```

This will install:
- Mininet
- FRRouting (FRR)
- Python 3 and required packages (matplotlib, networkx)
- iperf3, tcpdump, and other network tools

### Step 3: Setup FRR Configurations

```bash
sudo ./setup_frr.sh
```

This copies router configurations to the FRR directories.

## 🎯 Quick Start

### Start the Network

```bash
sudo python3 run.py
```

You should see:
```
*** Network is ready ***
*** You can test connectivity with: pc1 ping pc4 ***

*** Starting CLI:
mininet>
```

### Basic Test

In the Mininet CLI:
```bash
# Test connectivity
pc1 ping -c 3 pc4

# Check routing
pc1 traceroute 192.168.4.2

# Exit
exit
```

### Cleanup

```bash
sudo mn -c
```

## 🧪 Testing Guide

### 1. Basic Connectivity Test

**Purpose**: Verify all nodes can communicate

**Steps**:

```bash
# Start network
sudo python3 run.py

# In Mininet CLI, test all PC pairs:
mininet> pc1 ping -c 3 pc2
mininet> pc1 ping -c 3 pc3
mininet> pc1 ping -c 3 pc4
mininet> pc2 ping -c 3 pc3
mininet> pc2 ping -c 3 pc4
mininet> pc3 ping -c 3 pc4
or
mininet> pingall
```

**Expected Result**: All pings should succeed with 0% packet loss

**Verification**:
```bash
# Check routing table on PC1
mininet> pc1 ip route

# Trace path from PC1 to PC3
mininet> pc1 traceroute -n 192.168.3.2
```

**Success Criteria**:
- ✅ All PCs can ping each other
- ✅ Traceroute shows proper path through routers
- ✅ 0% packet loss

---

### 2. BGP Peering Policy Test

**Purpose**: Verify BGP prefers peering over transit

**Background**: Traffic between ISP #1 and ISP #2 can go via:
- **Peering**: R2 ↔ R7 (preferred, Local Pref = 200)
- **Transit**: R2 → R4 → R5 → R6 → R7 (backup, Local Pref = 100)

**Steps**:

#### A. Check BGP Configuration

In another terminal:
```bash
cd /home/hung1fps/final_ip_project/multi_as_network

# Check BGP sessions on R2
./run_on_node.sh r2 "show ip bgp summary"

# Check BGP routes on R2
./run_on_node.sh r2 "show ip bgp"
```

#### B. Verify Route Preference

```bash
# Check specific route to ISP #2 network
./run_on_node.sh r2 "show ip bgp 192.168.4.0/24"
```

**Expected Output**:
```
BGP routing table entry for 192.168.4.0/24
Paths: (2 available, best #1)
  300
    10.0.9.2 from 10.0.9.2 (10.0.6.2)
      Origin IGP, localpref 200, valid, external, best  ← PEERING (LP=200)
  100 300
    10.0.3.2 from 10.0.3.2 (10.0.3.2)
      Origin IGP, localpref 100, valid, external        ← TRANSIT (LP=100)
```

#### C. Verify Traffic Path

```bash
# In Mininet CLI
mininet> pc1 traceroute -n 192.168.4.2
```

**Expected Path** (via peering):
```
1  192.168.1.1  (R1)
2  10.0.1.2     (R2)
3  10.0.9.2     (R7) ← Peering link!
4  10.0.8.2     (R9)
5  192.168.4.2  (PC4)
```

**NOT via transit**:
```
❌ Should NOT see: R2 → R4 → R5 → R6 → R7
```

#### D. Automated Test

```bash
./verify_bgp_policy.sh
```

**Success Criteria**:
- ✅ BGP sessions are "Established"
- ✅ Peering routes have Local Pref = 200
- ✅ Transit routes have Local Pref = 100
- ✅ Peering route is marked as "best"
- ✅ Traceroute shows traffic via R2→R7 (peering)

---

### 3. Multicast IPTV Test

**Purpose**: Verify multicast streaming from TV server to all PCs

**Background**: TV server on R5 streams to multicast group 239.1.1.1 using PIM-SM

**Steps**:

#### A. Verify PIM Configuration

```bash
# Check PIM neighbors on R5 (Rendezvous Point)
./run_on_node.sh r5 "show ip pim neighbor"

# Check RP information
./run_on_node.sh r5 "show ip pim rp-info"
```

**Expected**: R5 should show R4 and R6 as PIM neighbors

#### B. Start TV Server

In another terminal:
```bash
# Start multicast sender on TV server
./run_on_node.sh tv_server "python3 multicast_sender.py &"
```

**Expected Output**:
```
📺 TV Server starting...
   Multicast Group: 239.1.1.1
   Port: 5007
   TTL: 32
✓ Sent frame 0
✓ Sent frame 10
...
```

#### C. Start Receivers on PCs

```bash
# Start receiver on PC1
./run_on_node.sh pc1 "python3 multicast_receiver.py &"

# Start receiver on PC2
./run_on_node.sh pc2 "python3 multicast_receiver.py &"

# Start receiver on PC3
./run_on_node.sh pc3 "python3 multicast_receiver.py &"

# Start receiver on PC4
./run_on_node.sh pc4 "python3 multicast_receiver.py &"
```

**Expected Output** (on each PC):
```
📺 IPTV Receiver starting on mininet-vm...
   Multicast Group: 239.1.1.1
   Port: 5007
   Waiting for stream...

✓ Received frame 10: IPTV Frame #10 - Timestamp: ...
✓ Received frame 20: IPTV Frame #20 - Timestamp: ...
...
```

#### D. Verify Multicast Routes

```bash
# Check multicast routes on R5
./run_on_node.sh r5 "show ip mroute"

# Check IGMP groups on R1 (should show PC1 joined)
./run_on_node.sh r1 "show ip igmp groups"
```

#### E. Test Dynamic Source

```bash
# Stop TV server
./run_on_node.sh tv_server "pkill -f multicast_sender"

# Start new source on PC3
./run_on_node.sh pc3 "python3 multicast_sender.py &"
```

**Expected**: All receivers automatically switch to new source!

**Success Criteria**:
- ✅ PIM neighbors established on all routers
- ✅ R5 configured as RP
- ✅ All PCs receive multicast stream
- ✅ Multicast routes show (S,G) entries
- ✅ Dynamic source switching works

---

<!-- ### 4. Quality of Service (QoS) Test

**Purpose**: Verify QoS prioritizes customer traffic over infrastructure traffic

**Background**: QoS should guarantee bandwidth for PC-to-PC traffic even under congestion

**Steps**:

#### A. Setup QoS

```bash
# Apply QoS configuration
./setup_qos.sh
```

**Expected Output**:
```
✅ QoS Configuration Complete!

Traffic Classification:
  HIGH Priority (mark 1):
    - PC1 ↔ PC3
    - PC2 ↔ PC4
  LOW Priority (mark 3):
    - R2 ↔ R7
    - R4 ↔ R6
```

#### B. Light Traffic Test

```bash
# Run basic QoS test (4 flows)
./test_qos.sh
```

**Expected Results**:
```
Flow PC1 → PC3 (HIGH PRIORITY):
  Average Bandwidth: 8-10 Mbps

Flow PC2 → PC4 (HIGH PRIORITY):
  Average Bandwidth: 8-10 Mbps

Flow R2 → R7 (LOW PRIORITY):
  Average Bandwidth: 8-12 Mbps

Flow R4 → R6 (LOW PRIORITY):
  Average Bandwidth: 2-5 Mbps
```

#### C. Congestion Test (Recommended)

```bash
# Run congestion test (11 flows to create heavy load)
./test_qos_congestion.sh
```

**Expected Results Under Congestion**:
```
HIGH PRIORITY Traffic (Customer):
  PC1 → PC3: 24-30 Mbps total (3 streams)
  PC2 → PC4: 24-30 Mbps total (3 streams)

LOW PRIORITY Traffic (Infrastructure):
  R2 → R7: 8-15 Mbps total (4 streams) ← LIMITED!
  R4 → R6: 2-5 Mbps
```

#### D. Verify QoS Statistics

```bash
# Check QoS on peering interface
./run_on_node.sh r2 "tc -s class show dev r2-eth3"
```

**Expected Output**:
```
class htb 1:10 (HIGH):
 Sent 450M bytes  ← Large (customer traffic)
 
class htb 1:30 (LOW):
 Sent 85M bytes   ← Smaller (router traffic limited)
```

#### E. Diagnostic

```bash
# Run diagnostic tool
./diagnose_qos.sh
```

**Success Criteria**:
- ✅ Packets marked correctly (iptables shows marks)
- ✅ TC classes configured on all interfaces
- ✅ Customer traffic maintains 8-15 Mbps per flow
- ✅ Under congestion, HIGH priority gets more bandwidth than LOW
- ✅ QoS statistics show traffic in correct classes

--- -->

## 📁 Project Structure

```
multi_as_network/
├── README.md                          # This file
├── install_dependencies.sh            # Dependency installation
├── topology.py                        # Network topology definition
├── run.py                             # Main script to start network
├── setup_frr.sh                       # FRR configuration setup
│
├── r1/, r2/, ..., r9/                 # Router configurations
│   ├── frr.conf                       # FRR routing config
│   ├── daemons                        # FRR daemons to run
│   └── vtysh.conf                     # vtysh config
│
├── BGP Configuration
│   ├── BGP_FIX_DOCUMENTATION.md       # BGP route reflector setup
│   ├── BGP_POLICY_GUIDE.md            # BGP policy documentation
│   └── verify_bgp_policy.sh           # BGP verification script
│
├── Multicast
│   ├── MULTICAST_GUIDE.md             # Multicast theory
│   ├── MULTICAST_QUICKSTART.md        # Quick setup guide
│   ├── MULTICAST_DYNAMIC_SOURCES.md   # Dynamic source support
│   ├── multicast_sender.py            # TV server script
│   └── multicast_receiver.py          # PC receiver script
│
├── Quality of Service
│   ├── QOS_GUIDE.md                   # QoS theory
│   ├── QOS_QUICKSTART.md              # Quick setup guide
│   ├── QOS_CONGESTION_TEST.md         # Congestion test guide
│   ├── QOS_PATH_ANALYSIS.md           # Traffic path analysis
│   ├── setup_qos.sh                   # QoS configuration
│   ├── test_qos.sh                    # Basic QoS test
│   ├── test_qos_congestion.sh         # Congestion test
│   └── diagnose_qos.sh                # QoS diagnostic tool
│
├── Visualization
│   ├── topology_editor.py             # GUI topology editor
│   ├── visualize_topology.py          # Standalone visualizer
│   ├── VISUALIZATION_GUIDE.md         # Visualization guide
│   └── launch_editor.sh               # Editor launcher
│
└── Utilities
    ├── run_on_node.sh                 # Execute commands on nodes
    ├── EXTERNAL_TERMINAL_GUIDE.md     # Multi-terminal usage
    └── TOPOLOGY_EDITOR_README.md      # Editor documentation
```

## 🔧 Troubleshooting

### Network Won't Start

**Problem**: `sudo python3 run.py` fails

**Solutions**:
```bash
# Clean up previous instances
sudo mn -c

# Check FRR is installed
vtysh -v

# Reinstall dependencies
sudo ./install_dependencies.sh
```

### PCs Can't Ping Each Other

**Problem**: Connectivity issues

**Solutions**:
```bash
# Check routing on PC1
pc1 ip route

# Check FRR is running on routers
./run_on_node.sh r1 "show ip route"

# Verify BGP sessions
./run_on_node.sh r2 "show ip bgp summary"
```

### Multicast Not Working

**Problem**: PCs don't receive multicast

**Solutions**:
```bash
# Check PIM is enabled
./run_on_node.sh r5 "show ip pim interface"

# Verify RP configuration
./run_on_node.sh r5 "show ip pim rp-info"

# Check IGMP
./run_on_node.sh r1 "show ip igmp groups"
```

### QoS Not Prioritizing

**Problem**: All flows get same bandwidth

**Solutions**:
```bash
# Re-apply QoS
./setup_qos.sh

# Check packet marking
./run_on_node.sh r2 "iptables -t mangle -L -v -n"

# Run diagnostic
./diagnose_qos.sh

# Use congestion test (not light traffic test)
./test_qos_congestion.sh
```

## 📚 Documentation

### Quick Reference

- **BGP**: See `BGP_POLICY_GUIDE.md`
- **Multicast**: See `MULTICAST_QUICKSTART.md`
- **QoS**: See `QOS_QUICKSTART.md`
- **Visualization**: See `VISUALIZATION_GUIDE.md`

### Key Commands

```bash
# Start network
sudo python3 run.py

# Setup QoS
./setup_qos.sh

# Test connectivity
pc1 ping pc4

# Check BGP
./run_on_node.sh r2 "show ip bgp summary"

# Start multicast
./run_on_node.sh tv_server "python3 multicast_sender.py &"

# Visualize topology
python3 visualize_topology.py
```

## 🎓 Learning Outcomes

This project demonstrates:

1. **Multi-AS BGP Routing**
   - eBGP and iBGP configuration
   - Route reflectors
   - BGP policy (Local Preference)

2. **Multicast Networking**
   - PIM-SM protocol
   - Rendezvous Point (RP)
   - IGMP for host subscriptions

3. **Quality of Service**
   - Traffic classification
   - HTB queuing disciplines
   - Priority enforcement

4. **Network Integration**
   - Multiple routing protocols (OSPF, RIP, BGP)
   - Inter-AS communication
   - Production-grade network design

## 👥 Authors

- Network design and implementation
- FRR configuration
- QoS and multicast setup
- Testing and documentation

## 📄 License

This project is for educational purposes.

## 🙏 Acknowledgments

- Mininet project
- FRRouting project
- Network engineering community

---

**For detailed information on specific features, see the documentation files in the project directory.**
