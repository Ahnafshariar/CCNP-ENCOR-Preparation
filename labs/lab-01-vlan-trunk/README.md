# Lab 01 — Basic VLAN Configuration + 802.1Q Trunk

**ENCOR v1.2 mapping:** 3.0 Infrastructure → Layer 2 (VLANs, trunking, 802.1Q) — part of the 30% Infrastructure domain.
**Status:** ✅ Complete

## Objective
Segment two access VLANs across two switches connected by a single 802.1Q trunk, and confirm intra-VLAN reachability / inter-VLAN isolation at Layer 2.

## Topology
```
   VPC1 (VLAN10)   VPC2 (VLAN20)              VPC3 (VLAN10)   VPC4 (VLAN20)
        |               |                          |               |
      [SW1] e0/0 ===== 802.1Q trunk ===== e0/0 [SW2]
              native VLAN 100, allowed 10,20
```

## Addressing
| Host | VLAN | IP / Mask |
|------|:----:|-----------|
| VPC1 | 10 | 192.168.10.240/27 |
| VPC2 | 20 | 192.168.20.240/27 |
| VPC3 | 10 | 192.168.10.241/27 |
| VPC4 | 20 | 192.168.20.241/27 |

## Configuration (both switches, mirror as needed)
```
vlan 10
 name DATA
vlan 20
 name VOICE
vlan 100
 name NATIVE
!
interface e0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 100
 switchport trunk allowed vlan 10,20
!
interface <access-port-to-VPC>
 switchport mode access
 switchport access vlan 10        ! (or 20)
```

## Verification — commands & expected output
```
SW1# show vlan brief
! Expect VLAN 10 (DATA), 20 (VOICE), 100 (NATIVE) with correct access ports listed

SW1# show interfaces trunk
! Expect e0/0 — mode on, encapsulation 802.1q, native vlan 100, allowed/active 10,20

SW1# show interfaces e0/0 switchport
! Expect: Administrative Mode: trunk, Trunking Native Mode VLAN: 100
```
Ping test: VPC1 → VPC3 succeeds (same VLAN 10). VPC1 → VPC2 fails at L2 (different VLAN, no L3 device yet) — expected.

## Troubleshooting
| Symptom | Likely cause | Check |
|---------|--------------|-------|
| Trunk not forming | Encapsulation/mode mismatch | `show int trunk`, both ends `mode trunk` + `dot1q` |
| Native VLAN mismatch CDP warning | Native VLAN differs across link | `show int e0/0 switchport` both sides = 100 |
| VLAN traffic blocked over trunk | VLAN not in allowed list | `switchport trunk allowed vlan` includes 10,20 |
| Host can't reach same-VLAN peer | Access port in wrong VLAN | `show vlan brief` port membership |

## Key takeaways
- Native VLAN must match on both trunk ends or you get a mismatch error and potential VLAN hopping risk.
- Pruning the allowed VLAN list is a best practice for security and broadcast control.
