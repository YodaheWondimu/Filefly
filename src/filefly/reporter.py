# Made by Yodahe Wondimu
# A simple script to generate a report based on data from the SQLite database and telemetry metrics.

from .storage import Storage
from .telemetry import Telemetry

storage = Storage()
telemetry = Telemetry()
summary = storage.summary()
snapshot = telemetry.snapshot()

# Abstracted report generation so it can be called from the CLI or other contexts.
def generate_report():
    print("=== Filefly Telemetry Report ===")
    print(f"Total Events Recorded: {summary['total_events']}")
    print(f"Average stabilization time by extension: {summary['avg_stabilization_by_extension']} seconds")
    print(f"Average stabilization time overall: {summary['avg_stabilization_total']} seconds")
    print(f"Telemetry snapshot: {snapshot}")

generate_report()