"""
Run from project root: PYTHONPATH=src python3 -m cli.main
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# Allow `python3 src/cli/main.py` from repo root without PYTHONPATH
_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import psycopg

from config.database import DatabaseConfig
from services.traffic_service import TrafficService


def _safe_int(value: str) -> Optional[int]:
    try:
        return int(value)
    except ValueError:
        return None


def run_cli() -> None:
    DatabaseConfig.initialize()
    service = TrafficService()

    try:
        while True:
            print("\n=== Traffic Management System ===")
            print("1. Look up intersection by ID")
            print("2. Show high-incident intersections (last 90 days)")
            print("3. System performance metrics")
            print("4. Incident counts by severity")
            print("5. Exit")
            choice = input("Select option: ").strip()

            if choice == "5":
                print("Goodbye.")
                break
            if choice not in ("1", "2", "3", "4"):
                print("Invalid option. Please choose 1-5.")
                continue

            try:
                if choice == "1":
                    iid = _safe_int(input("Intersection ID: ").strip())
                    if iid is None or iid <= 0:
                        print("Invalid intersection ID.")
                        continue
                    inter = service.get_intersection_by_id(iid)
                    if not inter:
                        print("Intersection not found.")
                        continue
                    print(inter)

                elif choice == "2":
                    lim = _safe_int(
                        input("How many rows to show [default 20]: ").strip() or "20"
                    )
                    if lim is None or lim <= 0:
                        print("Invalid limit.")
                        continue
                    rows = service.get_high_incident_intersections(limit=lim)
                    if not rows:
                        print("No data returned.")
                        continue
                    print("\n=== High-Incident Intersections (Last 90 Days) ===\n")
                    print(
                        f"{'Rank':<5} {'Intersection':<28} {'Zone':<18} "
                        f"{'Incidents':<10} {'Sensors':<8}"
                    )
                    print("-" * 75)
                    for rank, row in enumerate(rows, start=1):
                        name = (row.get("intersection_name") or "")[:26]
                        zone = (row.get("zone") or "N/A")[:16]
                        inc = row.get("incidents", 0)
                        sen = row.get("sensors", 0)
                        print(f"{rank:<5} {name:<28} {zone:<18} {inc!s:<10} {sen!s:<8}")

                elif choice == "3":
                    m = service.get_system_metrics()
                    print("\n=== System Performance Metrics ===\n")
                    print(f"Total incidents                 : {m['total_incidents']}")
                    print(f"Total intersections             : {m['total_intersections']}")
                    print(f"Total sensors                   : {m['total_sensors']}")
                    print(
                        "Avg sensors per intersection    : "
                        f"{m['avg_sensors_per_intersection']:.2f}"
                    )
                    om = m.get("open_maintenance_tasks")
                    if om is None:
                        print(
                            "Open maintenance tasks          : "
                            "(table/column unavailable)"
                        )
                    else:
                        print(f"Open maintenance tasks          : {om}")

                elif choice == "4":
                    rows = service.get_incident_counts_by_severity()
                    if not rows:
                        print("No incident data.")
                        continue
                    print("\n=== Incident Counts by Severity ===\n")
                    print(f"{'Severity':<22} {'Count':>8}")
                    print("-" * 32)
                    for row in rows:
                        sev = row.get("severity_level") or "N/A"
                        cnt = row.get("incident_count", 0)
                        print(f"{str(sev):<22} {int(cnt):>8}")
            except psycopg.OperationalError:
                print(
                    "\nCannot connect to PostgreSQL (connection refused or unreachable)."
                )
                print(
                    "Fix: start the server locally, or set DB_HOST / DB_PORT / DB_NAME "
                    "in a .env file."
                )
            except psycopg.Error as exc:
                print(f"\nDatabase error: {exc}")
    finally:
        DatabaseConfig.close_all()


if __name__ == "__main__":
    run_cli()
