# BGP — Border Gateway Protocol Fundamentals

*From my Class 17 notes (8 Aug 2026) and study material. BGP is a critical ENCOR topic — the protocol that runs the internet.*

---

## What BGP Is (and Isn't)

BGP is NOT an IGP. It's the **only EGP (Exterior Gateway Protocol)** in use. While OSPF and EIGRP route traffic within my network (autonomous system), BGP routes traffic **between** autonomous systems — between ISPs, between enterprises and their ISPs, between data centers.

BGP is a **path vector protocol** — it doesn't use metrics like cost (OSPF) or bandwidth/delay (EIGRP). Instead, it uses **attributes** (AS-PATH, local preference, MED, etc.) to select the best path. It's the most complex routing protocol and the slowest to converge — by design, because stability matters more than speed at internet scale.

---

## ASN (Autonomous System Number) Ranges

ASNs are assigned by IANA. Originally 16-bit (0-65,535), expanded to 32-bit via RFC 4893 to handle global growth.

**16-bit range (0-65,535):**

| Range | Use |
|-------|-----|
| 0 | Reserved |
| 1 - 64,495 | **Public Internet** (assigned by IANA/RIRs) |
| 23,456 | 32-bit transition (reserved) |
| 64,496 - 64,511 | Documentation |
| **64,512 - 65,534** | **Private use** (like RFC1918 for IPs — used in labs and internal iBGP) |
| 65,535 | Reserved |

**32-bit range (65,536-4,294,967,295):**

| Range | Use |
|-------|-----|
| 65,536 - 65,551 | Documentation |
| 65,552 - 131,071 | IANA Reserved |
| 131,072 - 4,199,999,999 | **Public Internet** |
| 4,200,000,000 - 4,294,967,294 | **Private use** |
| 4,294,967,295 | Reserved |

For my labs, I use numbers like 600, 1000 — these fall in the public range, which is fine for lab purposes. In production, I'd use private ASNs (64512-65534) for internal BGP or get a public ASN from an RIR (like ARIN for North America).

---

## BGP Message Types — The 4 Messages

Every BGP message uses a **19-byte common header.** There are only four message types, and each has a specific job:

| Type | Name | Function | Mnemonic | Key fields |
|:----:|------|----------|----------|------------|
| 1 | **OPEN** | Establishes session parameters | "Who are you?" | BGP Version (4), ASN, Hold Time (180s), BGP Identifier (Router ID) |
| 2 | **UPDATE** | Advertises and withdraws routes | "Here are my routes" | NLRI (prefixes), Path Attributes (AS-PATH, next-hop, etc.) |
| 3 | **NOTIFICATION** | Reports fatal errors, terminates session | "Closing session" | Error Code, Error Subcode |
| 4 | **KEEPALIVE** | Maintains session (heartbeat) | "Still there?" | Header only (no payload — smallest BGP message) |

**The lifecycle is strictly sequential:** TCP Handshake → OPEN → KEEPALIVE → UPDATE.

---

## The 7 Rules of BGP Messages

1. BGP runs exclusively over **TCP port 179**
2. Every BGP message uses a uniform **19-byte common header**
3. **OPEN** establishes the BGP relationship parameters
4. **KEEPALIVE** maintains the session via periodic heartbeats
5. **UPDATE** is the sole vehicle for both route advertisements and withdrawals
6. **NOTIFICATION** reports fatal errors and forces session termination
7. The BGP lifecycle is strictly sequential: **TCP Handshake → OPEN → KEEPALIVE → UPDATE**

---

## BGP Session Establishment — 3 Phases

```
Router A                                    Router B
    |                                           |
    |--- Phase 1: TCP 3-way handshake ---------|
    |          SYN ---------------------->      |
    |      <---------------------- SYN-ACK      |   TCP connection is
    |          ACK ---------------------->      |   established first.
    |                                           |
    |--- Phase 2: OPEN exchange ---------------|
    |         OPEN ---------------------->      |
    |      <---------------------- OPEN         |
    |    (exchange: version, ASN, hold time,    |
    |     BGP identifier/router-id)             |
    |                                           |
    |--- Phase 3: KEEPALIVE exchange ----------|
    |     KEEPALIVE --------------------->      |
    |      <--------------------- KEEPALIVE     |
    |                                           |
    |        [ State: ESTABLISHED ]             |
```

A successful OPEN exchange must be followed by KEEPALIVE to enter the Established state. Only after Established do UPDATE messages (route advertisements) begin flowing.

---

## BGP Finite-State Machine (FSM)

Every BGP session progresses through these states in order:

```
Idle --> Connect --> Active --> OpenSent --> OpenConfirm --> Established
  ^                                                              |
  +-------------- (session drops, restart) ----------------------+
```

| State | What's happening | Stuck here? Check... |
|-------|-----------------|---------------------|
| **Idle** | Not attempting TCP. Waiting for start event or backoff timer. | Peer IP unreachable, wrong neighbor config, stuck timer |
| **Connect** | Attempting TCP connection (SYN sent) | Firewall blocking TCP 179, peer not listening |
| **Active** | TCP failed, retrying. "Actively trying but unable to connect." | Peer reachable but BGP not configured there, wrong AS, ACL |
| **OpenSent** | TCP connected, OPEN sent, waiting for peer's OPEN | AS mismatch, version mismatch |
| **OpenConfirm** | Both OPENs exchanged, waiting for KEEPALIVE | Hold time negotiation issue |
| **Established** | Session up, exchanging routes. PfxRcd shows a number. | Working! |

