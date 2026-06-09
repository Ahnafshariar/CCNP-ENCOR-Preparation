# EVE-NG — Lab Environment

All labs in this portfolio are built and verified in **EVE-NG**.

## Node types used
| Role | Image type | Notes |
|------|-----------|-------|
| Switch (SW1, SW2) | Cisco **IOSv-L2** | Layer 2 switching, trunking, STP |
| End hosts (VPC1–4) | VPCS | Lightweight test hosts |
| Router (later labs) | Cisco IOSv / CSR1000v | For L3 / OSPF / BGP labs |

## ⚠️ Images are NOT in this repo
Cisco IOSv-L2 / IOU / qcow2 images are **licensed Cisco binaries** and are never committed here (see root `.gitignore`). This repo contains only my own configurations, topologies, and documentation.

## Topology exports
Saved `.unl` files (small XML) live in [`topologies/`](topologies/).
