# Made by Yodahe Wondimu
# Collects and summarizes metrics about file events.

from collections import defaultdict

class Telemetry:
    def __init__(self):
        self.metrics = {
            "total_events": 0,
            "created": 0,
            "modified": 0,
            "deleted": 0,
            "moved": 0,
            "stabilization_times": [],
            "filetype_counts": defaultdict(int),
        }

    def record_event(self, event_type, file_path, extension=None):
        self.metrics["total_events"] += 1
        if event_type in self.metrics:
            self.metrics[event_type] += 1
        
        if extension:
            self.metrics["filetype_counts"][extension] += 1

    def record_stabilization(self, duration):
        self.metrics["stabilization_times"].append(duration)

    def average_stabilization_time(self):
        times = self.metrics["stabilization_times"]
        if not times:
            return 0.0
        return sum(times) / len(times)

    def snapshot(self):
        return {
            **self.metrics,
            "avg_stabilization_time": self.average_stabilization_time()
        }