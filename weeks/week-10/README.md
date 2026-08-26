# Week 10 — eBGP with Loopback Peering & Multihop

**Domain focus:** 3.0 Infrastructure — BGP fundamentals, eBGP peering
**Lab built:** [Lab 10 — eBGP with Loopback Peering](../../labs/lab-10-ebgp/)
**Status:** ✅ Complete

## What I covered
- eBGP peering via loopback addresses across a transit router
- `ebgp-multihop` (increase TTL for non-directly-connected peers)
- `update-source Loopback0` (stable BGP source address)
- Two route advertisement methods: `network` command vs `redistribute connected` with route-map
- BGP states: Idle, Active, OpenSent, OpenConfirm, Established
- BGP uses TCP port 179, triggered/incremental updates
- eBGP loop prevention via AS-PATH (reject routes containing own ASN)
- iBGP split-horizon rule and Route Reflector concept
- ISP context: multi-homing, MPLS/L3VPN, VPNv4, MP-BGP

## Bugs I found and fixed
- **R8 e0/1 mask /32** — broke OSPF adjacency to R10, BGP couldn't reach peer
- **R10 prefix-list mismatch** — `100.100.100.0/24` didn't match the connected route `100.100.100.100/32`
- **BGP stuck in Idle** — configured BGP before OSPF was working. Backoff timer got stuck on IOSv. Fix: `no router bgp` + rebuild. Lesson: always IGP first, verify ping, then BGP.

## Key takeaways
- **"If there is ping reachability, we can do eBGP"** — minimum condition from class. Everything else (multihop, update-source) is about making it work via loopbacks.
- **BGP "Active" state is bad** despite the name — it means trying but failing.
- **`network` command is safer than `redistribute`** for BGP — explicit control over what gets advertised.
- **Build order: IGP → verify ping → BGP.** Reversing this can cause stuck states that even `clear ip bgp *` doesn't fix.
- **eBGP prevents loops via AS-PATH.** iBGP prevents loops via split-horizon (needs full-mesh or RR).

## Configs
Verified device configs: [`configs/`](configs/) — R6, R8, R10.
