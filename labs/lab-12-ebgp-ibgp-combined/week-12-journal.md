# Week 12 - eBGP + iBGP Combined (12 Routers)

## Lab Summary

Built a 12-router topology combining iBGP and eBGP in EVE-NG. The core AS 100 runs iBGP with dual Route Reflectors (R4, R5) using peer-groups, while two parallel eBGP chains extend outward through six external ASes and converge at R12 (AS 1200). OSPF process 100 serves as the IGP underlay for iBGP loopback reachability.

## What I Learned

- eBGP requires physical interface IPs for peering by default - loopback peering only works with ebgp-multihop and a route to the loopback
- next-hop-self must be applied at the peer-group level, not individual neighbors, when using peer-groups on Route Reflectors - otherwise only one client gets rewritten next-hops
- Peer-groups simplify Route Reflector config significantly - one set of commands covers all clients
- Dual Route Reflectors provide redundancy - both R4 and R5 reflect the same routes to all clients
- The BGP table on clients shows two AS-PATHs to R12's prefix, one through each eBGP chain
- Always double-check remote-as values - a typo (AS 500 vs AS 100) silently prevents the session from establishing

## Bugs Fixed

1. R4 eBGP neighbor used R6's loopback (6.6.6.6) instead of physical IP (10.4.6.6)
2. R7 had remote-as 500 instead of remote-as 100 for R5
3. R12 was missing the network statement for 12.12.12.12/32
4. next-hop-self was on individual neighbor instead of peer-group RR2
5. R11 had the R12 link on e0/1 instead of e0/2 (wrong interface)

## ENCOR Topics Covered

- BGP path selection and AS-PATH
- iBGP Route Reflectors with peer-groups
- eBGP peering with physical IPs
- next-hop-self behavior
- OSPF as IGP underlay for iBGP
- Dual RR redundancy design

## Next Steps

- Add Local Preference route-maps on R4 and R5 to influence path selection
- Practice show ip bgp interpretation with multiple paths
