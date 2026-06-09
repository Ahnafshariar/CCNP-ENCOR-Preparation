# CCNP ENCOR 350-401 (v1.2) — Study Progress Tracker

- **Exam target:** Q4 2026
- **Blueprint:** ENCOR 350-401 **v1.2** (live since 19 Mar 2026)
- **Lab environment:** EVE-NG — Cisco IOSv-L2 + IOU web console
- **Locked base topology:** SW1 ↔ SW2 802.1Q trunk (e0/0↔e0/0, native VLAN 100, allowed 10/20) + 4 VPCs
  - VPC1 192.168.10.240/27 · VPC2 192.168.20.240/27 · VPC3 192.168.10.241/27 · VPC4 192.168.20.241/27

Status key: ⬜ Not started · 🟨 In progress · ✅ Solid · 🔁 Needs review

---

## Domain coverage (v1.2 weights)

| # | Domain | Weight | Status | Confidence (1–5) | Last touched |
|---|--------|:------:|:------:|:----------------:|--------------|
| 1.0 | Architecture (enterprise design, fabric, OSPF/BGP path selection, wireless concepts) | 15% | ⬜ | – | – |
| 2.0 | Virtualization (VRF, GRE/IPsec, LISP, VXLAN basics) | 10% | ⬜ | – | – |
| 3.0 | Infrastructure (L2: VLAN/trunk/STP/EtherChannel · L3: OSPF/BGP · IP services · NAT/QoS) | 30% | 🟨 | 2 | – |
| 4.0 | Network Assurance (SNMP, syslog, NetFlow, SPAN, NETCONF/RESTCONF, debugs) | 10% | ⬜ | – | – |
| 5.0 | Security (ACLs, CoPP, AAA/802.1X, device hardening, wireless security) | 20% | ⬜ | – | – |
| 6.0 | Automation & AI (Python basics, JSON/XML/YAML, EEM, REST APIs, Ansible/agentless) | 15% | ⬜ | – | – |

---

## Lab portfolio log

| Lab | Title | Domain map | Status | Repo path |
|-----|-------|------------|:------:|-----------|
| 01 | Basic VLAN + 802.1Q Trunk | 3.0 Infrastructure (L2) | ✅ | `labs/lab-01-vlan-trunk/` |
| 02 | _(next — STP root election & port roles, or EtherChannel)_ | 3.0 Infrastructure (L2) | ⬜ | – |
| 03 | _(planned)_ | – | ⬜ | – |

> Every lab folder must contain: objective, topology, addressing table, full config, **verification commands with expected output**, troubleshooting section, and ENCOR v1.2 blueprint mapping.

---

## Weekly log

| Week | Dates | Bootcamp topic | Hours | Lab done | Notes / weak spots |
|------|-------|----------------|:-----:|----------|--------------------|
| 1 | | | | | |
| 2 | | | | | |

---

## Exam-readiness checklist (fill closer to Q4 2026)

- [ ] All 6 domains at confidence ≥ 4
- [ ] ≥ 1 portfolio lab per major Infrastructure sub-topic (VLAN ✅, STP, EtherChannel, OSPF, BGP, NAT)
- [ ] Practice exams scoring ≥ 85% consistently
- [ ] Automation: can read/write JSON & YAML, write a basic EEM applet, call a REST API
- [ ] Booked Pearson VUE slot
