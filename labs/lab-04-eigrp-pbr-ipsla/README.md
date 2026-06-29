# Lab 04 — EIGRP + Policy-Based Routing + IP SLA Tracking

**ENCOR v1.2 mapping:** 3.0 Infrastructure — EIGRP, PBR, IP SLA, path control
**Status:** ✅ Complete — verified working

## Objective

Build a dual-path EIGRP network and use **PBR (Policy-Based Routing)** to override EIGRP's path selection for specific traffic. Use **IP SLA** to monitor path health and automatically failover when a link goes down.

---

## What is PBR? (Simple version)

Normally, a router decides where to send a packet by looking at the **routing table** (built by EIGRP, OSPF, static routes, etc). PBR says: "Before you check the routing table, check MY rules first."

PBR has three pieces that chain together:

```
ACL               Route-Map              Interface
(the eyes)    →   (the brain)       →    (the switch)
identifies        decides what            turns it on
the traffic       to do with it           for incoming packets
```

- **ACL** alone does nothing — it just describes traffic
- **Route-map** alone does nothing — it just holds logic
- **`ip policy route-map` on an interface** activates it

All three must be connected, or PBR has no effect.

**Critical rule:** Only **ONE** `ip policy route-map` can be active on an interface at a time. Applying a second one **replaces** the first — it does not stack. To combine multiple policies, use multiple **entries** (sequence numbers) inside one route-map.

---

## What is IP SLA? (Simple version)

IP SLA is a **heartbeat monitor**. It pings a target on a schedule and records whether it replied. By itself, it changes nothing — it just watches.

```
IP SLA           Track Object         PBR / Static Route
(the sensor) →   (the translator) →   (the decision maker)
pings every       says UP or DOWN      uses UP/DOWN to decide
X seconds         based on replies     where to send traffic
```

Three layers, each useless without the next one.

---

## Topology

```
                      [ R2 ]  (top path, BW2000)
                  e0/0      e0/1
               10.1.2.2    10.2.4.1
                  |              |
               10.1.2.1      10.2.4.2
               e0/2            e0/0
VPC6 --- SW1 --- [ R1 ] -------------- [ R4 ] --- VPC8
VPC7 ---/       e0/1            e0/1
               10.1.3.1      10.3.4.2
                  |              |
               10.1.3.2    10.3.4.1
                  e0/0      e0/1
                      [ R3 ]  (bottom path, BW1000)
```

## Addressing

| Device | Interface | IP | Subnet | Notes |
|--------|-----------|------|--------|-------|
| R1 | e0/0 | 10.1.0.1 | 10.1.0.0/24 | LAN gateway |
| R1 | e0/2 | 10.1.2.1 | 10.1.2.0/24 | To R2 (BW2000) |
| R1 | e0/1 | 10.1.3.1 | 10.1.3.0/24 | To R3 (BW1000) |
| R2 | e0/0 | 10.1.2.2 | 10.1.2.0/24 | To R1 |
| R2 | e0/1 | 10.2.4.1 | 10.2.4.0/24 | To R4 (BW2000) |
| R3 | e0/0 | 10.1.3.2 | 10.1.3.0/24 | To R1 |
| R3 | e0/1 | 10.3.4.1 | 10.3.4.0/24 | To R4 (BW1000) |
| R4 | e0/0 | 10.2.4.2 | 10.2.4.0/24 | To R2 |
| R4 | e0/1 | 10.3.4.2 | 10.3.4.0/24 | To R3 |
| R4 | e0/2 | 10.4.0.1 | 10.4.0.0/24 | VPC8 gateway |
| SW1 | — | — | 10.1.0.0/24 | L2 switch (no IP) |
| VPC6 | eth0 | 10.1.0.10 | /24 | GW 10.1.0.1 |
| VPC7 | eth0 | 10.1.0.20 | /24 | GW 10.1.0.1 |
| VPC8 | eth0 | 10.4.0.10 | /24 | GW 10.4.0.1 |

## EIGRP setup

All four routers (R1–R4) run `router eigrp 2000` with exact network statements (`0.0.0.0` wildcard). Without PBR, EIGRP picks the **top path** (R1→R2→R4) because BW2000 gives a better EIGRP composite metric than the bottom path's BW1000. The tasks below override that choice with PBR.

---

## Task 1 — Size-based PBR: 500–700 byte packets via R3

### The problem
EIGRP sends everything via R2 (top path, BW2000). We want packets between 500 and 700 bytes to take the bottom path via R3 instead.

### The solution
```
route-map PBR-Size permit 10
 match length 500 700
 set ip next-hop 10.1.3.2
route-map PBR-Size permit 20
 ! catch-all: everything else follows normal EIGRP routing
!
interface e0/0
 ip policy route-map PBR-Size
```

### How it works
- `match length 500 700` — matches Layer 3 packet size (inclusive). No ACL needed.
- `set ip next-hop 10.1.3.2` — overrides the routing table, sends to R3.
- Entry 20 (no match/set) — all other traffic falls through to normal routing (R2 via EIGRP).

### Verify
```
! Generate a 500-byte ping from VPC6:
VPC6> ping 10.4.0.10 -l 500

! Check PBR is being applied:
R1# show route-map PBR-Size
R1# debug ip policy                  ! see PBR decisions in real time (disable with: undebug all)
```

