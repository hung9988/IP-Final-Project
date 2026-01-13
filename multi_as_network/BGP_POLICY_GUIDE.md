# BGP Traffic Engineering Policies

## Overview

Traffic between ISP #1 (AS 200) and ISP #2 (AS 300) can take two paths:

1. **Direct Peering**: R2 ↔ R7 (10.0.9.0/24)
2. **Transit via Tier 1**: R2 → R4 → R5 → R6 → R7

## Policy Objectives

### Primary Goal: Prefer Peering Path
- **Reason**: Lower cost, lower latency, less transit load
- **Method**: Use BGP Local Preference

### Secondary Goal: Use Transit as Backup
- **Reason**: Redundancy if peering link fails
- **Method**: Lower Local Preference for transit routes

## BGP Attributes Used

### 1. Local Preference (LP)
- **Scope**: Local to AS (not advertised to eBGP peers)
- **Default**: 100
- **Rule**: Higher is better
- **Our Policy**:
  - Peering routes: LP = **200** (preferred)
  - Transit routes: LP = **100** (backup)

### 2. AS Path Length
- **Natural behavior**: Shorter AS path is preferred
- Peering: AS_PATH = [300] or [200] (length 1)
- Transit: AS_PATH = [100, 300] or [100, 200] (length 2)
- This provides automatic preference even without LP manipulation

### 3. MED (Multi-Exit Discriminator)
- **Optional**: Can be used to influence incoming traffic
- **Scope**: Advertised to neighboring AS only
- Lower MED is preferred

## Configuration Strategy

### For R2 (ISP #1 Border Router)

**Inbound from R7 (Peering):**
```
route-map PREFER-PEERING permit 10
 set local-preference 200
```

**Inbound from R4 (Transit):**
```
route-map TRANSIT-BACKUP permit 10
 set local-preference 100
```

**Apply to neighbors:**
```
router bgp 200
 neighbor 10.0.9.2 route-map PREFER-PEERING in   ! R7 peering
 neighbor 10.0.3.2 route-map TRANSIT-BACKUP in   ! R4 transit
```

### For R7 (ISP #2 Border Router)

**Inbound from R2 (Peering):**
```
route-map PREFER-PEERING permit 10
 set local-preference 200
```

**Inbound from R6 (Transit):**
```
route-map TRANSIT-BACKUP permit 10
 set local-preference 100
```

**Apply to neighbors:**
```
router bgp 300
 neighbor 10.0.9.1 route-map PREFER-PEERING in   ! R2 peering
 neighbor 10.0.6.1 route-map TRANSIT-BACKUP in   ! R6 transit
```

## Traffic Flow Examples

### Example 1: PC1 → PC4

**Without Policy (AS Path only):**
- Path 1: PC1 → R1 → R2 → R7 → R9 → PC4 (AS_PATH: 200, 300) ✅ Chosen
- Path 2: PC1 → R1 → R2 → R4 → R5 → R6 → R7 → R9 → PC4 (AS_PATH: 200, 100, 300)

**With Local Preference Policy:**
- Path 1: LP=200, AS_PATH: 200, 300 ✅ **Strongly preferred**
- Path 2: LP=100, AS_PATH: 200, 100, 300

### Example 2: PC4 → PC1

**Without Policy:**
- Path 1: PC4 → R9 → R7 → R2 → R1 → PC1 (AS_PATH: 300, 200) ✅ Chosen
- Path 2: PC4 → R9 → R7 → R6 → R5 → R4 → R2 → R1 → PC1 (AS_PATH: 300, 100, 200)

**With Local Preference Policy:**
- Path 1: LP=200, AS_PATH: 300, 200 ✅ **Strongly preferred**
- Path 2: LP=100, AS_PATH: 300, 100, 200

## Advanced Policies (Optional)

### 1. Conditional Peering Preference
Only prefer peering for certain prefixes (e.g., customer routes):

```
ip prefix-list CUSTOMER-ROUTES permit 192.168.0.0/16 le 24

route-map PREFER-PEERING permit 10
 match ip address prefix-list CUSTOMER-ROUTES
 set local-preference 200
route-map PREFER-PEERING permit 20
 set local-preference 150
```

### 2. Load Balancing
Use both paths with different preferences:

```
route-map PEERING-PRIMARY permit 10
 set local-preference 200
 
route-map TRANSIT-SECONDARY permit 10
 set local-preference 150  ! Still usable, just less preferred
```

### 3. Time-Based Policies
Prefer transit during off-peak hours to balance load:

```
route-map DYNAMIC-PREFERENCE permit 10
 match time-range PEAK-HOURS
 set local-preference 200
route-map DYNAMIC-PREFERENCE permit 20
 set local-preference 150
```

## Tier 1 Perspective (AS 100)

### Policy for R4 and R6

Tier 1 should **not prefer** one customer over another:

```
router bgp 100
 ! No local-preference manipulation
 ! Let customers control their own traffic
 ! Charge for transit bandwidth used
```

**Optional**: Tier 1 can use MED to suggest preferred entry point:

```
route-map SET-MED-TO-ISP1 permit 10
 set metric 50
 
route-map SET-MED-TO-ISP2 permit 10
 set metric 50

router bgp 100
 neighbor 10.0.3.1 route-map SET-MED-TO-ISP1 out
 neighbor 10.0.6.2 route-map SET-MED-TO-ISP2 out
```

## Verification Commands

### Check BGP Routes
```bash
# On R2 (ISP #1)
vtysh -c "show ip bgp"
vtysh -c "show ip bgp 192.168.4.0/24"  # PC4's network

# Look for:
# - Local Preference value
# - AS Path
# - Best path marker (>)
```

### Check Route Selection
```bash
# On R2
vtysh -c "show ip bgp neighbors 10.0.9.2 routes"  # From R7 (peering)
vtysh -c "show ip bgp neighbors 10.0.3.2 routes"  # From R4 (transit)
```

### Test Traffic Path
```bash
# In Mininet CLI
pc1 traceroute 192.168.4.2

# Expected path with peering preference:
# 192.168.1.2 → 192.168.1.1 (R1) → 10.0.1.2 (R2) → 10.0.9.2 (R7) → ... → 192.168.4.2
```

## Summary

| Aspect | Peering Path | Transit Path |
|--------|-------------|--------------|
| **Local Preference** | 200 (high) | 100 (default) |
| **AS Path Length** | 1 hop | 2 hops |
| **Cost** | Free (settlement-free peering) | Paid (transit fees) |
| **Latency** | Lower (direct) | Higher (via Tier 1) |
| **Use Case** | Primary path | Backup/redundancy |

## Implementation Priority

1. **Start with AS Path** - Already works naturally (shorter path preferred)
2. **Add Local Preference** - Explicit control, recommended for production
3. **Consider MED** - For influencing incoming traffic from peers
4. **Advanced policies** - Only if needed for specific requirements

The key principle: **Peering is preferred, transit is backup**.
