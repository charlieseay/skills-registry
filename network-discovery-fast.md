# Fast Network Discovery — ARP + Topology

**Category:** network  
**Priority:** LOW  
**Created:** 2026-08-20  
**Confidence triggers:** network discovery, ARP scan, nmap, topology, service discovery

**Source:** [8tp/netmap](https://github.com/8tp/netmap), [abrander/pnmap](https://github.com/abrander/pnmap)

## Fast ARP Discovery

```bash
# Sub-second subnet scan
arp-scan --localnet --interface=en0

# vs nmap (10-15s)
nmap -sn 192.168.68.0/24
```

## netmap — TUI Topology

**Features:**
- ARP scanning (sub-second)
- Interactive topology graph in terminal
- Port scanning on demand
- Latency measurements

```bash
# Install
git clone https://github.com/8tp/netmap
cd netmap && make install

# Run
netmap
```

## Passive Discovery (pnmap)

**Use case:** Zero network noise

```bash
# Monitor traffic, don't probe
pnmap --interface en0 --output discovered.json
```

## Integration for Riggins

**Current:** Full nmap scan (slow)  
**Improvement:** Two-tier discovery
1. Fast ARP scan → list hosts
2. Selective deep nmap → only interesting hosts

**References:** [L0P4Map](https://github.com/search?q=L0P4Map) (2025)
