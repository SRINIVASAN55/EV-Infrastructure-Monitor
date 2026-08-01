<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=5&height=80&text=⚡%20EV%20Infrastructure%20Monitor&fontSize=28&fontColor=ffffff" width="100%"/>

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![No Dependencies](https://img.shields.io/badge/stdlib-only-green?style=for-the-badge)]()
[![Endpoints](https://img.shields.io/badge/Endpoints-6000+-orange?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Enterprise EV charging infrastructure monitoring & ops automation.**  
Monitors thousands of EV charging endpoints via REST API health checks, detects offline/fault/degraded stations, opens incidents, collects enriched logs, and generates operational reports — entirely on Python stdlib.

*Inspired by real NOC operations at scale.*

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| ⚡ **Multi-threaded Polling** | Concurrent health checks across 6000+ endpoints |
| 🏥 **Health Check Engine** | REST API polling with timeout, retry, and error classification |
| 🚨 **Incident Management** | Auto-opens P1/P2/P3 incidents; resolves on recovery |
| 📊 **Live Dashboard** | Real-time terminal dashboard with fleet status breakdown |
| 📝 **Log Collector** | Enriched JSONL logs per station per check cycle |
| 📈 **Ops Reports** | JSON reports with fleet availability %, status breakdown |
| 🔄 **State Machine** | ONLINE → OFFLINE → FAULT → DEGRADED → RECOVERY |
| 🎭 **Simulator Mode** | Built-in station simulator — no hardware needed to demo |

---

## 🚀 Quick Start

```bash
git clone https://github.com/SRINIVASAN55/EV-Infrastructure-Monitor.git
cd EV-Infrastructure-Monitor

# Demo mode — simulates 50 EV charging stations
python ev_monitor.py

# Scale up — 200 stations, 15s interval
python ev_monitor.py -n 200 -i 15 -w 50

# Real API mode
python ev_monitor.py --api-base http://your-charger-api.com --no-sim -n 6000
```

---

## 📊 Live Dashboard

```
  Fleet Size : 50 endpoints  |  Open Incidents: 3

  ● ONLINE     :    38 (76%)     ⚡ CHARGING   :    6
  ✖ OFFLINE    :     4           ~ DEGRADED    :    2
  ⚠ FAULT      :     2           ⚡ Total Power : 842 kW
    Avg Response:    47 ms

  ─────────────────────────────────────────────────
  ⚠ PROBLEM STATIONS (8):
  [OFFLINE  ] EVSE-0023  Station-0023  Chennai - Adyar     (failures: 3)
  [FAULT    ] EVSE-0041  Station-0041  Bangalore - Whitefield  (failures: 2)
  [P2] INC-3A7F2C: Station-0041 — FAULT
```

---

## 🔁 Incident Severity

| Status | Severity | Description |
|---|---|---|
| OFFLINE | **P1** | Station unreachable — immediate action |
| FAULT | **P2** | Hardware fault detected — investigate |
| DEGRADED | **P3** | Partial failure — monitor closely |

---

## 📄 License

MIT License © 2024 [Srinivasan S](https://github.com/SRINIVASAN55)
