# Lab 01: Basic VLAN Configuration

## Metadata
| Field | Value |
|-------|-------|
| **Topic** | Layer 2 Technologies - VLANs & Trunking |
| **ENCOR Weight** | 15% |
| **Difficulty** | Beginner |
| **Estimated Time** | 60-90 minutes |
| **Status** | Completed |
| **Date Completed** | 2026-06-08 |
| **Course Context** | CCNP ENCOR Course - Class 1 & 2 Review |

---

## Objective

Build a multi-switch Layer 2 network with VLAN segmentation and 802.1Q trunking. Verify that hosts within the same VLAN can communicate across switches while remaining isolated from other VLANs. Document the complete configuration and verification process for portfolio reference.

**Key Skills Demonstrated:**
- VLAN creation and naming
- Access port assignment
- 802.1Q trunk configuration with native VLAN
- Inter-switch VLAN communication verification
- Layer 2 broadcast domain isolation

---

## Topology

### Logical Diagram

```
                                    +-----------+
                                    |    SW2    |
                                    |           |
                      Trunk (802.1Q)|           |
                    +---------------|Gi0/0  Gi0/1|-------+ PC3 (VLAN 10)
                    |               |           |
                    |               +-----------+
                    |
               +----|---+
               |    SW1   |
               |          |
         +-----|Gi0/1     |
         |     |    Gi0/0 |-----+ Trunk to SW2
         |     |          |
   PC1   |     |    Gi0/2 |-----+ PC2
 (VLAN10)|     +----------+
         |
    192.168.10.10/24

```

### Physical Topology (EVE-NG)

```
+-----------------+                    +-----------------+
|       SW1       |     Gi0/0 <->      |       SW2       |
|   (IOSv-L2)     |<--- 802.1Q Trunk-->|   (IOSv-L2)     |
|                 |                    |                 |
|  Gi0/1    Gi0/2 |                    |  Gi0/1          |
+---+---------+---+                    +---+-------------+
    |         |                            |
  (Access)  (Access)                   (Access)
 VLAN 10    VLAN 20                     VLAN 10
    |         |                            |
  +----+   +----+                       +----+
  |PC1 |   |PC2 |                       |PC3 |
  +----+   +----+                       +----+
```

### Device Inventory
| Device | Model | Role | IP Address | Connects To |
|--------|-------|------|------------|-------------|
| SW1 | Cisco IOSv-L2 | Access/Distribution | N/A (L2) | SW2 (Gi0/0), PC1 (Gi0/1), PC2 (Gi0/2) |
| SW2 | Cisco IOSv-L2 | Distribution | N/A (L2) | SW1 (Gi0/0), PC3 (Gi0/1) |
| PC1 | VPCS | End Host - VLAN 10 | 192.168.10.10/24 | SW1 (Gi0/1) |
| PC2 | VPCS | End Host - VLAN 20 | 192.168.20.10/24 | SW1 (Gi0/2) |
| PC3 | VPCS | End Host - VLAN 10 | 192.168.10.20/24 | SW2 (Gi0/1) |

### VLAN Table
| VLAN ID | Name | Subnet | Purpose | Native |
|---------|------|--------|---------|--------|
| 1 | default | N/A | Factory default, unused | No |
| 10 | SALES | 192.168.10.0/24 | Sales department hosts | No |
| 20 | ENGINEERING | 192.168.20.0/24 | Engineering department hosts | No |
| 99 | NATIVE | N/A | Native VLAN for trunk (security best practice) | Yes |

### Port Assignment Table
| Device | Port | Mode | VLAN | Description |
|--------|------|------|------|-------------|
| SW1 | Gi0/0 | Trunk (802.1Q) | ALL (10,20,99) | Uplink to SW2 |
| SW1 | Gi0/1 | Access | 10 | PC1 - Sales |
| SW1 | Gi0/2 | Access | 20 | PC2 - Engineering |
| SW2 | Gi0/0 | Trunk (802.1Q) | ALL (10,20,99) | Uplink to SW1 |
| SW2 | Gi0/1 | Access | 10 | PC3 - Sales |

---

## Configuration Steps

### Step 1: Create VLANs on SW1

**Device:** SW1

```
SW1# configure terminal
SW1(config)# vlan 10
SW1(config-vlan)# name SALES
SW1(config-vlan)# exit

SW1(config)# vlan 20
SW1(config-vlan)# name ENGINEERING
SW1(config-vlan)# exit

SW1(config)# vlan 99
SW1(config-vlan)# name NATIVE
SW1(config-vlan)# exit
```

