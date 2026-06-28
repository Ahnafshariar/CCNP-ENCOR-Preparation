# Week 04 — EIGRP, Policy-Based Routing & IP SLA Tracking

**Domain focus:** 3.0 Infrastructure — EIGRP, PBR, IP SLA, path control
**Lab built:** [Lab 04 — EIGRP + PBR + IP SLA](../../labs/lab-04-eigrp-pbr-ipsla/)
**Status:** ✅ Complete

## What I covered
- EIGRP configuration with AS number and exact network statements (wildcard 0.0.0.0)
- EIGRP bandwidth manipulation on interfaces
- Policy-Based Routing with multiple separate route-maps (one active at a time)
- PBR match conditions: ACL-based, packet length, tracked availability
- IP SLA probes (ICMP echo) with frequency and timeout tuning
- Track objects with asymmetric delay (fast down, slow up)
- `verify-availability` for intelligent PBR failover
- L2 switch vs router for shared-subnet hosts (overlapping subnet issue)

## Labs completed this week
- [x] Lab 04 — EIGRP + PBR + IP SLA

## Key takeaways / gotchas
- **Only one `ip policy route-map` per interface.** A second command replaces the first silently — does not stack. Use multiple entries (sequence numbers) inside one route-map to combine policies.
- **`match length` doesn't need an ACL.** It matches packet size directly.
- **IP SLA → Track → PBR is a three-layer chain.** Each layer does nothing alone.
- **`verify-availability` is the difference between dumb PBR and smart PBR.** Without it, PBR sends traffic into a dead path.
- **Router interfaces can't share a subnet.** R9 had to be an L2 switch because IOS rejects overlapping /24 assignments on different interfaces.
- **`permit` in an ACL used for PBR means "match this policy," not "allow the packet."** Traffic that doesn't match is NOT dropped — it falls to the next route-map entry.
- **`end` drops you out of config mode.** PBR commands (access-list, route-map, ip sla, track) are global config — need `conf t` before them.

## Configs
Verified device configs: [`configs/`](configs/) — R1, R2, R3, R4, R9, VPCs.
