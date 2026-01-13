# BGP Configuration Fix for Tier 1 Connectivity

## Problem Identified

PC1 (and other hosts in ISP #1) could ping hosts and routers in ISP #2, but **could NOT ping routers in Tier 1 (R4, R5, R6)**.

## Root Causes

### 1. **Incorrect iBGP Peering in Tier 1**
- **R4** was trying to peer with R6 at `10.0.5.2` (not directly connected)
- **R6** was trying to peer with R4 at `10.0.4.1` (not directly connected)
- iBGP neighbors must be **reachable** (either directly or via IGP)

### 2. **Missing BGP on R5**
- **R5** is the central router connecting R4 and R6
- R5 had **no BGP configuration** at all
- This broke the iBGP mesh needed to distribute external routes within AS 100

### 3. **Missing Route Redistribution**
- OSPF wasn't redistributing BGP routes properly
- BGP wasn't using route reflector to avoid full mesh

## Solution Implemented

### Architecture: **Route Reflector Topology**

Instead of full iBGP mesh (which would require R4↔R5, R5↔R6, R4↔R6), we use **R5 as a Route Reflector**:

```
        eBGP to AS 200
              ↓
            [R4] ←─────── iBGP ────────→ [R5] ←────── iBGP ────────→ [R6]
                                          ↑                              ↓
                                   Route Reflector                  eBGP to AS 300
                                   (cluster-id: 10.0.4.2)
```

### Changes Made

#### **R4 (Border Router to ISP #1)**
- ✅ Changed iBGP neighbor from `10.0.5.2` (R6) → `10.0.4.2` (R5)
- ✅ Added `next-hop-self` for iBGP neighbor
- ✅ Removed manual network advertisement for 10.0.5.0/24 (learned via OSPF)

#### **R5 (Route Reflector)**
- ✅ **Added BGP configuration** (was completely missing!)
- ✅ Enabled `bgpd=yes` in daemons file
- ✅ Configured as Route Reflector with `bgp cluster-id 10.0.4.2`
- ✅ Set both R4 and R6 as route-reflector-clients
- ✅ Added `redistribute bgp` in OSPF to distribute external routes internally

#### **R6 (Border Router to ISP #2)**
- ✅ Changed iBGP neighbor from `10.0.4.1` (R4) → `10.0.5.1` (R5)
- ✅ Added `next-hop-self` for iBGP neighbor
- ✅ Removed manual network advertisement for 10.0.4.0/24 (learned via OSPF)

## How Route Reflector Works

1. **R4** receives external routes from AS 200 via eBGP
2. **R4** sends these routes to **R5** via iBGP
3. **R5** (Route Reflector) reflects these routes to **R6**
4. **R6** can now forward traffic to AS 200 networks
5. Same process works in reverse for routes from AS 300

**Benefits:**
- ✅ Only 2 iBGP sessions needed (R4↔R5, R5↔R6) instead of 3
- ✅ Scales better as network grows
- ✅ R5 acts as central point for route distribution

## How to Apply the Fix

### Step 1: Re-run FRR Setup
```bash
cd /home/hung1fps/final_ip_project/multi_as_network
sudo ./setup_frr.sh
```

### Step 2: Restart the Network
```bash
# Stop current Mininet session (Ctrl+C or type 'exit' in CLI)
# Then restart:
sudo python3 run.py
```

### Step 3: Verify Connectivity

In the Mininet CLI, test:

```bash
# Test PC1 can reach Tier 1 routers
pc1 ping -c 3 10.0.4.1  # R4
pc1 ping -c 3 10.0.4.2  # R5
pc1 ping -c 3 10.0.5.2  # R6

# Test PC1 can reach all other PCs
pc1 ping -c 3 192.168.2.2  # PC2
pc1 ping -c 3 192.168.3.2  # PC3
pc1 ping -c 3 192.168.4.2  # PC4
```

### Step 4: Verify BGP Sessions

Access router CLI to check BGP status:

```bash
# In Mininet CLI:
r5 vtysh -c "show ip bgp summary"
r4 vtysh -c "show ip bgp summary"
r6 vtysh -c "show ip bgp summary"

# Check BGP routes:
r5 vtysh -c "show ip bgp"
```

You should see:
- R4 has 1 eBGP session (to R2) and 1 iBGP session (to R5)
- R5 has 2 iBGP sessions (to R4 and R6) - both should show "Established"
- R6 has 1 eBGP session (to R7) and 1 iBGP session (to R5)

## Expected Behavior After Fix

✅ **PC1** can ping all routers (R1-R9)  
✅ **PC1** can ping all hosts (PC2, PC3, PC4)  
✅ **All PCs** have full connectivity to each other  
✅ **BGP routes** are properly distributed within AS 100  
✅ **OSPF** distributes BGP routes to all Tier 1 routers  

## Technical Details

### Why Route Reflector?

In iBGP, routes learned from one iBGP peer are **not** re-advertised to other iBGP peers (to prevent loops). This means:

**Without Route Reflector:**
- Need full mesh: R4↔R5, R5↔R6, R4↔R6 (3 sessions for 3 routers)
- For N routers: N(N-1)/2 sessions needed
- Doesn't scale well

**With Route Reflector:**
- R5 is configured to **reflect** routes between its clients
- Only need R4→R5 and R6→R5 (2 sessions)
- For N clients: N sessions to RR
- Scales much better

### Key Configuration Lines

**R5 as Route Reflector:**
```
router bgp 100
 bgp cluster-id 10.0.4.2                    # Identifies this RR cluster
 neighbor 10.0.4.1 route-reflector-client   # R4 is a client
 neighbor 10.0.5.2 route-reflector-client   # R6 is a client
```

**R4 and R6 with next-hop-self:**
```
neighbor 10.0.4.2 next-hop-self  # Changes next-hop to self for iBGP
```

This ensures that when R4 advertises routes from AS 200 to R5, the next-hop is set to R4's IP, making it reachable via OSPF.

## Troubleshooting

If connectivity still doesn't work after applying the fix:

1. **Check BGP sessions:**
   ```bash
   r5 vtysh -c "show ip bgp summary"
   ```
   All sessions should show "Established"

2. **Check OSPF neighbors:**
   ```bash
   r5 vtysh -c "show ip ospf neighbor"
   ```
   Should see R4 and R6

3. **Check routing table:**
   ```bash
   r5 vtysh -c "show ip route"
   ```
   Should see routes from all ASes

4. **Check if FRR is running:**
   ```bash
   r5 ps aux | grep frr
   ```

5. **Check FRR logs:**
   ```bash
   sudo tail -f /var/log/frr/r5/frr.log
   ```

## Files Modified

- `r4/frr.conf` - Fixed iBGP neighbor
- `r5/frr.conf` - Added complete BGP configuration
- `r5/daemons` - Enabled bgpd
- `r6/frr.conf` - Fixed iBGP neighbor

## Summary

The issue was a **broken iBGP topology** in AS 100. By implementing R5 as a Route Reflector and fixing the neighbor relationships, BGP routes now properly flow through Tier 1, enabling full connectivity across all three autonomous systems.
