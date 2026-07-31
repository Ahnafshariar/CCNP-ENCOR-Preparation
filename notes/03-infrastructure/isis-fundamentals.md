# IS-IS — Intermediate System to Intermediate System

*From my Class 14 notes (27 Jul 2026). IS-IS is not on the CCNP ENCOR exam but is essential for ISP/SP roles and deepens my understanding of link-state protocols.*

---

## What IS-IS Is

IS-IS is a link-state routing protocol like OSPF — both use the SPF (Dijkstra) algorithm to calculate shortest paths. The key difference: IS-IS runs at **Layer 2** (directly over the data link using CLNS), while OSPF runs at **Layer 3** (over IP). This means IS-IS can form neighbor relationships without matching IP subnets — something OSPF cannot do.

IS-IS supports both IPv4 and IPv6 in a **single process** (unlike OSPF which needs OSPFv2 for IPv4 and OSPFv3 for IPv6 as separate processes). This is one reason IS-IS is preferred in ISP networks — one protocol, dual-stack.

IS-IS is also the primary protocol for **Segment Routing (SR)** deployments in service provider and data center networks.

---

## Terminology

- **IS** = Intermediate System = Router
- **ES** = End System = End device (PC, server)
- **B** = Backbone = Level-2 + Level-1-2 routers (no "area 0" concept like OSPF)
- **R** = Regular area = Level-1 routers

---

## Level System (How IS-IS Does Areas)

IS-IS doesn't use numbered areas like OSPF. Instead, it uses **levels:**

| Level | Role | OSPF equivalent |
|-------|------|----------------|
| **Level-1 (L1)** | Intra-area only. Knows only local area routes. Gets a default route from the L1-L2 router for everything else. | Internal router |
| **Level-2 (L2)** | Backbone only. Carries inter-area routes between L1-L2 routers. | Backbone router |
| **Level-1-2 (L1-L2)** | Both. Bridges its L1 area to the L2 backbone. This is the **default** on Cisco routers. | ABR |

**Key rules I noted:**
- L1 routers connect to L1 (same level only)
- L2 and L1-L2 routers connect to L1 AND L2
- L2 + L1-L2 routers together form the **backbone** (no area 0 needed)
- The backbone area will never be any area type (stub, NSSA, etc.) — it's always the backbone

---

## IS-IS Adjacency Requirements

From my class notes, IS-IS adjacency needs:

1. **IS-IS enabled** on both routers (`router isis` + `ip router isis` on the interface)
2. **Interfaces in the same area** — for Level-1 adjacency, both routers must share the same area (same AFI+Area in the NET address). Level-2 adjacency can be between different areas.
3. **Matching level** — L1↔L1, L2↔L2, or L1-L2↔either. An L1-only router and an L2-only router will never form adjacency.
4. **Unique System ID** — duplicates corrupt the LSDB
5. **Hello and Dead timers must match** — same as OSPF
6. **Authentication must match** (if configured)
7. **MTU must match** — IS-IS is sensitive to this
8. **Subnet match is NOT required** — this is a major difference from OSPF. IS-IS runs at Layer 2, so the adjacency forms at the data-link layer regardless of IP addressing. However, IP routing still needs matching subnets to actually forward traffic.

---

## NET Address (Network Entity Title)

Every IS-IS router identifies itself with a NET address instead of a router-id:

```
49.0200.0000.0000.1111.00
```

Breaking it down (2 hex digits = 1 byte):

| Field | Value | Bytes | Meaning |
|-------|-------|:-----:|---------|
| **AFI** | `49` | 1 | Authority & Format Identifier. 49 = private use (In old convention, now it is not followed anymore). No deeper significance — I just used 49. |
| **Area** | `0200` | 2 | Area identifier. All routers in the same L1 area share this. Can be 1–13 bytes, but I use 2 bytes. |
| **System ID** | `0000.0000.1111` | 6 | Unique per router. Always exactly 6 bytes. I derive mine from the router number (R1 = 1111, R2 = 2222). |
| **NSEL** | `00` | 1 | N-Selector. Always `00` for a router (IS). Anything else = end system (ES). I keep it 00 for protocols. |

**Converting a loopback IP to System ID** (the standard method):
```
Loopback: 192.168.2.10
Step 1: Pad octets to 3 digits → 192.168.020.010
Step 2: Remove dots → 192168020010
Step 3: Regroup by 4 → 1921.6802.0010
Result: System ID = 1921.6802.0010
```

---

## IS-IS Path Selection

IS-IS uses **metric** for path selection, but unlike OSPF which derives cost from bandwidth, IS-IS defaults to **metric 10 on every interface** regardless of bandwidth. This means a 100Mbps link and a 10Gbps link have the same cost by default.

For real-world deployments, I need to use **wide metrics** (`metric-style wide` under `router isis`) and manually set interface metrics, or configure IS-IS to derive metrics from bandwidth like OSPF does.

---

## `is-type` vs `isis circuit-type` — What I Learned the Hard Way

`is-type` (under `router isis`) sets the **router-level ceiling** — what the router is capable of.

`isis circuit-type` (under the interface) restricts a **single interface** — but can never exceed the ceiling.

I made this mistake twice:
1. First I set R1 to `is-type level-1` but needed L2 on e0/0 → ceiling was too low, L2 adjacency failed
2. Then I overcorrected to `is-type level-2-only` → couldn't form L1 with R2/R3

The fix: remove `is-type` entirely (defaults to L1-L2), and use `circuit-type` per interface to control which adjacency forms where. The ceiling stays high, and each interface is selectively restricted.

---

## Quick Recall

```
IS-IS                          OSPF
─────                          ────
Layer 2 (CLNS)                 Layer 3 (IP)
Area = per router (NET)        Area = per interface
L1 = internal router           = internal router
L2 = backbone                  = area 0
L1-L2 = ABR (default!)         = ABR
No area 0 needed               Area 0 mandatory
No subnet match for adjacency  Subnet must match
Single process: IPv4 + IPv6    Two processes: v2 + v3
Metric default: 10 on all      Metric: ref BW / int BW
```
