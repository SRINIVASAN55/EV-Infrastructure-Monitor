<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=5,10&height=60&text=⚡+EV+INFRASTRUCTURE+MONITOR&fontSize=22&fontColor=ffffff&fontAlignY=65" width="100%"/>

<br/>

[![Endpoints](https://img.shields.io/badge/Scale-6000%2B_Endpoints-FFD700?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![Threads](https://img.shields.io/badge/Multithreaded-20%2B_Workers-39ff14?style=for-the-badge)]()
[![Incidents](https://img.shields.io/badge/P1%2FP2%2FP3-Incident_Management-ff4444?style=for-the-badge)]()

**Enterprise-grade monitoring for EV charging infrastructure.**  
*Inspired by real NOC operations. Built for scale.*

</div>

---

## 🏭 The Scale Problem

> You're running a fleet of 6,000+ EV charging stations across 50 cities.  
> At any given moment, dozens are offline, degraded, or in fault.  
> Your NOC team gets 300 alerts a day. Manual triage takes hours.  

**EV-Infrastructure-Monitor** solves this with automated health polling, smart incident classification, and actionable ops reports — so your team focuses on what matters.

---

## 📊 Live Fleet Dashboard

```
  Last Check: 2024-01-15 12:34:01  |  Total Checks: 8,420  |  Open Incidents: 7
  ─────────────────────────────────────────────────────────────────────
  ● ONLINE     :   4,312  (71%)     ⚡ CHARGING   :  1,089
  ✖ OFFLINE    :     234            ~ DEGRADED    :     98
  ⚠ FAULT      :      67            ⚡ Total Power : 89,432 kW
    Avg Response:      43 ms

  ⚠ PROBLEM STATIONS (10 shown):
  [OFFLINE  ] EVSE-0023   Chennai - Adyar          (failures: 3)
  [FAULT    ] EVSE-0041   Bangalore - Whitefield    (failures: 2)
  [DEGRADED ] EVSE-0112   Mumbai - BKC              (failures: 1)

  [P1] INC-3A7F2C: Station-0023 — OFFLINE → Escalated to L2
  [P2] INC-B91E44: Station-0041 — FAULT   → GROUND_FAULT error
```

---

## 🚨 Incident Severity System

```
Station reports OFFLINE (3 consecutive failures)
         │
         ▼
    ┌─────────────┐
    │  P1 Incident│ ← Immediate escalation, L2/L3 alert
    │  EV is DOWN │
    └─────────────┘

Station reports FAULT (hardware error code)
         │
         ▼
    ┌─────────────┐
    │  P2 Incident│ ← Field technician dispatch
    │  GROUND_FAULT│
    └─────────────┘

Station recovers → Incident auto-resolved ✓
```

---

## 🚀 Run It

```bash
git clone https://github.com/SRINIVASAN55/EV-Infrastructure-Monitor
cd EV-Infrastructure-Monitor

# Demo mode — simulates 50 EV stations instantly
python ev_monitor.py

# Scale to 500 stations, 15s interval, 50 workers
python ev_monitor.py -n 500 -i 15 -w 50

# Real API mode (your ChargePoint/OCPP API)
python ev_monitor.py --api-base https://api.your-network.com --no-sim -n 6000
```

---

## 📄 Ops Report (JSON)

Generated after every run:

```json
{
  "fleet_size": 6000,
  "availability_pct": 91.4,
  "status_breakdown": {
    "ONLINE": 4312, "CHARGING": 1089,
    "OFFLINE": 234, "FAULT": 67, "DEGRADED": 98
  },
  "open_incidents": 7,
  "total_power_kw": 89432
}
```

---

## 🗂️ Log Structure

Every check cycle writes to `logs/ev_monitor_YYYY-MM-DD.jsonl`:

```jsonl
{"timestamp":"...","station_id":"EVSE-0023","status":"OFFLINE","response_ms":0,"errors":[]}
{"timestamp":"...","station_id":"EVSE-0041","status":"FAULT","errors":["GROUND_FAULT"]}
```

---

<p align="center">
Built by <a href="https://github.com/SRINIVASAN55">SRINIVASAN55</a> ·
<a href="https://linkedin.com/in/srinivasan132">LinkedIn</a> ·
Inspired by real NOC operations @ ChargePoint
</p>
