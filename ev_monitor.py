#!/usr/bin/env python3
"""
EV-Infrastructure-Monitor — Enterprise EV Charging Endpoint Monitor
Author: Srinivasan S (SRINIVASAN55)

Monitors 6000+ EV charging endpoints:
  - Health checks via REST API polling
  - Offline / degraded / fault detection
  - Latency and response time tracking
  - Automated log collection & enrichment
  - Alert escalation with incident reports
  - Operational runbook automation
"""

import os
import sys
import json
import time
import uuid
import random
import logging
import argparse
import threading
import urllib.request
import urllib.error
from datetime import datetime
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ─── Colors ────────────────────────────────────────────────────────────────────
class C:
    RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"
    CYAN="\033[96m"; BLUE="\033[94m"; BOLD="\033[1m"; RESET="\033[0m"

BANNER = f"""{C.GREEN}{C.BOLD}
  ███████╗██╗   ██╗    ██╗███╗   ██╗███████╗██████╗  █████╗
  ██╔════╝██║   ██║    ██║████╗  ██║██╔════╝██╔══██╗██╔══██╗
  █████╗  ██║   ██║    ██║██╔██╗ ██║█████╗  ██████╔╝███████║
  ██╔══╝  ╚██╗ ██╔╝    ██║██║╚██╗██║██╔══╝  ██╔══██╗██╔══██║
  ███████╗ ╚████╔╝     ██║██║ ╚████║██║     ██║  ██║██║  ██║
  ╚══════╝  ╚═══╝      ╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝
          Enterprise EV Charging Infrastructure Monitor v1.0
                      Author: SRINIVASAN55 | ChargePoint-style
{C.RESET}"""

# ─── Data Models ───────────────────────────────────────────────────────────────
@dataclass
class EVEndpoint:
    station_id: str
    name: str
    location: str
    ip: str
    port: int = 8080
    status: str = "UNKNOWN"       # ONLINE / OFFLINE / FAULT / DEGRADED / CHARGING
    last_seen: Optional[str] = None
    response_ms: float = 0.0
    consecutive_failures: int = 0
    connector_status: str = "AVAILABLE"
    firmware_version: str = "v2.1.0"
    power_kw: float = 0.0
    alerts: List[str] = field(default_factory=list)
    history: deque = field(default_factory=lambda: deque(maxlen=50))

@dataclass
class Incident:
    incident_id: str
    station_id: str
    station_name: str
    severity: str       # P1 / P2 / P3
    title: str
    description: str
    created_at: str
    resolved: bool = False
    resolved_at: Optional[str] = None

@dataclass
class HealthCheckResult:
    station_id: str
    success: bool
    status_code: int = 0
    response_ms: float = 0.0
    payload: dict = field(default_factory=dict)
    error: str = ""
    timestamp: str = ""
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

# ─── Simulator (mimics real API responses) ─────────────────────────────────────
class EVStationSimulator:
    """Simulates EV charging station API responses for demo/testing."""
    STATUSES = ["ONLINE", "ONLINE", "ONLINE", "ONLINE", "CHARGING",
                "CHARGING", "FAULT", "OFFLINE", "DEGRADED"]
    LOCATIONS = [
        "Chennai - Anna Nagar", "Chennai - T. Nagar", "Chennai - Adyar",
        "Bangalore - Koramangala", "Bangalore - Whitefield",
        "Mumbai - BKC", "Delhi - Connaught Place", "Hyderabad - HITEC City",
        "Pune - Hinjewadi", "Coimbatore - RS Puram"
    ]

    @staticmethod
    def get_station_response(station_id: str) -> dict:
        """Returns simulated API payload for a station health check."""
        # Inject occasional faults for realism
        seed = hash(station_id + str(int(time.time() / 30))) % 100
        if seed < 3:
            raise ConnectionError("Connection refused")
        if seed < 6:
            raise TimeoutError("Request timeout")

        status = random.choices(
            ["ONLINE", "CHARGING", "FAULT", "OFFLINE", "DEGRADED"],
            weights=[55, 25, 8, 7, 5]
        )[0]
        return {
            "station_id": station_id,
            "status": status,
            "connector_status": "IN_USE" if status == "CHARGING" else "AVAILABLE",
            "power_kw": round(random.uniform(7.2, 150.0), 1) if status == "CHARGING" else 0,
            "voltage_v": round(random.uniform(220, 240), 1),
            "current_a": round(random.uniform(16, 63), 1) if status == "CHARGING" else 0,
            "temperature_c": round(random.uniform(28, 45), 1),
            "firmware": "v2.1.4",
            "uptime_hours": random.randint(0, 8760),
            "sessions_today": random.randint(0, 40),
            "energy_today_kwh": round(random.uniform(0, 500), 1),
            "last_heartbeat": datetime.now().isoformat(),
            "errors": [] if status not in ("FAULT",) else [
                random.choice(["GROUND_FAULT", "OVERCURRENT", "COMM_TIMEOUT",
                               "CONTACTOR_FAIL", "TEMP_HIGH"])
            ]
        }

