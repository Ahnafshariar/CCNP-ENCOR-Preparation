# Lab 09 — Redistribution Filtering (Distribute-List, Route-Map, Prefix-List, Route Tags)

**ENCOR v1.2 mapping:** 3.0 Infrastructure — redistribution, route filtering, route-maps, prefix-lists
**Status:** ✅ Complete — verified working

## Objective

Redistribute routes between EIGRP and OSPF on an ASBR (R1), then practice **four different filtering tools** to control which routes cross the boundary. Each tool is an alternative approach to the same problem — only one is active at a time.

---

## The Four Redistribution Filtering Tools

### Tool 1 — Basic Redistribution (no filtering)

The starting point. Everything crosses the boundary unfiltered.

```
router ospf 100
 redistribute eigrp 100 metric 100 metric-type 2 subnets

router eigrp 100
 redistribute ospf 100 metric 1000 10 255 1 1500
```

**EIGRP metric format:** `metric <bandwidth> <delay> <reliability> <load> <MTU>`
- Bandwidth: 1000 (Kbps)
- Delay: 10 (tens of microseconds)
- Reliability: 255 (max, 255/255)
- Load: 1 (min, 1/255)
- MTU: 1500

Without an explicit metric, EIGRP redistribution fails silently (metric 0 = unreachable).

**OSPF `subnets` keyword:** without it, only classful boundaries are redistributed. A 20.20.1.2/32 route is silently dropped because 20.0.0.0 is Class A. Always include `subnets`.

---

### Tool 2 — Distribute-List (filter AFTER redistribution)

A distribute-list applies an ACL to routes that have **already been redistributed** into the routing protocol. It filters what gets **advertised**, not what gets imported.

```
access-list 10 permit 20.20.1.2 0.0.0.0
access-list 10 permit 20.20.3.2 0.0.0.0
access-list 10 permit 20.20.5.2 0.0.0.0
access-list 10 permit 20.20.7.2 0.0.0.0
! implicit deny any blocks all others

router ospf 100
 redistribute eigrp 100 metric 100 metric-type 2 subnets
 distribute-list 10 out
```

**Result:** R3 sees only 20.20.1.2, 20.20.3.2, 20.20.5.2, 20.20.7.2 (the odd-numbered loopbacks). Everything else is redistributed into OSPF internally but filtered before being advertised.

**When to use:** quick filtering when the redistribute statement is already in place and you don't want to change it.

---

### Tool 3 — Route-Map with ACL (filter DURING redistribution)

A route-map attached to the `redistribute` command filters routes **at the point of entry** — routes that don't match are never imported at all.

```
route-map EIGRP_TO_OSPF permit 10
 match ip address 10
route-map EIGRP_TO_OSPF permit 20
 ! catch-all: no match = normal routing for everything else

router ospf 100
 redistribute eigrp 100 route-map EIGRP_TO_OSPF subnets
```

**Result:** same filtering as Tool 2, but cleaner — unmatched routes never enter OSPF's database. The route-map can also `set` attributes (metric, metric-type, tag) per-route, which distribute-list cannot.

**When to use:** when you need per-route control (different metrics or tags for different prefixes), or when you want filtering at the source rather than at advertisement time.

---

### Tool 4 — Prefix-List (more powerful than ACL)

A prefix-list matches on **both the network address AND the prefix length**, which standard/extended ACLs cannot do.

```
ip prefix-list OSPF-TO-EIGRP seq 100 permit 10.0.0.0/8 le 24

route-map OSPF-TO-EIGRP permit 100
 match ip address prefix-list OSPF-TO-EIGRP
route-map OSPF-TO-EIGRP permit 110
 ! catch-all

router eigrp 100
 redistribute ospf 100 metric 1000 10 255 1 1500 route-map OSPF-TO-EIGRP
```

**What `10.0.0.0/8 le 24` means:** match any route that starts with 10.x.x.x AND has a prefix length between /8 and /24 (inclusive). A 10.10.1.0/24 matches (starts with 10, /24 is ≤24). A 10.10.1.1/32 does NOT match (/32 > 24).

**Prefix-list keywords:**
| Syntax | Matches |
|--------|---------|
| `permit 10.0.0.0/8` | Exactly 10.0.0.0/8 (only that one prefix) |
| `permit 10.0.0.0/8 le 24` | 10.x.x.x with mask /8 through /24 |
| `permit 10.0.0.0/8 ge 16` | 10.x.x.x with mask /16 through /32 |
| `permit 10.0.0.0/8 ge 16 le 24` | 10.x.x.x with mask /16 through /24 |
| `permit 0.0.0.0/0 le 32` | ANY route (the universal match) |

**When to use:** when filtering depends on prefix length (e.g., "only redistribute /24s or shorter, not host routes").

---

### Route Tags — Loop Prevention

Tags are numeric labels stamped on routes during redistribution. They travel with the route through the protocol and can be matched later to prevent loops.

**On R3 (tag the routes at the source):**
```
ip prefix-list Tag100 seq 100 permit 192.168.1.0/24
ip prefix-list Tag100 seq 101 permit 192.168.2.0/24
ip prefix-list Tag200 seq 100 permit 192.168.3.0/24

route-map ospf-tag permit 100
 match ip address prefix-list Tag100
 set tag 100
route-map ospf-tag permit 101
 match ip address prefix-list Tag200
 set tag 200

router ospf 100
 redistribute connected subnets route-map ospf-tag
```

