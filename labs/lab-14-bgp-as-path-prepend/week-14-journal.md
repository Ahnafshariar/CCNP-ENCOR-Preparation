# Week 14 - BGP AS-PATH Prepend (4 Routers)

## Lab Summary

Built a 4-router dual-homed topology in EVE-NG to practice AS-PATH prepend for inbound traffic engineering. R4 (AS 400) is dual-homed to two ISPs - R2 (AS 200) and R3 (AS 300). R1 (AS 100) sits behind both ISPs as the observer. R4 uses selective outbound route-maps to prepend its own AS three times on specific prefixes per neighbor, steering YouTube traffic through ISP-A (R2) and Gaming traffic through ISP-B (R3).

## What I Learned

- AS-PATH prepend controls inbound traffic by manipulating outbound advertisements - you change the signs on the road, not the cars
- You must always prepend your own AS number - prepending another AS triggers BGP loop detection and the route gets rejected entirely
- Route-map sequence order matters - IOS evaluates in numerical order, so the specific match must come before the catch-all or the catch-all matches everything first
- Selective prepending uses access-lists to identify which prefixes to pad and which to pass clean, applied per neighbor
- In a diamond topology, the second path disappears after convergence because the transit router learns a shorter path back from R1 - same best-path-only limitation from Lab 13
- Three prepends is the practical sweet spot - more than three rarely helps and can trigger upstream route filtering

## Bugs Fixed

1. Used `set as-path prepend 100 100 100` instead of `400 400 400` - prepending the wrong AS causes loop detection rejection
2. Route-map sequence numbers reversed - catch-all (permit 10) ran before the match (permit 20), so prepend never applied

## ENCOR Topics Covered

- AS-PATH prepend for inbound traffic engineering
- Outbound route-map application for path manipulation
- BGP best-path selection (AS-PATH length comparison)
- Route-map sequence ordering and implicit deny
- Access-list based prefix matching in BGP policy
- Dual-homing and multi-homing concepts

## Connection to Lab 13

Lab 13 used communities and local preference to control path selection from the receiver side (inbound route-maps). Lab 14 uses AS-PATH prepend to control path selection from the sender side (outbound route-maps). Together they cover both directions of BGP traffic engineering:
- Local preference = control where YOU send traffic (inbound route processing)
- AS-PATH prepend = control how traffic reaches YOU (outbound advertisement manipulation)

## Next Steps

- Practice BGP weight attribute (highest priority in path selection, local to router)
- Combine prepend with communities for full traffic engineering toolkit
- Practice MED (Multi-Exit Discriminator) for same-AS multi-homing