**Explanation:** VLANs are created in the VLAN database before port assignment. The `name` parameter provides administrative description and is visible in `show vlan brief` output. VLAN 99 is reserved as the native VLAN for trunk links as a security best practice (default native VLAN is 1, which is a known attack vector).

---

### Step 2: Configure Access Ports on SW1

**Device:** SW1

```
SW1(config)# interface gigabitEthernet 0/1
SW1(config-if)# description PC1 - Sales Department - VLAN 10
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# spanning-tree portfast
SW1(config-if)# no shutdown
SW1(config-if)# exit

SW1(config)# interface gigabitEthernet 0/2
SW1(config-if)# description PC2 - Engineering Department - VLAN 20
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 20
SW1(config-if)# spanning-tree portfast
SW1(config-if)# no shutdown
SW1(config-if)# exit
```

**Explanation:** Each access port is statically assigned to a single VLAN. PortFast is enabled to bypass STP listening/learning states (~30 second delay), which is safe for end-host ports. The `description` command aids troubleshooting and documentation. `switchport mode access` disables DTP (Dynamic Trunking Protocol) negotiation, preventing accidental trunk formation.

---

### Step 3: Configure Trunk Port on SW1

**Device:** SW1

```
SW1(config)# interface gigabitEthernet 0/0
SW1(config-if)# description Trunk to SW2 - 802.1Q
SW1(config-if)# switchport mode trunk 
## If it doesn't work on the switch as it might be enable and will require dot1q/802.1q
## SW1(config-if)# switchport trunk encap dot1q
SW1(config-if)# switchport trunk native vlan 99
SW1(config-if)# switchport trunk allowed vlan 10,20,99
SW1(config-if)# no shutdown
SW1(config-if)# exit
```

**Explanation:** The trunk link carries tagged frames for VLANs 10, 20, and 99 using 802.1Q encapsulation. The native VLAN is explicitly set to 99 for security (VLAN hopping attacks often target the default native VLAN 1). Limiting allowed VLANs with `switchport trunk allowed vlan` follows the principle of least privilege — only VLANs that need to traverse the trunk are permitted. `switchport mode trunk` hard-codes the trunk and disables DTP negotiation.

---

### Step 4: Create VLANs on SW2

**Device:** SW2

```
SW2# configure terminal
SW2(config)# vlan 10
SW2(config-vlan)# name SALES
SW2(config-vlan)# exit

SW2(config)# vlan 20
SW2(config-vlan)# name ENGINEERING
SW2(config-vlan)# exit

SW2(config)# vlan 99
SW2(config-vlan)# name NATIVE
SW2(config-vlan)# exit
```

**Explanation:** VLANs must be created on every switch where they exist. In production, VTP (VLAN Trunking Protocol) or automated provisioning would handle this, but for this foundational lab, manual VLAN creation ensures understanding of the underlying process.

---

### Step 5: Configure Access Port on SW2

**Device:** SW2

```
SW2(config)# interface gigabitEthernet 0/1
SW2(config-if)# description PC3 - Sales Department - VLAN 10
SW2(config-if)# switchport mode access
SW2(config-if)# switchport access vlan 10
SW2(config-if)# spanning-tree portfast
SW2(config-if)# no shutdown
SW2(config-if)# exit
```

---

### Step 6: Configure Trunk Port on SW2

**Device:** SW2

```
SW2(config)# interface gigabitEthernet 0/0
SW2(config-if)# description Trunk to SW1 - 802.1Q
SW2(config-if)# switchport mode trunk
## SW2(config-if)# switchport trunk encap dot1q
SW2(config-if)# switchport trunk native vlan 99
SW2(config-if)# switchport trunk allowed vlan 10,20,99
SW2(config-if)# no shutdown
SW2(config-if)# exit

SW2(config)# exit
SW2# write memory
```

**Critical Detail:** Both sides of a trunk must agree on the native VLAN. A native VLAN mismatch generates a CDP/LLDP warning and can cause traffic leakage or STP issues. The `switchport trunk allowed vlan` list should match on both ends for predictable behavior.

---

### Step 7: Configure End Hosts (VPCS)

**Device:** PC1 (VPCS)

```
PC1> ip 192.168.10.10 255.255.255.0
PC1> save
```

**Device:** PC2 (VPCS)

```
PC2> ip 192.168.20.10 255.255.255.0
PC2> save
```

**Device:** PC3 (VPCS)

```
PC3> ip 192.168.10.20 255.255.255.0
PC3> save
```

---

## Verification & Output

### Verification 1: VLAN Database on SW1

