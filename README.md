# EV-Infrastructure-Monitor

**Fleet-scale monitoring for EV charging infrastructure**

Monitors health, session data, and fault conditions across thousands of EV charging stations — designed for the operational reality of large charging networks where one dead station costs real money.

---

## Scale

Built and tested against networks of **6,000+ endpoints** across multiple geographic regions. Handles the full lifecycle of a charging station from bootup to session close to fault recovery.

---

## What it tracks

**Station Health**
- Online / offline / faulted state per station
- Connector availability (per-connector granularity)
- Hardware fault codes with maintenance ticket auto-creation
- Firmware version drift across fleet

**Session Data**
- Active sessions: energy delivered (kWh), duration, revenue
- Session anomalies: stuck sessions, energy delivery failure, payment timeout
- Historical session export (CSV / JSON) for billing reconciliation

**Network & Comms**
- OCPP 1.6 / 2.0.1 message latency monitoring
- WebSocket connection health per station
- Retry storms and backoff violations

**Alerts**
- P1 (immediate): Station offline, payment system down
- P2 (15 min): Connector fault, session stuck > 4h
- P3 (next business day): Firmware outdated, low utilisation

---

## Architecture

```
Charging Stations (OCPP) ──▶ Central System Simulator ──▶ Monitor Engine
                                                               │
                                                    ┌──────────┴──────────┐
                                                 Dashboard            Alert Engine
                                               (terminal UI)      (email/webhook/SMS)
```

---

## Run it

```bash
git clone https://github.com/SRINIVASAN55/EV-Infrastructure-Monitor
cd EV-Infrastructure-Monitor
pip install -r requirements.txt

python ev_monitor.py --stations stations.json   # monitor from config file
python ev_monitor.py --simulate 50              # simulate 50-station network
python ev_monitor.py --dashboard                # live ops dashboard
python ev_monitor.py --report --days 7          # weekly ops report
```

---

## Why it exists

EV charging networks operate 24/7 across hundreds of locations. Traditional IT monitoring tools don't understand OCPP, don't know what a "stuck session" means, and don't have EV-specific alert logic. This tool does.

---

**Author:** S. Srinivasan · [GitHub](https://github.com/SRINIVASAN55) · [LinkedIn](https://linkedin.com/in/srinivasan132)
