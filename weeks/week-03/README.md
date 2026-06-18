# Week 03 — Static Routing & Path Control

**Domain focus:** 3.0 Infrastructure → Layer 3 static routing, path selection
**Lab built:** [Lab 03 — Static Routing with Path Control](../../labs/lab-03-static-routing/)
**Status:** ✅ Complete

## What I covered
- Static routes with both interface and next-hop specified
- /30 point-to-point link addressing
- Two parallel paths through a four-router topology
- Path control: forcing traffic through a specific path using selective static routes
- Floating static routes (AD manipulation) as the clean approach for primary/backup

## Topology
Four routers (R1–R4), two end hosts (VPC5, VPC6). Two paths: bottom via 10.1.1.x (R2→R3→R4), top via 20.1.1.x (R2→R1→R4).

## Verification I ran
- `show ip route static` on each router — confirmed correct next-hops per task
- `trace 192.168.20.100` from VPC5 — hop IPs proved which path was taken (10.x or 20.x)
- Ping both directions confirmed reachability

## Key takeaways / gotchas
- **The big debug:** R4's static routes had the interface and next-hop swapped (e0/0 paired with a 20.x next-hop, e0/1 with a 10.x next-hop). Silent failure — no error, just unreachable. Caught by checking the interface-to-subnet mapping against the route table.
- Two static routes to the same prefix with the same AD = ECMP, not primary/backup.
- A floating static route (higher AD) stays in config but only enters the RIB when the preferred route disappears.
- R3 only needs 10.x path routes — it has no connection to R1.

## Configs
Verified device configs: [`configs/`](configs/) — R1, R2, R3, R4, VPCs.