```bash
SW1# show vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi1/0, Gi1/1, Gi1/2, Gi1/3
                                                Gi2/0, Gi2/1, Gi2/2, Gi2/3
                                                Gi3/0, Gi3/1, Gi3/2, Gi3/3
10   SALES                            active    Gi0/1
20   ENGINEERING                      active    Gi0/2
99   NATIVE                           active
1002 fddi-default                     act/unsup
1003 token-ring-default              act/unsup
1004 fddinet-default                 act/unsup
1005 trnet-default                   act/unsup
```

**Expected Result:** VLANs 10, 20, and 99 appear with correct names. Gi0/1 is assigned to VLAN 10, Gi0/2 to VLAN 20.
**Actual Result:** MATCH

**Analysis:** VLAN 1 remains as the default but is unused on access ports. VLAN 99 has no access ports assigned — this is correct as it serves only as the native (untagged) VLAN on the trunk link.

---

### Verification 2: Trunk Status on SW1

```bash
SW1# show interfaces trunk

Port        Mode             Encapsulation  Status        Native vlan
Gi0/0       on               802.1q         trunking      99

Port        Vlans allowed on trunk
Gi0/0       10,20,99

Port        Vlans allowed and active in management domain
Gi0/0       10,20,99

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/0       10,20,99
```

**Expected Result:** Port Gi0/0 is trunking with 802.1Q encapsulation, native VLAN 99, and allows VLANs 10, 20, 99.
**Actual Result:** MATCH

**Analysis:** The `on` mode indicates trunking is administratively forced (no DTP negotiation). All three VLANs are active and forwarding. If a VLAN were missing from the "active" list, it would indicate the VLAN is not created in the local VLAN database.

---

### Verification 3: Trunk Status on SW2

```bash
SW2# show interfaces trunk

Port        Mode             Encapsulation  Status        Native vlan
Gi0/0       on               802.1q         trunking      99

Port        Vlans allowed on trunk
Gi0/0       10,20,99

Port        Vlans allowed and active in management domain
Gi0/0       10,20,99

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/0       10,20,99
```

**Expected Result:** Both switches show matching trunk configuration.
**Actual Result:** MATCH

---

### Verification 4: Interface Status on SW1

```bash
SW1# show interfaces status

Port      Name               Status       Vlan       Duplex  Speed Type
Gi0/0     Trunk to SW2       connected    trunk      full    1000  
Gi0/1     PC1 - Sales        connected    10         full    1000  
Gi0/2     PC2 - Engineering  connected    20         full    1000  
Gi1/0                        notconnect   1            auto   auto  
... (remaining ports notconnect)
```

**Expected Result:** All three active ports show `connected` status with correct VLAN assignment.
**Actual Result:** MATCH

---

### Verification 5: Same-VLAN Communication Test (PC1 to PC3)

```bash
PC1> ping 192.168.10.20

84 bytes from 192.168.10.20 icmp_seq=1 ttl=64 time=0.978 ms
84 bytes from 192.168.10.20 icmp_seq=2 ttl=64 time=0.845 ms
84 bytes from 192.168.10.20 icmp_seq=3 ttl=64 time=0.912 ms
84 bytes from 192.168.10.20 icmp_seq=4 ttl=64 time=0.876 ms
84 bytes from 192.168.10.20 icmp_seq=5 ttl=64 time=0.934 ms
```

**Result:** PASS - 5/5 packets received, average RTT ~0.9ms

**Frame Walk Analysis:**
1. PC1 sends untagged frame to SW1 Gi0/1
2. SW1 receives on VLAN 10 access port, associates frame with VLAN 10
3. SW1 forwards toward PC3 via trunk Gi0/0 — inserts 802.1Q tag (VLAN ID = 10)
4. Tagged frame traverses trunk link to SW2
5. SW2 receives on trunk Gi0/0, reads VLAN tag (10), forwards out Gi0/1 (VLAN 10 access port)
6. SW2 strips 802.1Q tag before forwarding to PC3 (access ports deliver untagged frames)
7. PC3 receives frame, replies following reverse path

---

### Verification 6: Cross-VLAN Communication Test (PC1 to PC2) — Expected Fail

```bash
PC1> ping 192.168.20.10

host (192.168.20.10) not reachable
```

**Result:** EXPECTED FAIL

**Explanation:** VLANs create separate broadcast domains at Layer 2. PC1 (VLAN 10) and PC2 (VLAN 20) are on different subnets and different VLANs. Without a Layer 3 device (router or Layer 3 switch with SVI), inter-VLAN communication is impossible. This is the fundamental purpose of VLAN segmentation — traffic isolation.

