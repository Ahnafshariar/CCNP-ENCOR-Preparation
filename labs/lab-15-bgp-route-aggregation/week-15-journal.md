# Week 15 - BGP Route Aggregation with Null Route (5 Routers)

## Lab Summary

Built a 5-router ISP topology in EVE-NG to practice BGP route aggregation and prefix-list filtering. Three customer routers (R1, R2, R3) in separate ASes each advertise a /32 loopback. R4 acts as the ISP, aggregating those three /32s into a single /24 using a Null0 static route and advertising only the aggregate upstream. R5 (upstream ISP) applies its own inbound prefix-list to reject default routes and anything more specific than /24. Clean build with no bugs.

## What I Learned

- Null0 static route serves a dual purpose: creates the aggregate prefix in the RIB for BGP to advertise, and black-holes traffic for addresses within the aggregate that have no more specific route
- Prefix-lists match on both the prefix and the length, making them more precise than access-lists for BGP filtering
- The ge/le modifiers in prefix-lists define a range of prefix lengths to match - "deny 0.0.0.0/0 ge 25 le 32" blocks any prefix from /25 to /32 regardless of address
- Outbound filtering on R4 AND inbound filtering on R5 is defense in depth - standard practice in real ISP peering
- /29 subnets for point-to-point links give 6 usable addresses per segment, common in ISP customer handoffs

## ENCOR Topics Covered

- BGP route aggregation using Null0 static routes
- Prefix-list filtering with ge/le modifiers
- Outbound and inbound BGP route filtering
- ISP peering best practices
- BGP network statement with aggregate prefixes
- Static routing to Null0 (black hole routing)

## Connection to Previous Labs

- Lab 13 (Communities + Local Preference): controlled path selection from the receiver side using inbound route-maps
- Lab 14 (AS-PATH Prepend): controlled path selection from the sender side using outbound route-maps
- Lab 15 (Aggregation + Filtering): controlled what routes are visible at all using prefix-lists - a different kind of traffic engineering that focuses on route visibility rather than path preference

All three labs deal with BGP policy, but each at a different level: Lab 13 and 14 control WHICH path traffic takes, Lab 15 controls WHETHER a route is visible in the first place.

## Next Steps

- Practice BGP weight attribute (highest priority in path selection, local to router)
- Practice MED (Multi-Exit Discriminator) for same-AS multi-homing
- Combine aggregation with communities for scalable ISP policy
