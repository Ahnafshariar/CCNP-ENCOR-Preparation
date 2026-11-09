# Lab 15 - BGP Route Aggregation with Null Route and Prefix-List Filtering (5 Routers)

**CCNP ENCOR Domain:** 3.0 Infrastructure (25%)
**Topics:** Route Aggregation, Null Route, Prefix-List Filtering, ISP Best Practices, BGP Network Design

---

## Topology

```
  R1 (AS 10)        R2 (AS 20)        R3 (AS 30)
  Lo100: .11        Lo100: .12        Lo100: .13
     |                  |                  |
  e0/0              e0/0              e0/0
 10.1.4.1          10.1.4.9         10.1.4.17
     |                  |                  |
 10.1.4.2         10.1.4.10        10.1.4.18
  e0/0              e0/1              e0/2
      \                 |                /
       --------- R4 (AS 40) ---------
               ISP / Aggregator
            Null route: 11.111.111.0/24
            Prefix-list: only /24 out
                     |
               e0/3 (11.1.1.1)
                     |
               e0/0 (11.1.1.2)
                R5 (AS 50)
             Upstream ISP
          Prefix-list: reject /25-/32
                       reject default
                       accept /0-/24
```

All loopbacks fall within 11.111.111.0/24:
- R1: 11.111.111.11/32
- R2: 11.111.111.12/32
- R3: 11.111.111.13/32

R4 aggregates these into a single /24 advertisement upstream.

---

## Objectives

1. Configure three customer routers (R1, R2, R3) each in separate ASes advertising /32 loopbacks
2. Configure R4 as an ISP aggregating customer prefixes into a single /24 using a Null0 static route
3. Use an outbound prefix-list on R4 to advertise only the aggregate /24 to R5
4. Configure R5 with an inbound prefix-list to filter bogons and overly specific prefixes
5. Verify R5 receives only the clean /24 aggregate

---

## Router Table

| Router | AS | Role | Interfaces | Loopback | Notes |
|--------|------|------|------------|----------|-------|
| R1 | 10 | Customer | e0/0 (10.1.4.1/29) | 11.111.111.11/32 | Advertises /32 to R4 |
| R2 | 20 | Customer | e0/0 (10.1.4.9/29) | 11.111.111.12/32 | Advertises /32 to R4 |
| R3 | 30 | Customer | e0/0 (10.1.4.17/29) | 11.111.111.13/32 | Advertises /32 to R4 |
| R4 | 40 | ISP (Aggregator) | e0/0-2 (customers), e0/3 (11.1.1.1/30) | - | Aggregates /32s into /24, filters outbound |
| R5 | 50 | Upstream ISP | e0/0 (11.1.1.2/30) | - | Filters inbound, accepts only /24 and larger |

---

## Config Highlights

### Null Route Aggregation on R4

The core technique: create a static route pointing the aggregate prefix to Null0, then advertise it via BGP.

```
ip route 11.111.111.0 255.255.255.0 Null0

router bgp 40
 network 11.111.111.0 mask 255.255.255.0
```

**Why Null0?** BGP can only advertise a network that exists in the routing table. The individual /32s from customers exist, but the /24 aggregate does not unless you create it. The Null0 static route puts the /24 in the RIB so BGP can advertise it. Traffic matching the /24 but NOT matching a more specific /32 (like 11.111.111.50) gets dropped at Null0 - which is correct because no customer owns that address.

Think of it like a PO Box for a whole zip code. Mail for known addresses gets delivered to the right house. Mail for addresses that don't exist in that zip code gets thrown away at the post office (Null0) instead of bouncing around the network.

### Outbound Prefix-List on R4

```
ip prefix-list To-IIG-Out seq 5 permit 11.111.111.0/24

neighbor 11.1.1.2 prefix-list To-IIG-Out out
```

Only the /24 aggregate is permitted outbound. The three individual /32s from customers are implicitly denied. This keeps the upstream routing table clean - R5 sees one route instead of three.

### Inbound Prefix-List on R5 (ISP Hygiene Filter)

```
ip prefix-list From-ISP-IN seq 5 deny 0.0.0.0/0
ip prefix-list From-ISP-IN seq 10 deny 0.0.0.0/0 ge 25 le 32
ip prefix-list From-ISP-IN seq 15 permit 0.0.0.0/0 le 24
```

This is a real-world ISP inbound filter pattern:

| Sequence | Action | What It Matches | Why |
|----------|--------|----------------|-----|
| 5 | Deny | Exact default route (0.0.0.0/0) | Don't accept a default route from a downstream ISP |
| 10 | Deny | Any prefix /25 through /32 | Too specific - these are route leaks or hijack attempts |
| 15 | Permit | Any prefix /0 through /24 | Valid internet-sized prefixes |

The order matters. Seq 5 catches the exact default route before seq 15 could permit it (since 0.0.0.0/0 matches "le 24" too).

### /29 Subnets for Point-to-Point Links