---

### Verification 7: MAC Address Table Verification

```bash
SW1# show mac address-table

          Mac Address Table
-------------------------------------------

Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
  10    0050.7966.6800    DYNAMIC     Gi0/1        ; PC1
  10    0050.7966.6802    DYNAMIC     Gi0/0        ; PC3 (learned via trunk)
  20    0050.7966.6801    DYNAMIC     Gi0/2        ; PC2
Total Mac Addresses for this criterion: 3
```

```bash
SW2# show mac address-table

          Mac Address Table
-------------------------------------------

Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
  10    0050.7966.6800    DYNAMIC     Gi0/0        ; PC1 (learned via trunk)
  10    0050.7966.6802    DYNAMIC     Gi0/1        ; PC3
Total Mac Addresses for this criterion: 2
```

**Analysis:** SW1 correctly learns PC1's MAC on Gi0/1 (VLAN 10) and PC3's MAC on Gi0/0 (VLAN 10, via trunk). PC2's MAC is isolated to Gi0/2 (VLAN 20). SW2 only learns VLAN 10 MACs because VLAN 20 is not present on SW2 — the trunk correctly filters VLAN 20 from reaching SW2 since there are no VLAN 20 access ports on SW2.

---

### Verification 8: 802.1Q Tag Capture (Conceptual)

```bash
SW1# show interfaces gigabitEthernet 0/0 switchport

Name: Gi0/0
Switchport: Enabled
Administrative Mode: trunk
Operational Mode: trunk
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: dot1q
Negotiation of Trunking: Off
Access Mode VLAN: 1 (default)
Trunking Native Mode VLAN: 99 (NATIVE)
Administrative Native VLAN tagging: enabled
Voice VLAN: none
Administrative private-vlan host-association: none
Administrative private-vlan mapping: none
Administrative private-vlan trunk native VLAN: none
Administrative private-vlan trunk Native VLAN tagging: none
Administrative private-vlan trunk encapsulation: dot1q
Administrative private-vlan trunk normal VLANs: none
Administrative private-vlan trunk private VLANs: none
Operational private-vlan: none
Trunking VLANs Enabled: 10,20,99
Pruning VLANs Enabled: 2-1001
Capture Mode Disabled
Capture VLANs Allowed: ALL

Protected: false
Unknown unicast blocked: disabled
Unknown multicast blocked: disabled
Appliance trust: none
```

**Key Observations:**
- Negotiation of Trunking is `Off` — DTP is disabled because mode is hardcoded to `trunk`
- Native VLAN is 99, matching SW2
- Only VLANs 10, 20, 99 are enabled on the trunk (principle of least privilege)
- Encapsulation is dot1q (802.1Q) — the only modern standard for Cisco switches

---

## Key Concepts Reinforced

- **VLANs segment broadcast domains at Layer 2.** Each VLAN is a separate logical network. Without a router or Layer 3 switch, devices in different VLANs cannot communicate — this is a security feature, not a limitation.

- **802.1Q trunking multiplexes multiple VLANs across a single physical link.** The 4-byte 802.1Q tag inserted into the Ethernet frame header contains the VLAN ID (12 bits = 4,094 usable VLANs, 1-4094).

- **Native VLAN traffic is untagged across the trunk.** This is required for backward compatibility but creates a security concern if left at default (VLAN 1). Best practice: move native VLAN to an unused, dedicated VLAN (99 in this lab) and prune it from access ports.

- **Access ports belong to exactly one VLAN.** Frames are neither tagged on ingress nor egress at access ports. The switch associates the port's configured VLAN ID with all frames received on that port.

- **DTP should be disabled on all ports.** `switchport mode access` and `switchport mode trunk` disable DTP negotiation, preventing VLAN hopping attacks and ensuring predictable port behavior. Use `switchport nonegotiate` on older IOS versions if needed.

- **PortFast should only be enabled on ports connecting to end hosts.** Enabling PortFast on trunk or switch-to-switch ports can cause spanning tree loops. The `spanning-tree portfast` command adds a BPDU guard safety net on many modern IOS versions.

---

## Common Mistakes & Troubleshooting

