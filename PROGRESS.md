# CCNP ENCOR 350-401 (v1.2) — Study Progress Tracker

- **Exam target:** Q4 2026
- **Blueprint:** ENCOR 350-401 **v1.2** (live since 19 Mar 2026)
- **Lab environment:** EVE-NG — Cisco IOSv / IOSv-L2 + IOU web console
- **Topology:** evolves per lab — each lab documents its own topology

Status key: ⬜ Not started · 🟨 In progress · ✅ Solid · 🔁 Needs review

---

## Domain coverage (v1.2 weights)

| # | Domain | Weight | Status | Confidence (1–5) | Last touched |
|---|--------|:------:|:------:|:----------------:|--------------|
| 1.0 | Architecture (enterprise design, fabric, OSPF/BGP path selection, wireless concepts) | 15% | ⬜ | – | – |
| 2.0 | Virtualization (VRF, GRE/IPsec, LISP, VXLAN basics) | 10% | 🟨 | 2 | Lab 05 |
| 3.0 | Infrastructure (L2: VLAN/trunk/STP/EtherChannel · L3: OSPF/BGP · IP services · NAT/QoS) | 30% | 🟨 | 3 | Lab 04 |
| 4.0 | Network Assurance (SNMP, syslog, NetFlow, SPAN, NETCONF/RESTCONF, debugs) | 10% | ⬜ | – | – |
| 5.0 | Security (ACLs, CoPP, AAA/802.1X, device hardening, wireless security) | 20% | ⬜ | – | – |
| 6.0 | Automation & AI (Python basics, JSON/XML/YAML, EEM, REST APIs, Ansible/agentless) | 15% | ⬜ | – | – |

---

## Lab portfolio log

| Lab | Title | Domain map | Status | Repo path |
|-----|-------|------------|:------:|-----------|
| 01 | Basic VLAN + 802.1Q Trunk | 3.0 Infrastructure (L2) | ✅ | `labs/lab-01-vlan-trunk/` |
| 02 | Inter-VLAN Routing (Router-on-a-Stick) | 3.0 Infrastructure (L2+L3) | ✅ | `labs/lab-02-inter-vlan-routing/` |
| 03 | Static Routing with Path Control | 3.0 Infrastructure (L3) | ✅ | `labs/lab-03-static-routing/` |
| 04 | EIGRP + PBR + IP SLA Tracking | 3.0 Infrastructure (L3) | ✅ | `labs/lab-04-eigrp-pbr-ipsla/` |
| 05 | VRF Lite | 2.0 Virtualization | ✅ | `labs/lab-05-vrf-lite/` |
| 06 | _(planned)_ | – | ⬜ | – |

> Every lab folder must contain: objective, topology, addressing table, full config, **verification commands with expected output**, troubleshooting section, and ENCOR v1.2 blueprint mapping.

---

## Weekly log

| Week | Dates | Bootcamp topic | Hours | Lab done | Notes / weak spots |
|------|-------|----------------|:-----:|----------|--------------------|
| 1 | | VLAN + trunking | | Lab 01 | IOSv-L2 needs `encapsulation dot1q` before `mode trunk` |
| 2 | | Inter-VLAN routing | | Lab 02 | Empty `show interfaces trunk` = encapsulation missing |
| 3 | | Static routing, path control | | Lab 03 | Interface + next-hop must be consistent in static routes |
| 4 | | EIGRP, PBR, IP SLA | | Lab 04 | One route-map per interface; IP SLA alone changes nothing |
| 5 | | VRF Lite | | Lab 05 | `ip vrf forwarding` before `ip address` — always |

---

## Exam-readiness checklist (fill closer to Q4 2026)

- [ ] All 6 domains at confidence ≥ 4
- [ ] ≥ 1 portfolio lab per major Infrastructure sub-topic (VLAN ✅, inter-VLAN ✅, static ✅, EIGRP ✅, OSPF, BGP, STP, EtherChannel, NAT)
- [ ] Virtualization labs (VRF ✅, GRE, VXLAN)
- [ ] Practice exams scoring ≥ 85% consistently
- [ ] Automation: can read/write JSON & YAML, write a basic EEM applet, call a REST API
- [ ] Booked Pearson VUE slot