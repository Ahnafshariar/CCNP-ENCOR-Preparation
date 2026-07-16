# Week 06 — Multi-Area OSPF

**Domain focus:** 3.0 Infrastructure — OSPF multi-area, adjacency rules, DR/BDR, ABR, LSAs
**Lab built:** [Lab 06 — Multi-Area OSPF](../../labs/lab-06-ospf-multi-area/)
**Status:** ✅ Complete

## What I covered
- Multi-area OSPF design: backbone (area 0) + two non-backbone areas (245, 367)
- ABR role: R2 (area 0 + 245), R3 (area 0 + 367)
- The 8 OSPF adjacency requirements (RID, subnet, area, MTU, flags, timers, auth, network type)
- Two OSPF interface assignment methods (`network` command vs `ip ospf` on interface) — used both in the same lab
- DR/BDR election: priority, RID tie-breaker, non-preemptive behavior
- Router ID selection order: manual > loopback > physical
- OSPF network type `point-to-point` to skip DR election
- Loopback advertisement in OSPF (always /32 unless point-to-point network type)
- OSPF multicast addresses: 224.0.0.5 (AllSPFRouters), 224.0.0.6 (AllDRouters)
- Multicast MAC mapping: 01:00:5E:00:00:05 and 01:00:5E:00:00:06
- Inter-area route identification (`O IA` in routing table = Type 3 Summary LSA)

## Verification I ran
- `show ip ospf neighbor` — all adjacencies FULL
- `show ip ospf` — confirmed ABR status on R2 and R3
- `show ip route ospf` on R4 — saw O IA routes from area 0 and area 367
- `show ip ospf database` — Type 1 (Router), Type 2 (Network), Type 3 (Summary) LSAs
- `show ip ospf interface e0/0` — confirmed timers, network type, DR/BDR, area

## Key takeaways / gotchas
- **Process ID doesn't matter for adjacency** — only area ID must match. This is different from EIGRP where the AS number must match.
- **Stuck in INIT = parameter mismatch** (area, timers, auth, network type). Stuck in EXSTART = MTU mismatch.
- **DR election is non-preemptive** — adding a higher-priority router doesn't change the existing DR until it fails.
- **Loopbacks always advertise as /32** in OSPF. Use `ip ospf network point-to-point` on the loopback to advertise the configured mask instead.
- **Both `network` command and `ip ospf` on the interface work** — can mix them on the same router (R2 does this).
- **OSPF multicast is link-local (TTL=1)** — Hello packets never cross a router.

## Configs
Verified device configs: [`configs/`](configs/) — R1, R2, R3, R4, R5, R6, R7.