**On R1 (filter by tag when redistributing OSPF into EIGRP):**
```
route-map XYZ permit 100
 match tag 200                    ! permit routes tagged 200
route-map XYZ deny 101
 match tag 100                    ! block routes tagged 100
route-map XYZ permit 110
                                  ! catch-all: pass untagged routes

router eigrp 100
 redistribute ospf 100 metric 1000 10 255 1 1500 route-map XYZ
```

**Result:** 192.168.3.0 (tag 200) enters EIGRP. 192.168.1.0 and 192.168.2.0 (tag 100) are blocked.

**When to use:** mutual redistribution with multiple ASBRs — tag routes at entry, filter by tag at exit, preventing routes from looping back into their source protocol.

---

## Tool Comparison

| | Distribute-List | Route-Map + ACL | Route-Map + Prefix-List | Route Tags |
|---|---|---|---|---|
| **Filters on** | Network address | Network address | Network + prefix length | Tag value |
| **When filtering happens** | After redistribution (at advertisement) | During redistribution (at import) | During redistribution | During redistribution |
| **Can set attributes** | No | Yes (metric, tag, etc.) | Yes | Yes |
| **Can match prefix length** | No | No (ACL limitation) | Yes | No |
| **Primary use** | Quick filter on existing redistribute | Per-route control | Length-aware filtering | Loop prevention |

---

## Topology

```
[R2] ── e0/0 ── 10.1.2.0/24 ── e0/0 ── [R1] ── e0/1 ── 10.1.3.0/24 ── e0/0 ── [R3]
EIGRP 100                               ASBR                              OSPF 100
8 loopbacks                         redistributes                    7 OSPF loopbacks
(20.20.x.2/32)                     both directions                 + prefix-list practice
                                                                   + tag practice (192.168.x)
```

## Addressing

| Device | Interface | IP | Protocol |
|--------|-----------|------|----------|
| R1 | e0/0 | 10.1.2.1/24 | EIGRP 100 |
| R1 | e0/1 | 10.1.3.1/24 | OSPF 100, area 0 |
| R2 | e0/0 | 10.1.2.2/24 | EIGRP 100 |
| R2 | Lo1-Lo7,Lo9 | 20.20.x.2/32 | EIGRP 100 |
| R3 | e0/0 | 10.1.3.3/24 | OSPF 100, area 0 |
| R3 | Lo1-Lo7 | 30.30.x.3/32 | OSPF 100 |
| R3 | Lo200-204,208 | 10.x.x.x (various) | OSPF 100 (prefix-list practice) |
| R3 | Lo205-207 | 192.168.x.1/24 | OSPF 100 (tag practice) |

---

## Verification

```
! 1. Before any filtering — see all redistributed routes
R3# show ip route ospf | include E2
! Should see ALL of R2's 20.20.x.2 loopbacks as O E2

R2# show ip route eigrp | include EX
! Should see R3's routes as D EX (EIGRP external)

! 2. After applying distribute-list or route-map — see filtered routes
R3# show ip route ospf | include E2
! Should see ONLY 20.20.1.2, 20.20.3.2, 20.20.5.2, 20.20.7.2

! 3. Verify tags
R1# show ip route ospf | include tag
! Should show tag 100 on 192.168.1.0, 192.168.2.0
! Should show tag 200 on 192.168.3.0

! 4. Prefix-list match
R1# show ip prefix-list OSPF-TO-EIGRP
! Shows the prefix-list definition and hit count
```

---

## Bugs Found During Build

| # | Router | Bug | Fix |
|---|--------|-----|-----|
| 1 | R1 | `metric 100 metric 1000` — duplicate keyword | Removed extra `metric 100` |
| 2 | R1 | Multiple redistribute statements overwriting each other | Organized as commented alternatives |
| 3 | R3 | Loopback 203 defined twice with different IPs | Second IP moved to Loopback 208 |
| 4 | R3 | Loopback 204 defined twice (same IP) | Removed duplicate |
| 5 | R3 | Lo205-207 missing `ip ospf 100 area 0` | Added (now intra-area, not external) |
| 6 | R3 | `match ip add` instead of `match ip address` | Fixed keyword |

---

## Key Takeaways

- **Only ONE `redistribute` per source is active.** A second command replaces the first. Use comments to switch between tools.
- **`distribute-list` filters after import; `route-map` filters at import.** Route-map is more powerful and the preferred approach.
- **ACLs match network address only. Prefix-lists match address AND mask.** If prefix length matters, use a prefix-list.
- **Route tags prevent redistribution loops.** Tag at the source ASBR, filter by tag at the destination ASBR.
- **EIGRP redistribution needs an explicit metric** (BW, delay, reliability, load, MTU) or it silently fails.
- **`subnets` keyword is mandatory** for OSPF redistribution of subnetted routes — without it, only classful boundaries are imported.
- **Every route-map needs a catch-all `permit` entry** at the end — otherwise unmatched routes are implicitly denied (not dropped from the network, but not policy-routed/redistributed).

Full device configs are in [`configs/`](configs/).