Each customer link uses a /29 (255.255.255.248) giving 6 usable addresses per segment. This is common in ISP deployments where the link might later need a second router or a management device, making /30 too tight.

| Link | Network | Usable Range | Gateway (R4 side) |
|------|---------|-------------|-------------------|
| R1-R4 | 10.1.4.0/29 | 10.1.4.1 - 10.1.4.6 | 10.1.4.2 |
| R2-R4 | 10.1.4.8/29 | 10.1.4.9 - 10.1.4.14 | 10.1.4.10 |
| R3-R4 | 10.1.4.16/29 | 10.1.4.17 - 10.1.4.22 | 10.1.4.18 |

---

## Verification Commands

### 1. Verify BGP sessions are established

```
R4# show ip bgp summary
```

Expected: Four neighbors (R1, R2, R3, R5) all in Established state.

### 2. Verify R4 has all routes (individual + aggregate)

```
R4# show ip bgp
```

Expected:
- 11.111.111.0/24 via 0.0.0.0 (locally originated from Null0 route)
- 11.111.111.11/32 via 10.1.4.1 (from AS 10)
- 11.111.111.12/32 via 10.1.4.9 (from AS 20)
- 11.111.111.13/32 via 10.1.4.17 (from AS 30)

### 3. Verify R5 receives ONLY the aggregate /24

```
R5# show ip bgp
```

Expected: Only one route - `11.111.111.0/24` via 11.1.1.1, AS-PATH `40 i`. No /32s visible.

### 4. Verify prefix-list is filtering on R4

```
R4# show ip bgp neighbors 11.1.1.2 advertised-routes
```

Expected: Only 11.111.111.0/24 advertised to R5. Individual /32s should not appear.

### 5. Verify Null0 route exists

```
R4# show ip route static
```

Expected: `S 11.111.111.0/24 [1/0] is directly connected, Null0`

### 6. Verify customers see the aggregate and each other

```
R1# show ip bgp
```

Expected: R1 sees its own /32, plus the other two /32s via R4, plus the /24 aggregate from R4.

---

## Key Concepts

### Route Aggregation (Summarization)
Combining multiple specific prefixes into a single less-specific prefix. Reduces routing table size upstream and is considered best practice for ISPs. Without aggregation, the global internet routing table would be unmanageable.

### Null0 Route (Black Hole Route)
A static route pointing to the Null0 interface silently discards matching traffic. In aggregation, it serves two purposes:
1. Creates the aggregate prefix in the routing table so BGP can advertise it
2. Drops traffic for addresses within the aggregate range that have no more specific route (prevents routing loops)

### Prefix-List Filtering
Prefix-lists match on both the prefix AND the prefix length. The `ge` (greater than or equal) and `le` (less than or equal) modifiers let you match ranges of prefix lengths. This is more precise than access-lists for BGP route filtering.

### ISP Inbound Filtering
Real ISPs filter what they accept from peers and customers. Common filters include rejecting default routes, rejecting prefixes more specific than /24 (the minimum routable prefix on most of the internet), rejecting bogon prefixes (RFC1918, unallocated space), and rejecting prefixes not in the customer's registered allocation.

### Implicit Deny in Prefix-Lists
Like access-lists, prefix-lists end with an implicit deny. In R4's outbound prefix-list, only the /24 is explicitly permitted - everything else (the three /32s) is implicitly denied.

---

## Design Decisions

- **5-router star topology** - R4 as the hub with three customer spokes and one upstream link. Simplest topology to demonstrate ISP aggregation cleanly.
- **Separate AS per customer** - Realistic ISP scenario where each customer runs their own BGP autonomous system.
- **/29 subnets** - Practical ISP link sizing, more realistic than /30 for customer handoffs.
- **Loopbacks in the same /24 range** - All three customer loopbacks fall within 11.111.111.0/24, making aggregation natural and demonstrating proper address planning.
- **Dual prefix-list filtering** - Outbound on R4 AND inbound on R5 shows defense in depth. Even if R4's filter breaks, R5's filter catches the /32 leak.

---

## ENCOR Exam Relevance

| Topic | ENCOR Weight | What This Lab Covers |
|-------|-------------|---------------------|
| Route aggregation | 3.0 Infrastructure | Null0 static route to create aggregate prefix for BGP |
| Prefix-list filtering | 3.0 Infrastructure | Outbound and inbound prefix-lists with ge/le modifiers |
| BGP network design | 3.0 Infrastructure | ISP aggregation, customer peering, upstream filtering |
| Static routing | 3.0 Infrastructure | Null0 route for aggregation and black-hole traffic |
| BGP best practices | 3.0 Infrastructure | Filter specifics, advertise aggregates, defense in depth |

---

## Files

```
lab-15-bgp-route-aggregation/
  README.md
  week-15-journal.md
  configs/
    R1.txt
    R2.txt
    R3.txt
    R4.txt
    R5.txt
```
