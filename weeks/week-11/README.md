# Week 11 — iBGP with Dual Route Reflectors

**Domain focus:** 3.0 Infrastructure — iBGP, route reflector, peer-group
**Lab built:** [Lab 11 — iBGP with Dual Route Reflectors](../../labs/lab-11-ibgp-route-reflector/)
**Status:** ✅ Complete

## What I covered
- iBGP within AS 100: five routers, all peering via loopbacks over OSPF
- iBGP split-horizon rule: why full-mesh or RR is required
- Dual Route Reflectors (R4 + R5) for redundancy
- Peer-group config on R5 vs individual statements on R4
- BGP `network` command for route advertisement
- Why OSPF (or any IGP) is the foundation iBGP rides on

## Key takeaways / gotchas
- **`neighbour` is rejected by IOS** — must use American spelling `neighbor`. This bit me three times before I caught it. Use Tab-completion.
- **`route-reflector-client` is configured on the RR, not the client.** Clients don't know they're clients — their config is standard iBGP.
- **Peer-groups are cleaner** — R5's config is half the lines of R4 for the same result.
- **Dual RRs prevent single point of failure** — every client peers with both R4 and R5.
- **OSPF provides the reachability, BGP provides the routes.** They solve different problems at different scales. OSPF is the GPS inside the building; BGP is the postal system between buildings.

## Configs
Verified device configs: [`configs/`](configs/) — R1, R2, R3, R4 (RR), R5 (RR with peer-group).
