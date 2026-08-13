# Route Redistribution, Route-Maps, Prefix-Lists & Tags

*From my Class 15 (01 Aug 2026) and Class 16 (03 Aug 2026) notes. This is one of the heaviest ENCOR topics — route-maps especially are tested across redistribution, PBR, and BGP.*

---

## Why Redistribution Exists

One routing protocol doesn't automatically propagate routes to another. EIGRP knows its routes, OSPF knows its routes, but they don't talk to each other. An ASBR (the router running both protocols) has to manually bridge them with `redistribute`. Without it, R2's EIGRP loopbacks are invisible to R3's OSPF domain and vice versa.

---

## The Two Key Rules I Keep Forgetting

**1. EIGRP redistribution needs an explicit metric — or it silently fails.**
No metric = metric 0 = unreachable. The routes never appear in the EIGRP table, and there's no error message. The metric format is: `metric <bandwidth> <delay> <reliability> <load> <MTU>`.

**2. OSPF redistribution needs the `subnets` keyword — or subnetted routes are silently dropped.**
Without `subnets`, only classful boundaries get redistributed. A 20.20.1.2/32 route disappears because 20.0.0.0 is Class A, and /32 is a subnet of it. Again, no error message.

---

## The Two Tools (and which one to actually use)

From class, the instructor was very clear:

**Tool 1 — Distribute-list (uses ACL):** filters routes AFTER they've been redistributed. Works, but limited — never use in production. Can't set attributes, can't match prefix length. I learned it for the exam but won't use it in real life.

**Tool 2 — Route-map:** filters routes DURING redistribution. This is the one to use — always. It's the only way to truly control redistribution, and it's also used in PBR and BGP. The instructor said "CCNP = top → route map" — meaning route-maps are the top-level tool across the entire CCNP curriculum.

---

## Route-Map — The 3-Step Process

This is how I remember it:

```
Step 1: Create the ACL or prefix-list (the match criteria)
Step 2: Create the route-map (name is CASE SENSITIVE)
Step 3: Apply the route-map to the redistribute command
```

A route-map by itself does nothing. An ACL by itself does nothing. They only work when connected together and applied.

```
route-map <NAME> <permit|deny> <sequence-number>
 match ip address <ACL or prefix-list>
 set <attribute>                          ← optional, but important for BGP
```

- `permit` in a route-map = "match this traffic and apply the set action"
- `deny` in a route-map = "match this traffic and SKIP it (don't redistribute)"
- A route-map without a final `permit` catch-all implicitly denies everything unmatched

**The `set` keyword is especially important for BGP** — I'll need it heavily when I get to that topic. For redistribution, `set` is used for things like `set metric`, `set metric-type`, and `set tag`.

---

## Prefix-List — Why I Use It Over ACL

A standard ACL can only match on the network address. A prefix-list matches on **both the address AND the prefix length**. This is critical when I need to filter by subnet size.

**Example from class:**
```
Routes in the table:
  10.10.1.0/25
  10.10.1.128/25
  10.10.2.0/24
  10.10.3.0/24
  20.2.0.0/23
```

If I want only /24 or shorter from the 10.0.0.0 range:
```
ip prefix-list FILTER seq 100 permit 10.0.0.0/8 le 24
```
This matches 10.10.2.0/24 and 10.10.3.0/24 (both /24, which is ≤ 24).
It does NOT match 10.10.1.0/25 or 10.10.1.128/25 (/25 > 24).
It does NOT match 20.2.0.0/23 (doesn't start with 10).

An ACL can't do this — it would match all five routes if they start with 10, regardless of mask.

**Prefix-list keywords:**
| Syntax | What it matches |
|--------|----------------|
| `permit 10.0.0.0/8` | Exactly 10.0.0.0/8 (one route only) |
| `permit 10.0.0.0/8 le 24` | Any 10.x.x.x with mask /8 through /24 |
| `permit 10.0.0.0/8 ge 16` | Any 10.x.x.x with mask /16 through /32 |
| `permit 10.0.0.0/8 ge 16 le 24` | Any 10.x.x.x with mask /16 through /24 |
| `permit 0.0.0.0/0 le 32` | ANY route (universal match) |

**My homework was:** redistribute OSPF to EIGRP, but only subnets with mask /24 or less (i.e., /24 or shorter like /23, /16). The prefix-list `le 24` handles this perfectly.

---

## Route Tags — Loop Prevention

Tags are numeric labels I stamp on routes during redistribution. They travel with the route and can be matched later.

**Why they matter:** in mutual redistribution (EIGRP→OSPF and OSPF→EIGRP on the same ASBR), routes can loop back: a route enters OSPF from EIGRP, then gets redistributed BACK into EIGRP. Tags prevent this — I tag routes at entry, then deny that tag at the exit.

**From my class example:**
```
1.0/24  → TAG 100
2.0/24  → TAG 100
```

On the ASBR redistributing back, I deny tag 100 so those routes don't re-enter their source protocol.

**The config pattern:**
```
! Tag at the source
route-map TAG-ROUTES permit 10
 match ip address prefix-list MY-ROUTES
 set tag 100

! Filter at the other ASBR
route-map FILTER deny 10
 match tag 100               ← block anything tagged 100
route-map FILTER permit 20
                              ← pass everything else
```

---

## OSPF Loopback Behavior

From my notes: "In OSPF, loopback is considered as host IP by default — so configure as P2P to make it a network address."

What this means: OSPF always advertises loopbacks as /32 regardless of the configured mask. If I configure `ip address 10.10.1.1 255.255.255.0` on a loopback, OSPF still advertises it as 10.10.1.1/32. To advertise the actual /24 mask:

```
interface Loopback200
 ip ospf network point-to-point
```

This tells OSPF to treat the loopback like a regular interface and advertise the configured mask.

---

## IS-IS Note from Class

"Always Level 2 IS-IS used in Telco." This aligns with what I learned in Lab 08 — IS-IS Level-2 forms the backbone in service provider networks, and most ISP routers run as L2-only or L1-L2. The L1 areas are at the edges (customer-facing).

---

## Protocol Classification

| Protocol | Type | How it learns |
|----------|------|---------------|
| **EIGRP** | Distance vector (advanced) | Routing by rumor — learns from neighbors |
| **OSPF** | Link state | Builds a full map of the network, runs SPF |
| **IS-IS** | Link state | Same as OSPF (SPF/Dijkstra), but at Layer 2 |
| **BGP** | Path vector | Learns from peers, uses attributes for path selection |

---

## Quick Recall — Redistribution Checklist

```
Before redistributing, always check:
 ✅ EIGRP: explicit metric provided? (or it silently fails)
 ✅ OSPF: subnets keyword included? (or subnetted routes vanish)
 ✅ Route-map attached? (or everything crosses unfiltered)
 ✅ Route-map has a catch-all permit entry? (or unmatched = denied)
 ✅ Tags set for loop prevention? (if mutual redistribution)
 ✅ Prefix-list used where mask matters? (ACL can't match prefix length)
```
