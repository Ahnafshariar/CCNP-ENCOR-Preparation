# Week 05 — VRF Lite (Virtual Routing and Forwarding)

**Domain focus:** 2.0 Virtualization — VRF, network segmentation
**Lab built:** [Lab 05 — VRF Lite](../../labs/lab-05-vrf-lite/)
**Status:** ✅ Complete

## What I covered
- VRF Lite: creating multiple isolated routing tables on a single router
- Overlapping IP address spaces across VRFs
- Per-VRF subinterfaces over a shared WAN trunk (dot1Q)
- Per-VRF static routes and the `vrf` keyword in CLI commands
- Proving isolation: global pings fail, per-VRF pings succeed

## Verification I ran
- `show ip vrf` — confirmed three VRFs with correct interface mappings
- `show ip route vrf A/B/C` — each VRF has its own connected + static routes
- `ping vrf A/B/C 20.1.0.1` from R1 — all three succeed
- `ping 20.1.0.1` from R1 (global) — fails, proving isolation works

## Key takeaways / gotchas
- **`ip vrf forwarding` must come before `ip address`** — reversing the order wipes the IP with a warning. This is the number one VRF configuration mistake.
- Same IP (10.1.0.1) on three interfaces is legal when each is in a different VRF.
- LAN side: one physical port per VRF = simplest isolation (no tagging needed).
- WAN side: dot1Q subinterfaces multiplex VRFs over one cable (same concept as router-on-a-stick, but each subinterface belongs to a VRF instead of a VLAN gateway).
- The `vrf` keyword is needed in every operational command: `ping vrf`, `show ip route vrf`, `traceroute vrf`.
- **First domain 2.0 (Virtualization) lab in the portfolio** — previously all labs were domain 3.0 (Infrastructure).

## Configs
Verified device configs: [`configs/`](configs/) — R1, R2, VPCs.
