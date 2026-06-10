# Lab 02 - Inter-VLAN Routing (Router-on-a-Stick)

**ENCOR v1.2 mapping:** 3.0 Infrastructure — Layer 2 trunking + Layer 3 inter-VLAN routing (part of the 30% Infrastructure domain).
**Status:** ✅ Complete — verified working

> **As-built note:** device names in the lab are `R1` (router), `SW1` (aggregation), and `SW2`/`SW3`/`SW4` (access for Finance/IT/HR). The router uplink lands on **SW1 e0/3**. Verified configs are in [`configs/`](configs/). Cross-VLAN pings return `ttl=63`, confirming the router hop.

## Objective
Route traffic between three VLANs (10, 20, 30) on separate subnets using a single router interface (802.1Q subinterfaces). Prove Layer 3 reachability across VLANs while the switches stay purely Layer 2.

**Expected result:**
- Ping success: `192.168.1.10` -> `192.168.2.10` (VLAN 10 -> VLAN 20)
- Ping success: `192.168.1.10` -> `192.168.3.10` (VLAN 10 -> VLAN 30)

## Topology
```
                     [ CORE-RT ]  (router)
                       Gi0/0  (802.1Q trunk: .10/.20/.30)
                          |
                       e0/0
                     [ AGG-SW ]  (L2, VLANs 10/20/30)
              e0/1      e0/2      e0/3
               |         |         |
            [ACC-SW1] [ACC-SW2] [ACC-SW3]
             e0/1      e0/1      e0/1
               |         |         |
            Host10    Host20    Host30
            VLAN 10   VLAN 20   VLAN 30
```

## Addressing
| Device | Interface | VLAN | IP / Mask | Role |
|--------|-----------|:----:|-----------|------|
| CORE-RT | Gi0/0.10 | 10 | 192.168.1.1 /24 | Gateway VLAN 10 |
| CORE-RT | Gi0/0.20 | 20 | 192.168.2.1 /24 | Gateway VLAN 20 |
| CORE-RT | Gi0/0.30 | 30 | 192.168.3.1 /24 | Gateway VLAN 30 |
| Host10 | - | 10 | 192.168.1.10 /24 | GW 192.168.1.1 |
| Host20 | - | 20 | 192.168.2.10 /24 | GW 192.168.2.1 |
| Host30 | - | 30 | 192.168.3.10 /24 | GW 192.168.3.1 |

## Interface / link plan
| Link | A side | B side | Type | VLANs |
|------|--------|--------|------|-------|
| Core uplink | CORE-RT Gi0/0 | AGG-SW e0/0 | 802.1Q trunk | 10,20,30 |
| Agg -> Acc1 | AGG-SW e0/1 | ACC-SW1 e0/0 | trunk | 10 |
| Agg -> Acc2 | AGG-SW e0/2 | ACC-SW2 e0/0 | trunk | 20 |
| Agg -> Acc3 | AGG-SW e0/3 | ACC-SW3 e0/0 | trunk | 30 |
| Host access | ACC-SWx e0/1 | Host | access | x |

Full device configs are in [`configs/`](configs/).

## Verification - commands & expected output

**1. Router subinterfaces are up with the right IPs**
```
CORE-RT# show ip interface brief | include 0/0
GigabitEthernet0/0       unassigned      YES manual up      up
GigabitEthernet0/0.10    192.168.1.1     YES manual up      up
GigabitEthernet0/0.20    192.168.2.1     YES manual up      up
GigabitEthernet0/0.30    192.168.3.1     YES manual up      up
```

**2. Router has all three connected subnets**
```
CORE-RT# show ip route connected
C   192.168.1.0/24 is directly connected, GigabitEthernet0/0.10
C   192.168.2.0/24 is directly connected, GigabitEthernet0/0.20
C   192.168.3.0/24 is directly connected, GigabitEthernet0/0.30
```

**3. dot1Q encapsulation per subinterface**
```
CORE-RT# show vlans | include 802.1Q|GigabitEthernet
GigabitEthernet0/0.10 (10)
GigabitEthernet0/0.20 (20)
GigabitEthernet0/0.30 (30)
```

**4. Trunks formed on the switches (example: AGG-SW)**
```
AGG-SW# show interfaces trunk
Port        Mode   Encapsulation  Status     Native vlan
Et0/0       on     802.1q         trunking   1
Et0/1       on     802.1q         trunking   1
Et0/2       on     802.1q         trunking   1
Et0/3       on     802.1q         trunking   1

Port        Vlans allowed and active in management domain
Et0/0       10,20,30
Et0/1       10
Et0/2       20
Et0/3       30
```

**5. The cross-VLAN pings (the deliverable)**
```
Host10> ping 192.168.2.10
84 bytes from 192.168.2.10 icmp_seq=1 ttl=63 time=1.5 ms

Host10> ping 192.168.3.10
84 bytes from 192.168.3.10 icmp_seq=1 ttl=63 time=1.6 ms
```
> `ttl=63` (not 64) confirms the packet crossed exactly **one router hop** - proof the Core RT did the routing.

## Troubleshooting
| Symptom | Likely cause | Check / fix |
|---------|--------------|-------------|
| Ping to own gateway fails | Subinterface down or wrong encap VLAN | `show ip int brief`; verify `encapsulation dot1Q <vlan>` matches |
| Gateway pingable, other VLAN not | Allowed-VLAN list missing on a trunk | `show interfaces trunk` - VLAN must be "allowed and active" end to end |
| All cross-VLAN pings fail | Physical Gi0/0 still shut | `no shutdown` on the router physical interface (subinterfaces follow it) |
| Host can't reach gateway at all | Access port in wrong VLAN, or VLAN not in switch DB | `show vlan brief`; create the VLAN, fix `switchport access vlan` |
| Intermittent / native VLAN warning | Native VLAN mismatch across a trunk | Set the native VLAN consistently on both ends |
| `ttl` looks wrong / no reply | Host default gateway wrong | Re-set host GW to the matching `192.168.x.1` |

## Key takeaways
- One router interface routes many VLANs via 802.1Q subinterfaces - each subinterface is the default gateway for its VLAN.
- Switches need every VLAN they *transport* defined in their VLAN database, even if no local host uses it (AGG carries all three).
- Pruning the allowed-VLAN list per trunk is good practice but a frequent cause of "it pings the gateway but nothing else."
- A decrementing TTL is your fastest proof that routing (not just switching) happened.
