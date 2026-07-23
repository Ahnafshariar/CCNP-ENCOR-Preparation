# Week 07 — Advanced OSPF: Multi-Area, Area Types, Virtual-Links, Redistribution

**Domain focus:** 3.0 Infrastructure — OSPF (advanced)
**Lab built:** [Lab 07 — Advanced OSPF](../../labs/lab-07-ospf-advanced/)
**Status:** ✅ Complete

## What I covered
- 11-router multi-area OSPF topology with 7 areas
- Three OSPF processes (10, 100, 900) with mutual redistribution
- Area types: stub (area 26), NSSA (area 35), totally stub (area 411)
- Virtual-link chaining: area 0 → area 48 → area 108
- DR/BDR election with explicit priorities on the backbone broadcast segment
- Loopback advertisement across areas (Lo100-102 on five routers)
- Multi-process OSPF redistribution at three points (R1, R4, R5)
- Route type identification: O, O IA, O E1/E2, O N1/N2

## Build order I followed
1. Backbone first (R1-R4 + switch) — verify area 0 adjacency
2. Non-backbone routers one by one — P2P links, verify each neighbor before next
3. Loopbacks — RID loopbacks + service loopbacks in OSPF
4. Virtual-links — R4↔R8 then R8↔R10
5. Multi-process redistribution — R1(10↔100), R5(10↔900), R4(10↔100)
6. Area types last — stub, NSSA, totally stub

## Bugs I found and fixed
- **SW1 empty config** — no L2 = no backbone OSPF. Always check the switch.
- **R8 router-id stale** — set `router-id 8.8.8.8` after OSPF was running, but RID was still 10.4.8.8. Virtual-link couldn't find 8.8.8.8. Fix: `clear ip ospf process`.
- **R8 missing virtual-link to R10** — after configuring VL with an existing network, clear ip ospf process is required to advertise the routing.
- **R11 process mismatch** — interface in OSPF 10 but stub flag under OSPF 100. E-bit mismatch killed adjacency.
- **R9 missing P2P network type** — mismatch with R5's point-to-point.
- **Connected routes don't appear as OSPF** — `show ip route ospf` on backbone routers was empty initially, which is correct behavior.

## Key takeaways
- **Build order matters.** Backbone first, verify adjacency, then extend. Don't configure area types until the basic topology works.
- **`clear ip ospf process` after changing router-id.** Virtual-links are especially sensitive — they match on exact RID.
- **Virtual-links are bidirectional.** Always configure both ends.
- **Process ID is local, area ID must match.** Process 10 and process 100 coexist on the same router but are separate OSPF domains.
- **Stub/NSSA flags break adjacency if mismatched.** Configure area types last, on all routers in the area simultaneously.

## Configs
Verified device configs: [`configs/`](configs/) — R1-R11, SW1.
