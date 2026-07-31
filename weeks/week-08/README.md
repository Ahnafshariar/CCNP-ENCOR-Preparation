# Week 08 — IS-IS (Intermediate System to Intermediate System)

**Domain focus:** ⚠️ Out of ENCOR syllabus — built for deeper link-state understanding and ISP/SP interview prep
**Lab built:** [Lab 08 — IS-IS](../../labs/lab-08-isis/)
**Status:** ✅ Complete

## What I covered
- IS-IS Level system: L1 (intra-area), L2 (backbone), L1-L2 (ABR equivalent, default)
- NET address structure: AFI (49), Area, System ID (6 bytes), NSEL (00)
- `is-type` (router ceiling) vs `isis circuit-type` (per-interface restriction)
- IS-IS adjacency requirements — subnet match NOT required (Layer 2 protocol)
- IS-IS vs OSPF comparison: area assignment, metric, dual-stack, segment routing
- Two-area topology bridged by L1-L2 routers through an L2 backbone

## Bugs I found and fixed
- **R1 `is-type` wrong twice:** first L1-only (couldn't do L2 to R7), then L2-only (couldn't do L1 to R2/R3). Fix: remove `is-type`, let it default to L1-L2.
- **R6 duplicate System ID** (copied R5's NET). Fix: unique System ID per router.
- **R1↔R7 and R4↔R7 subnet mismatches** (octets transposed: 1.7 vs 7.1).
- **R4 duplicate IP** on e0/0 and e0/1 (both 10.4.6.4). Fix: e0/0 = 10.4.7.4 (to R7).
- **R6 Lo102 mask typo** (255.255.255.25A5). Fix: /32.

## Key takeaways
- **`is-type` = ceiling, `circuit-type` = restriction.** Interface can't exceed the router's capability. Learned this through two failed attempts.
- **IS-IS runs at Layer 2** — adjacency doesn't need matching subnets (fundamentally different from OSPF).
- **L1-L2 is the default and the safest** — it can form adjacencies with everything. Only restrict with `is-type` when you have a specific reason.
- **Duplicate System IDs are silent killers** — same as OSPF Router ID duplication but potentially worse because the LSDB corruption is harder to diagnose.
- **IS-IS is not on ENCOR** but understanding it made my OSPF knowledge sharper — both use SPF, but seeing the design differences (per-router vs per-interface areas, L2 vs L3 protocol) clarified why OSPF works the way it does.

## Configs
Verified device configs: [`configs/`](configs/) — R1, R2, R3, R4, R5, R6, R7.