| Problem | Symptom | Root Cause | Solution |
|---------|---------|------------|----------|
| Host can't ping same-VLAN neighbor across trunk | 100% packet loss | VLAN missing on one switch | `show vlan brief` on both switches; create missing VLAN |
| Trunk not forming | `show interfaces trunk` shows no output | Native VLAN mismatch; or port set to dynamic auto | Match native VLAN; hardcode `switchport mode trunk` on both ends |
| Native VLAN mismatch warning | CDP/LLDP warning: `%CDP-4-NATIVE_VLAN_MISMATCH` | Different native VLAN each side | Configure identical native VLAN: `switchport trunk native vlan 99` |
| VLAN missing from trunk | Hosts in that VLAN can't communicate across switches | VLAN not in allowed list | `switchport trunk allowed vlan add [vlan-id]` |
| Can't ping even same VLAN locally | `not reachable` on local subnet | Port not assigned to correct VLAN | `show interfaces switchport` — verify `Access Mode VLAN` |
| Ping works when it shouldn't | Cross-VLAN ping succeeds | Misconfigured subnet on host; or router-on-a-stick present | Double-check host IP and subnet mask; verify no L3 device exists |
| DTP forming undesirable trunks | Unexpected trunk ports | Dynamic desirable/auto modes negotiating | Disable DTP: `switchport mode access` or `switchport mode trunk` |

---

## ENCOR Exam Relevance

| Exam Topic | How This Lab Covers It |
|-----------|------------------------|
| VLAN creation and port assignment | Direct hands-on with `vlan` database and `switchport access vlan` |
| 802.1Q trunking | Configured and verified with `show interfaces trunk` |
| Native VLAN security | Best practice implementation using non-default native VLAN |
| DTP security risk | Disabled via hardcoded trunk/access modes |
| Layer 2 broadcast control | Verified cross-VLAN isolation via failed ping test |
| MAC address table operation | Observed dynamic learning per-VLAN via `show mac address-table` |
| PortFast for STP optimization | Enabled on access ports with understanding of scope |

---

## Related Labs

- **Next:** [Lab 02 - VTP Domain Configuration](../lab-02-vtp-domain/) — Automate VLAN propagation across switches
- **Builds Toward:** [Lab 03 - Inter-VLAN Routing](../lab-03-inter-vlan-routing/) — Add Layer 3 capability to enable cross-VLAN communication
- **Previous:** None (first lab in series)

---

## Cisco Documentation References

- [Configuring VLANs - Catalyst 9000 Series Switches](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-6/configuration_guide/vlan/b_176_vlan_9300_cg/configuring_vlan.html)
- [Configuring IEEE 802.1Q Trunking](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-6/configuration_guide/vlan/b_176_vlan_9300_cg/configuring_vlan_trunking.html)
- [Understanding VLAN Trunk Protocol (VTP)](https://www.cisco.com/c/en/us/support/docs/lan-switching/vtp/10558-21.html)
- [Best Practices for Catalyst Switches](https://www.cisco.com/c/en/us/support/docs/switches/catalyst-6500-series-switches/24328-185.html)

---

## Files in This Lab

| File | Description |
|------|-------------|
| `README.md` | This file — complete lab documentation with verification outputs |
| `configs/SW1.cfg` | Complete startup configuration for SW1 |
| `configs/SW2.cfg` | Complete startup configuration for SW2 |
| `topology.png` | EVE-NG topology screenshot (to be added) |

---

## Course Notes Integration

> **From ENCOR Course — Class 1: Switching Fundamentals**
> - VLANs are logical broadcast domains created within a physical switch infrastructure
> - The 802.1Q tag (4 bytes) is inserted after the source MAC address in the Ethernet frame
> - VLAN ID is 12 bits: supports 1-4094 (0 and 4095 reserved)
> - Best practice: Don't use VLAN 1 for anything; create dedicated management and native VLANs

> **From ENCOR Course — Class 2: VLAN Operations & Trunking**
> - DTP is a Cisco-proprietary protocol that negotiates trunking between switches
> - Security risk: DTP can be exploited for VLAN hopping attacks
> - Always disable DTP: `switchport mode access` OR `switchport mode trunk` + `switchport nonegotiate`
> - Native VLAN mismatch causes CDP warnings and potential security issues
> - The `switchport trunk allowed vlan` command should explicitly permit only required VLANs

---

## Time Log

| Phase | Time Spent |
|-------|------------|
| Topology Design & EVE-NG Setup | 15 min |
| VLAN & Port Configuration (SW1) | 10 min |
| VLAN & Port Configuration (SW2) | 10 min |
| End Host IP Configuration | 5 min |
| Verification & Testing | 15 min |
| Documentation (this README) | 45 min |
| **Total** | **~100 min** |

---

*Lab completed as part of CCNP ENCOR (350-401) preparation. All configurations tested and verified in EVE-NG with IOSv-L2 image.*
