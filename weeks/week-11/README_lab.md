# Lab 11 — iBGP with Dual Route Reflectors

**ENCOR v1.2 mapping:** 3.0 Infrastructure — iBGP, route reflector, peer-group, BGP split-horizon
**Status:** ✅ Complete — verified working

## Objective

Build an iBGP network within AS 100 using **two Route Reflectors** (R4 and R5) to solve the iBGP split-horizon problem. Prove that routes advertised by one client are reflected to all other clients without requiring full-mesh peering. Demonstrate **peer-groups** on all routers for cleaner configuration.

---

## The Problem Route Reflectors Solve

iBGP has a **split-horizon rule:** a route learned from an iBGP peer is NOT advertised to another iBGP peer. This prevents loops but creates a scaling problem:

```
Without RR (5 routers = 10 iBGP sessions needed):
  R1 <-> R2, R1 <-> R3, R1 <-> R4, R1 <-> R5
  R2 <-> R3, R2 <-> R4, R2 <-> R5
  R3 <-> R4, R3 <-> R5
  R4 <-> R5
  Formula: n(n-1)/2 = 5(4)/2 = 10 sessions

With RR (5 routers = 6 iBGP sessions):
  R1 -> R4 (RR), R1 -> R5 (RR)
  R2 -> R4,      R2 -> R5
  R3 -> R4,      R3 -> R5
  Clients only peer with RRs, not with each other.
```

### iBGP Route Propagation Solutions