**The fork in the road — Connect vs Active:**

The progression relies entirely on the underlying TCP connection. From Connect state:
- **Path A (TCP successful):** proceeds forward to send OPEN → OpenSent
- **Path B (TCP unsuccessful):** falls to Active state, where BGP actively attempts to initiate a TCP connection. If Active also fails, the ConnectRetry timer expires and it loops back to Connect.

**Key takeaway:** "Active" is the bad state despite the positive name. It means BGP is actively retrying and failing. If I see "Active" in `show ip bgp summary`, the peer is reachable at IP level but something is blocking BGP (wrong AS, firewall, no BGP config on the other side).

---

## BGP Keepalive & Hold Timer — The Heartbeat

BGP does not assume a connection remains healthy. It actively monitors the peer:

**Keepalive interval: 60 seconds** (default). A keepalive is sent every 60 seconds to tell the peer "I'm still here."

**Hold time: 180 seconds** (default). If no valid BGP message (keepalive OR update) is received within 180 seconds, the peer is declared dead and the session is torn down.

```
Timeline:
  0s ---- KEEPALIVE ---- 60s ---- KEEPALIVE ---- 120s ---- KEEPALIVE ---- 180s
                                                                           !
                                                               Hold-Time Exceeded
                                                               Peer declared dead
```

The math: hold time (180s) = 3 x keepalive interval (60s). So missing **three consecutive keepalives** means the peer is dead. UPDATE messages also reset the hold timer — any valid BGP message counts.

The hold time is **negotiated** during OPEN exchange — both sides propose their hold time, and the **lower value wins.** If one side proposes 180s and the other 90s, both use 90s.

---

## Key Concepts from Class

**BGP uses TCP port 179** to communicate. Unlike OSPF (multicast 224.0.0.5) or EIGRP (multicast 224.0.0.10), BGP forms a TCP session between peers. This means: if there's ping reachability, I can do eBGP.

**BGP uses triggered and incremental updates** — it only sends changes when something actually changes, not periodic full-table dumps. This is critical at internet scale where the full table is 900,000+ routes.

**3 upstream connections → BGP:** when an enterprise connects to multiple ISPs, it needs BGP to receive routes from all of them and make intelligent path selection decisions. Single ISP = default route is fine. Multiple ISPs = BGP is the only way.

---

## eBGP vs iBGP

| | eBGP | iBGP |
|---|---|---|
| **Between** | Different ASNs | Same ASN |
| **TTL** | 1 (default) | 255 |
| **AS-PATH** | Prepends own ASN | Does not modify AS-PATH |
| **Next-hop** | Changes to self | Does NOT change (common gotcha) |
| **Full mesh needed?** | No | Yes (or use Route Reflector) |
| **Private AS** | No | Can use private ASN |

**iBGP split-horizon rule:** a route learned from an iBGP peer is NOT advertised to another iBGP peer. This prevents loops inside the AS but means iBGP requires either full-mesh peering or a **Route Reflector (RR)** to distribute routes.

---

## eBGP Loop Prevention

eBGP prevents loops using the **AS-PATH attribute.** When a route passes through an AS, that AS number is prepended to the path. If a router receives a route with its OWN ASN in the path, it **rejects it** — the route has already been through this AS.

```
AS 100 (XYZ ISP) -- AS 200 (IIG) -- AS 300 (TATA) -- AS 400 (META)

Route originates from AS 400:
  AS 400 advertises to AS 300: AS-PATH = {400}
  AS 300 advertises to AS 200: AS-PATH = {300, 400}
  AS 200 advertises to AS 100: AS-PATH = {200, 300, 400}
  
If this route somehow loops back to AS 300:
  AS 300 sees its own ASN (300) in the path --> REJECTED. Loop prevented.
```

---

## eBGP Minimum Requirements

From my notes: "if there is ping reachability, then I can do eBGP." The minimum config:

```
router bgp <my-ASN>
 neighbor <peer-IP> remote-as <peer-ASN>
```

For **loopback peering** (across transit routers), two more commands:
```
 neighbor <peer-IP> ebgp-multihop <hops>     <- increase TTL (default is 1)
 neighbor <peer-IP> update-source Loopback0  <- source from stable loopback
```

---

## ISP/SP Context from Class

**MPLS > L3VPN:** service providers use MPLS with BGP to deliver L3VPN services. The building blocks:
- **VRF** with **Route Distinguisher (RD):** makes overlapping customer routes unique
- **VPNv4 routes:** 32-bit IPv4 prefix + 64-bit RD = 96-bit globally unique address
- **MP-BGP (Multiprotocol BGP):** carries VPNv4 routes between PE routers over iBGP

This connects back to my VRF lab (Lab 05) — VRF Lite is the customer-facing piece, while MPLS/MP-BGP is the provider backbone that connects VRF instances across the WAN.

---

## Quick Recall

```
BGP = path vector, TCP 179, between ASNs
eBGP = different AS, TTL 1, prepends ASN to path
iBGP = same AS, TTL 255, needs full-mesh or RR
4 messages: OPEN (who?), UPDATE (routes), NOTIFICATION (error), KEEPALIVE (alive?)
Timers: keepalive 60s, hold 180s (3 missed = dead)
FSM: Idle -> Connect -> Active -> OpenSent -> OpenConfirm -> Established
Active = BAD (trying but failing)
Loop prevention = reject routes containing own ASN in AS-PATH
Build order: IGP first -> verify ping -> BGP last
```