The debug will show: `policy match` for 500-byte packets (sent to 10.1.3.2), and no PBR action for normal-sized pings (sent via EIGRP to R2).

---

## Task 2 — IP SLA tracked PBR: failover when R3–R4 link goes down

### The problem
We want VPC6 traffic to prefer R3 (bottom path). But if the R3–R4 link (10.3.4.0/24) goes down (fiber cut, interface failure), traffic should automatically switch to R2 (top path) — without any manual intervention.

### The solution (three layers)

**Layer 1 — IP SLA: the heartbeat**
```
ip sla 1
 icmp-echo 10.1.3.2 source-interface Ethernet0/1
 frequency 10
 timeout 5000
ip sla schedule 1 life forever start-time now
!
ip sla 2
 icmp-echo 10.1.2.2 source-interface Ethernet0/2
 frequency 10
 timeout 5000
ip sla schedule 2 life forever start-time now
```
SLA 1 pings R3 every 10 seconds. SLA 2 pings R2 every 10 seconds. They just monitor — they change nothing.

**Layer 2 — Track: the translator**
```
track 1 ip sla 1 reachability
 delay down 1 up 5
track 2 ip sla 2 reachability
 delay down 1 up 5
```
Translates SLA results into simple UP/DOWN. Goes DOWN fast (1 second), comes UP slow (5 seconds) to prevent flapping.

**Layer 3 — PBR: the decision**
```
ip access-list extended PBR-VPC6-TRAFFIC
 permit ip host 10.1.0.10 any
!
route-map PBR-Tracked permit 10
 match ip address PBR-VPC6-TRAFFIC
 set ip next-hop verify-availability 10.1.3.2 10 track 1
 set ip next-hop verify-availability 10.1.2.2 20 track 2
route-map PBR-Tracked permit 20
 ! catch-all: normal routing
!
interface e0/0
 ip policy route-map PBR-Tracked
```

### How it works
- Seq 10 (R3): checked first because lower number. If track 1 is UP, send to R3. Done.
- Seq 20 (R2): only checked if track 1 is DOWN. If track 2 is UP, send to R2. Done.
- Both DOWN: no `set` applies, packet falls to entry 20 (normal EIGRP routing).

### Simulate the failure
```
! On R3, shut the link to R4:
R3(config)# int e0/1
R3(config-if)# shutdown

! Watch track 1 go DOWN:
R1# show track 1
! State should change from UP to DOWN

! Traceroute now takes the top path:
VPC6> trace 10.4.0.10
! Should show: 10.1.0.1 -> 10.1.2.2 -> 10.2.4.2 -> 10.4.0.10

! Restore:
R3(config-if)# no shutdown
! Wait 5 seconds (delay up), track 1 returns to UP
! Traffic automatically reverts to R3 path
```

### Verify
```
R1# show track brief             ! quick UP/DOWN status of all tracks
R1# show track 1                 ! detailed state + change count
R1# show track 2
R1# show ip sla summary          ! all SLA probe results
R1# show route-map PBR-Tracked   ! hit counters per entry
```

---

## Why `verify-availability` matters

| Command | Behavior |
|---------|----------|
| `set ip next-hop 10.1.3.2` | Sends blindly — even if R3 is dead (black hole) |
| `set ip next-hop verify-availability 10.1.3.2 10 track 1` | Checks track 1 first — only sends if UP |

Without `verify-availability`, PBR pushes traffic into a dead path. With it, PBR checks the heartbeat before deciding. This is the difference between a dumb redirect and an intelligent one.

---

## SW1 note

SW1 connects VPC6, VPC7, and R1's e0/0 — all on 10.1.0.0/24. A router cannot have multiple interfaces on the same subnet (IOS rejects with "overlaps with"). SW1 must be an **IOSv-L2 switch image** in EVE-NG, acting as a pure Layer 2 device with no IP address. See [`configs/SW1.txt`](configs/SW1.txt).

---

## Troubleshooting

| Symptom | Likely cause | Check |
|---------|--------------|-------|
| PBR has no effect | Route-map not applied on interface | `show ip policy` on R1 |
| Wrong route-map active | Applied a second `ip policy route-map` (replaced the first) | `show run int e0/0` — only last one survives |
| Track stuck on DOWN | SLA source-interface wrong | `show ip sla statistics` — check probe results |
| Track flaps UP/DOWN rapidly | `delay up` too low | Increase `delay up` in track config |
| `verify-availability` ignored | Track object doesn't exist or wrong ID | `show track brief` — confirm track IDs match |
| EIGRP not forming neighbors | AS number mismatch or network statement missing | `show ip eigrp neighbors` |

## Key takeaways

- **One interface, one route-map.** Multiple `ip policy route-map` commands on the same interface don't stack — only the last one is active.
- **ACL inside PBR: `permit` means "match this policy," not "allow the packet."** Denied traffic is not dropped — it just skips to the next route-map entry.
- **IP SLA by itself changes nothing.** It needs a track object to translate results, and something (PBR, static route, HSRP) to act on the track.
- **`verify-availability` is what makes PBR intelligent.** Without it, PBR sends traffic blindly.
- **`delay down 1 up 5`** = trust is lost fast, earned back slow. Prevents flapping.

Full device configs are in [`configs/`](configs/).
