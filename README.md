# EV-Infrastructure-Monitor

![CI](https://github.com/SRINIVASAN55/EV-Infrastructure-Monitor/actions/workflows/ci.yml/badge.svg) ![License: MIT](https://img.shields.io/badge/License-MIT-green.svg) ![Python](https://img.shields.io/badge/python-3.8+-blue.svg)



**Fleet-scale monitoring for EV charging infrastructure**

Monitors health, session data, and fault conditions across thousands of EV charging stations — designed for the operational reality of large charging networks where one dead station costs real money.

---

## Scale

Built and tested against networks of **6,000+ endpoints** across multiple geographic regions. Handles the full lifecycle of a charging station from bootup to session close to fault recovery.

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Python | 3.8 or higher |
| OS | Linux, macOS, Windows |
| Network | Access to charging station API or OCPP endpoint |

```bash
python3 --version    # must be 3.8+
```

---

## Installation

```bash
git clone https://github.com/SRINIVASAN55/EV-Infrastructure-Monitor.git
cd EV-Infrastructure-Monitor
pip install -r requirements.txt
```

---

## Running It

### Simulate a network — no real hardware needed
```bash
# Simulate 50 charging stations (default)
python3 ev_monitor.py

# Simulate a larger fleet
python3 ev_monitor.py --count 200
python3 ev_monitor.py -n 200

# Simulate 500 stations with 40 worker threads for speed
python3 ev_monitor.py --count 500 --workers 40
```
This is the best way to evaluate the tool — it generates realistic station data, faults, and sessions without needing actual OCPP hardware.

### Change the monitoring interval
```bash
# Check every 10 seconds (more responsive)
python3 ev_monitor.py --interval 10
python3 ev_monitor.py -i 10

# Check every 60 seconds (lower load)
python3 ev_monitor.py --interval 60
```

### Connect to a real OCPP API
```bash
# Point at your central system API
python3 ev_monitor.py --api-base http://your-ocpp-server.com/api --no-sim

# Combine with custom interval and worker count
python3 ev_monitor.py --api-base http://your-ocpp-server.com/api --no-sim --count 100 --workers 20
```

### Save reports to a custom directory
```bash
python3 ev_monitor.py --output ./reports/
python3 ev_monitor.py -o /var/log/ev-monitor/
```

---

## All CLI Flags

| Flag | Short | Description | Default | Example |
|------|-------|-------------|---------|---------|
| `--count` | `-n` | Number of endpoints to monitor | `50` | `-n 200` |
| `--interval` | `-i` | Check interval in seconds | `30` | `-i 10` |
| `--workers` | `-w` | Concurrent worker threads | `20` | `-w 40` |
| `--api-base` | | Real API base URL | — | `--api-base http://server/api` |
| `--no-sim` | | Disable simulator, use real API only | — | `--no-sim` |
| `--output` | `-o` | Output directory for reports | `.` | `-o ./reports` |

---

## What It Monitors

**Station Health**
- Online / offline / faulted state per station
- Connector availability (per-connector granularity)
- Hardware fault codes with auto-escalation
- Firmware version drift across fleet

**Session Data**
- Active sessions: energy delivered (kWh), duration, revenue
- Session anomalies: stuck sessions, energy delivery failure
- Historical export for billing reconciliation

**Alerts**
- P1 (immediate): Station offline, payment system down
- P2 (15 min): Connector fault, session stuck
- P3 (next business day): Firmware outdated, low utilisation

---

## Architecture

```
Charging Stations (OCPP) ──▶ Central System / Simulator ──▶ Monitor Engine
                                                               │
                                                    ┌──────────┴──────────┐
                                                 Dashboard            Alert Engine
                                               (terminal UI)      (email/webhook)
```

---

## Troubleshooting

**`Connection refused` to API endpoint**
→ Check that your OCPP central system is running and the URL is correct. Try `curl http://your-server/api` first.

**Monitor is slow with many stations**
→ Increase workers: `-w 50`. Each worker handles one station concurrently.

**Reports not appearing**
→ Check the output directory exists and is writable: `mkdir -p ./reports`

**Want to test without any setup?**
→ Just run `python3 ev_monitor.py` with no flags — it simulates 50 stations automatically.

---

**Author:** S. Srinivasan · [GitHub](https://github.com/SRINIVASAN55) · [LinkedIn](https://linkedin.com/in/srinivasan132)