# ─── Health Checker ─────────────────────────────────────────────────────────────
class HealthChecker:
    def __init__(self, use_simulator: bool = True, api_base: str = ""):
        self.use_sim = use_simulator
        self.api_base = api_base.rstrip("/")
        self.timeout = 5

    def check(self, station: EVEndpoint) -> HealthCheckResult:
        t0 = time.time()
        if self.use_sim:
            try:
                payload = EVStationSimulator.get_station_response(station.station_id)
                ms = (time.time() - t0) * 1000 + random.uniform(10, 120)
                return HealthCheckResult(
                    station_id=station.station_id, success=True,
                    status_code=200, response_ms=ms, payload=payload
                )
            except (ConnectionError, TimeoutError) as e:
                ms = (time.time() - t0) * 1000
                return HealthCheckResult(
                    station_id=station.station_id, success=False,
                    response_ms=ms, error=str(e)
                )
        else:
            # Real API call
            url = f"{self.api_base}/api/v1/stations/{station.station_id}/health"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "EV-Monitor/1.0"})
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    ms = (time.time() - t0) * 1000
                    payload = json.loads(r.read())
                    return HealthCheckResult(
                        station_id=station.station_id, success=True,
                        status_code=r.status, response_ms=ms, payload=payload
                    )
            except Exception as e:
                ms = (time.time() - t0) * 1000
                return HealthCheckResult(
                    station_id=station.station_id, success=False,
                    response_ms=ms, error=str(e)
                )

# ─── Log Collector ──────────────────────────────────────────────────────────────
class LogCollector:
    """Collects and enriches logs from EV stations."""
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def collect(self, station: EVEndpoint, result: HealthCheckResult) -> dict:
        entry = {
            "timestamp": result.timestamp,
            "station_id": station.station_id,
            "station_name": station.name,
            "location": station.location,
            "status": result.payload.get("status", "UNKNOWN") if result.success else "UNREACHABLE",
            "response_ms": round(result.response_ms, 1),
            "success": result.success,
            "error": result.error,
            "connector": result.payload.get("connector_status", ""),
            "power_kw": result.payload.get("power_kw", 0),
            "errors": result.payload.get("errors", []),
        }
        # Write to daily log file
        date = datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(self.log_dir, f"ev_monitor_{date}.jsonl")
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

# ─── Incident Manager ───────────────────────────────────────────────────────────
class IncidentManager:
    SEVERITY_MAP = {
        "OFFLINE":  "P1",
        "FAULT":    "P2",
        "DEGRADED": "P3",
    }
    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self._lock = threading.Lock()

    def open(self, station: EVEndpoint, status: str) -> Optional[Incident]:
        key = f"{station.station_id}-{status}"
        with self._lock:
            if key in self.incidents and not self.incidents[key].resolved:
                return None  # Already open
            sev = self.SEVERITY_MAP.get(status, "P3")
            inc = Incident(
                incident_id=f"INC-{uuid.uuid4().hex[:6].upper()}",
                station_id=station.station_id,
                station_name=station.name,
                severity=sev,
                title=f"{station.name} — {status}",
                description=(
                    f"Station {station.station_id} at {station.location} "
                    f"reported status: {status}. "
                    f"Consecutive failures: {station.consecutive_failures}. "
                    f"Last seen online: {station.last_seen or 'Unknown'}."
                ),
                created_at=datetime.now().isoformat()
            )
            self.incidents[key] = inc
            return inc

    def resolve(self, station_id: str):
        with self._lock:
            for key, inc in self.incidents.items():
                if inc.station_id == station_id and not inc.resolved:
                    inc.resolved = True
                    inc.resolved_at = datetime.now().isoformat()

    def open_count(self) -> int:
        return sum(1 for i in self.incidents.values() if not i.resolved)

