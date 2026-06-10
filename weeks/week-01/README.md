# Week 01 — Layer 2 Foundations: VLANs & 802.1Q Trunking

**Domain focus:** 3.0 Infrastructure → Layer 2 (part of the 30% domain)
**Lab built:** [Lab 01 — Basic VLAN + 802.1Q Trunk](../../labs/lab-01-vlan-trunk/)
**Status:** ✅ Complete

## What I covered
- Creating VLANs and assigning access ports
- 802.1Q trunking between two switches with a dedicated native VLAN (100)
- Pruning the trunk allowed-VLAN list (10, 20)
- Same-VLAN reachability across a trunk, and VLAN isolation at Layer 2

## Topology
Two IOSv-L2 switches (SW1, SW2) joined by one 802.1Q trunk on e0/0; two VLANs, four hosts.

| Host | Port | VLAN | IP (/27) |
|------|------|:----:|----------|
| VPC1 | SW1 e0/1 | 10 | 192.168.10.240 |
| VPC2 | SW1 e0/2 | 20 | 192.168.20.240 |
| VPC3 | SW2 e0/1 | 10 | 192.168.10.241 |
| VPC4 | SW2 e0/2 | 20 | 192.168.20.241 |

## Verification I ran
- `show vlan brief` — access ports in the correct VLANs
- `show interfaces trunk` — e0/0 trunking, native 100, allowed 10,20
- Ping VPC1 → VPC3 (VLAN 10) **succeeds**; VPC1 → VPC2 **fails** at L2 (different VLAN, no router) — expected

## Key takeaways / gotchas
- Native VLAN must match on both ends of a trunk or you get a mismatch warning.
- On IOSv-L2, set `switchport trunk encapsulation dot1q` **before** `switchport mode trunk`.
- Pure-L2 lab: there is no router, so the host gateway values are never used.

## Configs
Verified device configs: [`configs/`](configs/) — SW1, SW2, VPCs.
