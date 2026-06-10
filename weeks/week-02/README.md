# Week 02 — Inter-VLAN Routing (Router-on-a-Stick)

**Domain focus:** 3.0 Infrastructure → Layer 2 trunking + Layer 3 routing
**Lab built:** [Lab 02 — Inter-VLAN Routing](../../labs/lab-02-inter-vlan-routing/)
**Status:** ✅ Complete

## What I covered
- Router-on-a-stick: one router interface, 802.1Q subinterfaces as per-VLAN gateways
- A campus-style layout: router → aggregation switch → access switches → hosts
- End-to-end trunking across multiple switches
- Telling Layer 3 routing apart from Layer 2 switching

## Topology
R1 (router) trunks to SW1 (aggregation) on SW1 e0/3; SW1 trunks down to SW2/SW3/SW4 (access for Finance/IT/HR). Each access switch carries one VLAN; R1 routes between them.

| VLAN | Subnet | Gateway (R1 subif) | Host |
|:----:|--------|--------------------|------|
| 10 (IT)      | 192.168.1.0/24 | 192.168.1.1 | PC6 .10 (SW3) |
| 20 (HR)      | 192.168.2.0/24 | 192.168.2.1 | PC7 .10 (SW4) |
| 30 (Finance) | 192.168.3.0/24 | 192.168.3.1 | PC8 .10 (SW2) |

## Verification I ran
- `show ip route connected` (R1) — three connected subnets, one per subinterface
- `show interfaces trunk` (switches) — VLANs allowed and active end to end
- Ping PC6 → PC7 / PC8 — **success, `ttl=63`** (one router hop = proof of routing)

## Key takeaways / gotchas
- **The big one:** `switchport mode trunk` silently fails on IOSv-L2 without `switchport trunk encapsulation dot1q` first → empty `show interfaces trunk` → nothing forwards. This cost the most debugging time.
- A trunk must be a trunk on **both** ends; leaving one end as access kills the VLAN path.
- Router subinterfaces need `encapsulation dot1Q <vlan>` — an IP address alone does nothing.
- A decrementing TTL is the fastest proof that routing (not just switching) happened.

## Configs
Verified device configs: [`configs/`](configs/) — R1, SW1 (agg), SW2/SW3/SW4 (access), PCs.