# ─── Main Monitor ───────────────────────────────────────────────────────────────
class EVInfraMonitor:
    def __init__(self, station_count: int = 50, interval: int = 30,
                 use_simulator: bool = True, api_base: str = "",
                 workers: int = 20, output_dir: str = "."):
        self.station_count = station_count
        self.interval      = interval
        self.output_dir    = output_dir
        self.checker       = HealthChecker(use_simulator, api_base)
        self.collector     = LogCollector(os.path.join(output_dir, "logs"))
        self.incidents     = IncidentManager()
        self.stations: List[EVEndpoint] = []
        self.stats         = defaultdict(int)
        self._lock         = threading.Lock()
        self._running      = True
        self._workers      = workers
        self._sem          = threading.Semaphore(workers)
        self._check_count  = 0

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)-8s %(message)s",
            handlers=[
                logging.FileHandler(os.path.join(output_dir, "ev_monitor.log")),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.log = logging.getLogger("EVMonitor")
        self._generate_stations()

    def _generate_stations(self):
        """Generate simulated station fleet."""
        locs = EVStationSimulator.LOCATIONS
        for i in range(self.station_count):
            loc = locs[i % len(locs)]
            self.stations.append(EVEndpoint(
                station_id=f"EVSE-{i+1:04d}",
                name=f"Station-{i+1:04d}",
                location=loc,
                ip=f"10.{(i//254)%256}.{i%254+1}.1",
                port=8080,
            ))
        self.log.info(f"Fleet loaded: {len(self.stations)} endpoints")

    def _process_result(self, station: EVEndpoint, result: HealthCheckResult):
        log_entry = self.collector.collect(station, result)
        prev_status = station.status

        if result.success:
            new_status = result.payload.get("status", "ONLINE")
            station.consecutive_failures = 0
            station.last_seen = result.timestamp
            station.response_ms = result.response_ms
            station.power_kw = result.payload.get("power_kw", 0)
            station.connector_status = result.payload.get("connector_status", "")

            if new_status not in ("FAULT",) and prev_status in ("OFFLINE", "FAULT", "DEGRADED"):
                self.incidents.resolve(station.station_id)
                self.log.info(f"[RECOVERY] {station.station_id} {station.name} → {new_status}")
        else:
            station.consecutive_failures += 1
            new_status = "OFFLINE"

        station.status = new_status
        station.history.append({"ts": result.timestamp, "status": new_status, "ms": result.response_ms})

        with self._lock:
            self.stats[new_status] += 1
            self._check_count += 1

        # Open incidents for bad states
        if new_status in ("OFFLINE", "FAULT", "DEGRADED") and station.consecutive_failures >= 2:
            inc = self.incidents.open(station, new_status)
            if inc:
                color = {"P1": C.RED+C.BOLD, "P2": C.RED, "P3": C.YELLOW}.get(inc.severity, C.RESET)
                self.log.warning(f"[{inc.severity}] {inc.incident_id}: {inc.title}")
                print(f"  {color}[{inc.severity}] {inc.incident_id}: {inc.title}{C.RESET}")

    def _check_station(self, station: EVEndpoint):
        with self._sem:
            result = self.checker.check(station)
            self._process_result(station, result)

    def _run_check_cycle(self):
        """Run one check cycle across all stations using threads."""
        threads = []
        self.stats.clear()
        for station in self.stations:
            t = threading.Thread(target=self._check_station, args=(station,), daemon=True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join(timeout=10)

    def _print_dashboard(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = len(self.stations)
        online   = sum(1 for s in self.stations if s.status in ("ONLINE","CHARGING"))
        charging = sum(1 for s in self.stations if s.status == "CHARGING")
        offline  = sum(1 for s in self.stations if s.status == "OFFLINE")
        fault    = sum(1 for s in self.stations if s.status == "FAULT")
        degraded = sum(1 for s in self.stations if s.status == "DEGRADED")
        avg_lat  = sum(s.response_ms for s in self.stations if s.response_ms > 0) / max(online, 1)
        total_kw = sum(s.power_kw for s in self.stations)

        print(f"\033[2J\033[H", end="")
        print(BANNER)
        print(f"  {C.BOLD}Last Check : {now}  |  Total Checks: {self._check_count:,}{C.RESET}")
        print(f"  {C.BOLD}Fleet Size : {total:,} endpoints  |  Open Incidents: {self.incidents.open_count()}{C.RESET}")
        print(f"  {'─'*65}")
        print(f"  {C.GREEN}{'● ONLINE':<14}: {online:>5} ({online/total*100:.0f}%){C.RESET}   "
              f"{C.CYAN}{'⚡ CHARGING':<14}: {charging:>5}{C.RESET}")
        print(f"  {C.RED}{'✖ OFFLINE':<14}: {offline:>5}{C.RESET}   "
              f"{C.YELLOW}{'~ DEGRADED':<14}: {degraded:>5}{C.RESET}")
        print(f"  {C.RED+C.BOLD}{'⚠ FAULT':<14}: {fault:>5}{C.RESET}   "
              f"{C.CYAN}{'⚡ Total Power':<14}: {total_kw:.0f} kW{C.RESET}")
        print(f"  {C.CYAN}{'Avg Response':<14}: {avg_lat:.0f} ms{C.RESET}")
        print(f"  {'─'*65}")

        # Show worst stations
        bad = [s for s in self.stations if s.status in ("OFFLINE","FAULT","DEGRADED")]
        if bad:
            print(f"\n  {C.RED}{C.BOLD}  ⚠ PROBLEM STATIONS ({len(bad)}):{C.RESET}")
            for s in bad[:10]:
                color = {"OFFLINE": C.RED+C.BOLD, "FAULT": C.RED, "DEGRADED": C.YELLOW}.get(s.status, C.RESET)
                print(f"  {color}  [{s.status:<9}]{C.RESET} {s.station_id}  {s.name:<16}  {s.location}  (failures: {s.consecutive_failures})")
        else:
            print(f"\n  {C.GREEN}  ✓ All stations operating normally{C.RESET}")

        print(f"\n  {C.CYAN}Check interval: {self.interval}s  |  Workers: {self._workers}  |  Press Ctrl+C to stop{C.RESET}\n")

    def generate_report(self):
        """Generate operational report."""
        total = len(self.stations)
        online = sum(1 for s in self.stations if s.status in ("ONLINE","CHARGING"))
        report = {
            "generated": datetime.now().isoformat(),
            "fleet_size": total,
            "availability_pct": round(online / total * 100, 2),
            "status_breakdown": {
                s: sum(1 for st in self.stations if st.status == s)
                for s in ["ONLINE","CHARGING","OFFLINE","FAULT","DEGRADED"]
            },
            "open_incidents": self.incidents.open_count(),
            "total_checks": self._check_count,
            "total_power_kw": round(sum(s.power_kw for s in self.stations), 1),
            "problem_stations": [
                {"id": s.station_id, "name": s.name, "location": s.location,
                 "status": s.status, "failures": s.consecutive_failures}
                for s in self.stations if s.status in ("OFFLINE","FAULT","DEGRADED")
            ][:20]
        }
        path = os.path.join(self.output_dir, f"ev_report_{int(time.time())}.json")
        with open(path, "w") as f:
            json.dump(report, f, indent=2)
        return path, report

    def run(self):
        print(BANNER)
        self.log.info(f"Starting EV Infrastructure Monitor — {len(self.stations)} endpoints")
        try:
            while self._running:
                self._run_check_cycle()
                self._print_dashboard()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.log.info("Stopping...")
            self._running = False
        finally:
            path, report = self.generate_report()
            print(f"\n{C.GREEN}[✓] Report saved: {path}{C.RESET}")
            print(f"    Fleet availability: {report['availability_pct']}%")
            print(f"    Total checks run: {self._check_count:,}")

def main():
    parser = argparse.ArgumentParser(
        description="EV-Infrastructure-Monitor — Enterprise EV Charging Endpoint Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ev_monitor.py                         # Demo mode: 50 simulated stations
  python ev_monitor.py -n 200 -i 15           # 200 stations, 15s interval
  python ev_monitor.py --api-base http://your-api.com --no-sim  # Real API mode
        """
    )
    parser.add_argument("-n","--count",    type=int, default=50,  help="Number of endpoints to monitor (default: 50)")
    parser.add_argument("-i","--interval", type=int, default=30,  help="Check interval in seconds (default: 30)")
    parser.add_argument("-w","--workers",  type=int, default=20,  help="Concurrent worker threads (default: 20)")
    parser.add_argument("--api-base",      default="",            help="Real API base URL (e.g. http://api.chargepoint.com)")
    parser.add_argument("--no-sim",        action="store_true",   help="Disable simulator — use real API")
    parser.add_argument("-o","--output",   default=".",           help="Output directory for reports and logs")
    args = parser.parse_args()

    monitor = EVInfraMonitor(
        station_count=args.count,
        interval=args.interval,
        use_simulator=not args.no_sim,
        api_base=args.api_base,
        workers=args.workers,
        output_dir=args.output
    )
    monitor.run()

if __name__ == "__main__":
    main()
