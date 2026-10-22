# Week 13 - BGP Communities + Local Preference (6 Routers)

## Lab Summary

Built a 6-router topology in EVE-NG to practice BGP community tagging and local-preference-based path selection. R5 (AS 500) tags four loopback prefixes with two communities (1:1 and 2:2) using access-lists and route-maps. R1 (AS 100) and R4 (AS 400) each receive two paths to R5's prefixes and use inbound route-maps to set local-preference based on community values, steering traffic to different paths per community group.

## What I Learned

- Communities are stripped by default at eBGP boundaries - send-community both must be on every neighbor in the chain or the tags disappear
- Local preference is applied on the receiver via inbound route-maps, not configured on the sender
- The "set" keyword is required before local-preference in a route-map - without it IOS silently ignores the command
- A ring topology cannot deliver two usable BGP paths because BGP only advertises the best path and the shorter path always wins at intermediate routers
- ip community-list matches community values (1:1), access-list matches IP prefixes (5.5.5.0/24) - they solve different problems
- Route-maps need a catch-all empty permit at the end or unmatched routes get implicitly denied
- ip bgp-community new-format changes display from a single 32-bit number to the AS:Value format (1:1 instead of 65537)

## Bugs Fixed

1. R4 route-map had "local-preference 200" instead of "set local-preference 200" - silently ignored
2. R5 neighbor statement pointed to its own IP (10.1.5.5) instead of R1 (10.1.5.1)
3. R4 had remote-as 200 for R3 after R3 was changed to AS 300 - "peer in wrong AS" error
4. Ring topology could not deliver second path to R1/R4 - solved by adding direct R1-R4 eBGP link
5. IOUweb cable mapping bug on R1-R5 link - migrated to EVE-NG

## ENCOR Topics Covered

- BGP community tagging and propagation
- Local preference for path selection
- Route-map match/set logic with community-lists
- BGP best-path selection process (local-pref beats AS-PATH length)
- BGP best-path-only advertisement limitation
- send-community behavior across eBGP

## Next Steps

- Add AS-PATH prepend to this topology for additional path manipulation practice
- Practice weight attribute (local to router, highest priority in path selection)
- Package and push to GitHub