| Solution | Real-world usage | How it works |
|----------|:----------------:|--------------|
| **Full mesh** | Rare (doesn't scale) | Every iBGP router peers with every other. n routers = n(n-1)/2 sessions. |
| **Route Reflector (RR)** | ~99.99% of deployments | RR reflects routes from clients to other clients. Clients only peer with the RR. |
| **Confederation** | Almost never used | Split AS into sub-ASes. Complex, legacy design. |

The RR **reflects** routes from one client to all other clients, bypassing the split-horizon rule. The clients don't even know they're talking to an RR — they just see iBGP routes appearing.

---

## IOU Topology

![Topology](Topology.png)

```
                     [ R4 ] RR #1 (PG4)
                   / |   \
                 /   |     \
               /     |       \
  [ R1 ] ----   [ R2 ]   [ R3 ] ---- [ R5 ] RR #2 (PG5)
    |    \      /    |         \    /    |
    |     \   /      |          \/      |
    |      \/        |          /\      |
    |      /\        |        /    \    |
    |    /    \      |      /        \  |
  (PG3)   (PG3) (PG3)  (PG3)    (PG3) (PG3)

  All in AS 100.  OSPF 100 area 0 for reachability.
  R1, R2, R3 = RR clients (peer with both R4 and R5 via PG3)
  R4 = RR #1 (reflects via PG4)
  R5 = RR #2 (reflects via PG5)
```

## Addressing

| Device | Interface | IP | Protocol | Purpose |
|--------|-----------|------|----------|---------|
| R1 | e0/0 | 10.1.4.1/24 | OSPF area 0 | To R4 |
| R1 | e0/1 | 10.1.5.1/24 | OSPF area 0 | To R5 |
| R1 | Lo0 | 1.1.1.1/32 | OSPF area 0 | BGP source |
| R1 | Lo100 | 192.168.1.1/32 | BGP only | Advertised into BGP |
| R1 | Lo101 | 192.168.11.1/32 | BGP only | Advertised into BGP |
| R2 | e0/0 | 10.2.5.2/24 | OSPF area 0 | To R5 |
| R2 | e0/1 | 10.2.4.2/24 | OSPF area 0 | To R4 |
| R2 | Lo0 | 2.2.2.2/32 | OSPF area 0 | BGP source |
| R2 | Lo100 | 192.168.2.1/32 | BGP only | Advertised into BGP |
| R3 | e0/2 | 10.3.4.3/24 | OSPF area 0 | To R4 |
| R3 | e0/3 | 10.3.5.3/24 | OSPF area 0 | To R5 |
| R3 | Lo0 | 3.3.3.3/32 | OSPF area 0 | BGP source |
| R3 | Lo100 | 192.168.3.1/32 | BGP only | Advertised into BGP |
| R4 | e0/0 | 10.1.4.4/24 | OSPF area 0 | To R1 |
| R4 | e0/1 | 10.2.4.4/24 | OSPF area 0 | To R2 |
| R4 | e0/2 | 10.3.4.4/24 | OSPF area 0 | To R3 |
| R4 | e0/3 | 10.4.5.4/24 | - | To R5 |
| R4 | Lo0 | 4.4.4.4/32 | OSPF area 0 | BGP source |
| R5 | e0/0 | 10.2.5.5/24 | OSPF area 0 | To R2 |
| R5 | e0/1 | 10.1.5.5/24 | OSPF area 0 | To R1 |
| R5 | e0/2 | 10.4.5.5/24 | - | To R4 |
| R5 | e0/3 | 10.3.5.5/24 | OSPF area 0 | To R3 |
| R5 | Lo0 | 5.5.5.5/32 | OSPF area 0 | BGP source |

**Design note:** Service loopbacks (Lo100, Lo101) are intentionally **NOT in OSPF**. This prevents RIB-failure (`r` flag) — OSPF (AD 110) would beat iBGP (AD 200) for the same prefix. By keeping them out of OSPF, BGP is the only protocol that carries these routes.

---

## Peer-Groups

All routers use peer-groups for cleaner config:

| Router | Peer-group | Members | Settings |
|--------|-----------|---------|----------|
| R1, R2, R3 | PG3 | R4 (4.4.4.4), R5 (5.5.5.5) | remote-as 100, update-source Lo0 |
| R4 | PG4 | R1, R2, R3 | remote-as 100, update-source Lo0, route-reflector-client |
| R5 | PG5 | R1, R2, R3 | remote-as 100, update-source Lo0, route-reflector-client |

BGP peer-groups remove repetitive neighbor entries. Define settings once in the group, assign neighbors to it. `route-reflector-client` is configured **on the RR only** (R4/R5). Clients (R1/R2/R3) have no idea they're RR clients.

---

## Verification

### 1. OSPF reachability (foundation for iBGP)
```
R1# ping 4.4.4.4 source 1.1.1.1
R1# ping 5.5.5.5 source 1.1.1.1
```
![OSPF ping to R4](image.png)

![OSPF ping to R5](image-1.png)

### 2. BGP sessions established
```
R4# show ip bgp summary
! 1.1.1.1, 2.2.2.2, 3.3.3.3 should all show Established (PfxRcd = number)
```
![R4 BGP summary](image-2.png)

```
R5# show ip bgp summary
! Same — all three clients Established
```
![R5 BGP summary](image-4.png)

### 3. Route reflection working (the key test)
```
R1# show ip bgp
! Should see:
!   192.168.1.1/32   (local, next-hop 0.0.0.0, weight 32768)
!   192.168.11.1/32  (local, next-hop 0.0.0.0, weight 32768)
!   192.168.2.1/32   (from R2, reflected by R4 and/or R5)
!   192.168.3.1/32   (from R3, reflected by R4 and/or R5)
```
![R1 BGP table](image-3.png)

### 4. Verify the route was reflected
```
R1# show ip bgp 192.168.2.1/32
! Originator: 2.2.2.2 (R2 originated it)
! Cluster-list: 4.4.4.4 (or 5.5.5.5) — proves RR reflected it
```

### 5. BGP routes in the routing table (no RIB-failure)
```
R1# show ip route bgp
! Should see B (BGP) routes for 192.168.2.1 and 192.168.3.1
! No 'r' flag because OSPF doesn't carry these prefixes
```

---

## The RIB-Failure Lesson

Initially, all BGP routes showed `r` (RIB-failure) in `show ip bgp`. Root cause: OSPF was configured with `network 0.0.0.0 0.0.0.0 area 0`, which caught every interface — including the service loopbacks that BGP was also advertising. OSPF (AD 110) always beats iBGP (AD 200) for the same prefix, so BGP could never install its routes.

**The fix:** switch OSPF to per-interface assignment (`ip ospf 100 area 0` on each interface), and keep service loopbacks (Lo100, Lo101) **out of OSPF entirely**. Now OSPF carries only infrastructure (physical links + peering loopbacks), and BGP carries service routes without competition.

```
OSPF = underlay (how routers reach each other internally)
BGP  = overlay (what routes to advertise externally)
They must NOT overlap on the same prefixes.
```

---

## show ip bgp Status Codes

| Code | Meaning |
|------|---------|
| `*` | Valid route |
| `>` | Best route (selected by BGP decision process) |
| `*>` | Valid AND best — installed in the RIB |
| `r` | RIB-failure — BGP selected it as best, but another protocol (lower AD) already owns this prefix |
| `i` | Learned via iBGP (internal) |

---

## Bugs Found During Build

| # | Router | Bug | Fix |
|---|--------|-----|-----|
| 1 | R5 (v1) | Loopback0 = 4.4.4.4 (duplicate of R4) | Changed to 5.5.5.5 |
| 2 | R4-R5 (v1) | Subnet mismatch (10.4.4.0 vs 10.4.5.0) | R4 e0/1 changed to 10.4.5.4 |
| 3 | R1/R2/R3 (v1-v2) | `neighbour` (British spelling) rejected by IOS | Changed to `neighbor` |
| 4 | R5 (v2) | Peer-group AND individual statements mixed | Use peer-group only |
| 5 | All (v3) | `network 0.0.0.0 0.0.0.0 area 0` caused RIB-failure | Switched to per-interface OSPF |
| 6 | R1 (v3) | `network 192.168.1.0 mask 255.255.255.0` didn't match /32 route | Changed to /32 mask |
| 7 | R2 (v4) | `mask 255.255.255.1` (invalid mask) | Changed to 255.255.255.255 |

---

## Key Takeaways

- **iBGP split-horizon:** routes learned from an iBGP peer are NOT forwarded to another iBGP peer. Without RR or full-mesh, routes are invisible between clients.
- **Route Reflector is the solution ~99.99% of the time.** Full-mesh doesn't scale. Confederation is almost never used.
- **`route-reflector-client` goes on the RR, not the client.** Clients have standard iBGP config — they don't know they're clients.
- **Dual RRs for redundancy** — every client peers with both. Single RR = single point of failure.
- **Peer-groups save config lines** — define settings once, apply to all members.
- **OSPF and BGP must not carry the same prefixes** — OSPF (AD 110) beats iBGP (AD 200), causing RIB-failure. Keep service loopbacks out of OSPF.
- **BGP `network` command must match the RIB exactly** — `network 192.168.1.1 mask 255.255.255.255` works with a /32 loopback. `network 192.168.1.0 mask 255.255.255.0` does not.
- **`neighbour` is rejected by IOS** — American spelling only. Use Tab-completion.
- **OSPF is the underlay, BGP is the overlay.** Neither replaces the other.

Full device configs are in [`configs/`](configs/).
