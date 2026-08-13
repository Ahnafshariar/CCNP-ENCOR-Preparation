# Week 09 — Redistribution Filtering (Distribute-List, Route-Map, Prefix-List, Tags)

**Domain focus:** 3.0 Infrastructure — redistribution, route filtering, route-maps, prefix-lists
**Lab built:** [Lab 09 — Redistribution Filtering](../../labs/lab-09-redistribution-filtering/)
**Status:** ✅ Complete

## What I covered
- EIGRP ↔ OSPF mutual redistribution on an ASBR
- Four filtering tools as alternatives (not stacked):
  - Tool 1: Basic redistribute (no filter)
  - Tool 2: Distribute-list (ACL-based, filters after import)
  - Tool 3: Route-map with ACL (filters during import)
  - Tool 4: Route-map with prefix-list (filters by address AND mask)
- Route tagging for loop prevention (tag at source, filter by tag at ASBR)
- Prefix-list syntax: `le` (less than or equal), `ge` (greater than or equal)
- EIGRP metric format: bandwidth, delay, reliability, load, MTU
- OSPF `subnets` keyword requirement

## Key takeaways / gotchas
- **Only one redistribute per source is active** — a second command overwrites the first silently. Organized as commented alternatives in the config.
- **`distribute-list` filters at advertisement; `route-map` filters at import** — route-map is more powerful and preferred.
- **ACL can't match prefix length** — use prefix-list when mask matters (e.g., "only /24 or shorter").
- **Forgetting `subnets` on OSPF redistribute** silently drops subnetted routes — no error message.
- **Forgetting EIGRP metric** silently fails redistribution — routes never appear.
- **`match ip add`** is not valid — full keyword is `match ip address`.
- **Duplicate loopback numbers** overwrite each other — IOS doesn't warn, just replaces the IP.

## Configs
Verified device configs: [`configs/`](configs/) — R1, R2, R3.
