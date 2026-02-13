"""
Analytics and Performance Monitoring Tool

This tool tracks and analyzes workflow performance and video metrics.
"""

import json
import os
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsTracker:
    """Track and analyze workflow performance"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.storage_path = self.config.get('storage_path', 'analytics/data')
        self.metrics_file = os.path.join(self.storage_path, 'metrics.json')

        # Create storage directory
        os.makedirs(self.storage_path, exist_ok=True)

        # In-memory metrics
        self.current_session = {
            'start_time': time.time(),
            'events': [],
            'metrics': defaultdict(list)
        }

    def track_event(self, event_type: str, data: Optional[Dict] = None):
        """
        Track a workflow event

        Args:
            event_type: Type of event (e.g., 'video_generated', 'upload_complete')
            data: Optional event data
        """
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'unix_time': time.time(),
            'data': data or {}
        }

        self.current_session['events'].append(event)
        logger.debug(f"Event tracked: {event_type}")

    def track_metric(self, metric_name: str, value: float, tags: Optional[Dict] = None):
        """
        Track a numeric metric

        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for categorization
        """
        metric = {
            'value': value,
            'timestamp': time.time(),
            'tags': tags or {}
        }

        self.current_session['metrics'][metric_name].append(metric)

    def track_duration(self, operation_name: str, duration: float):
        """Track operation duration"""
        self.track_metric(f'{operation_name}_duration', duration, {'unit': 'seconds'})

    def track_success(self, operation_name: str, success: bool):
        """Track operation success/failure"""
        self.track_metric(f'{operation_name}_success', 1.0 if success else 0.0)

    def get_metric_stats(self, metric_name: str) -> Dict:
        """
        Get statistics for a metric

        Args:
            metric_name: Name of the metric

        Returns:
            Dictionary with statistics
        """
        values = [m['value'] for m in self.current_session['metrics'].get(metric_name, [])]

        if not values:
            return {'count': 0}

        return {
            'count': len(values),
            'sum': sum(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0
        }

    def get_success_rate(self, operation_name: str) -> float:
        """
        Calculate success rate for an operation

        Args:
            operation_name: Name of the operation

        Returns:
            Success rate (0-1)
        """
        metric_name = f'{operation_name}_success'
        values = [m['value'] for m in self.current_session['metrics'].get(metric_name, [])]

        if not values:
            return 0.0

        return sum(values) / len(values)

    def get_event_count(self, event_type: Optional[str] = None) -> int:
        """
        Count events of a specific type

        Args:
            event_type: Optional event type filter

        Returns:
            Event count
        """
        if event_type is None:
            return len(self.current_session['events'])

        return sum(1 for e in self.current_session['events'] if e['type'] == event_type)

    def get_events_by_time_range(self, start_time: float, end_time: float) -> List[Dict]:
        """
        Get events within a time range

        Args:
            start_time: Start unix timestamp
            end_time: End unix timestamp

        Returns:
            List of events
        """
        return [
            e for e in self.current_session['events']
            if start_time <= e['unix_time'] <= end_time
        ]

    def calculate_throughput(self, event_type: str, window_seconds: float = 3600) -> float:
        """
        Calculate throughput (events per hour)

        Args:
            event_type: Type of event to count
            window_seconds: Time window in seconds

        Returns:
            Events per hour
        """
        current_time = time.time()
        start_time = current_time - window_seconds

        events = [
            e for e in self.current_session['events']
            if e['type'] == event_type and e['unix_time'] >= start_time
        ]

        hours = window_seconds / 3600
        return len(events) / hours if hours > 0 else 0

    def generate_session_summary(self) -> Dict:
        """
        Generate summary of current session

        Returns:
            Dictionary with session summary
        """
        duration = time.time() - self.current_session['start_time']

        # Count events by type
        event_counts = defaultdict(int)
        for event in self.current_session['events']:
            event_counts[event['type']] += 1

        # Get metric summaries
        metric_summaries = {}
        for metric_name in self.current_session['metrics']:
            metric_summaries[metric_name] = self.get_metric_stats(metric_name)

        return {
            'session_duration': duration,
            'start_time': datetime.fromtimestamp(self.current_session['start_time']).isoformat(),
            'total_events': len(self.current_session['events']),
            'events_by_type': dict(event_counts),
            'metrics': metric_summaries,
            'generated_at': datetime.now().isoformat()
        }

    def generate_performance_report(self) -> str:
        """
        Generate a human-readable performance report

        Returns:
            Formatted report string
        """
        summary = self.generate_session_summary()

        report = []
        report.append("=" * 70)
        report.append("PERFORMANCE REPORT")
        report.append("=" * 70)
        report.append(f"Session Start: {summary['start_time']}")
        report.append(f"Session Duration: {summary['session_duration']:.2f} seconds")
        report.append(f"Total Events: {summary['total_events']}")
        report.append("")

        # Events breakdown
        if summary['events_by_type']:
            report.append("EVENTS BY TYPE:")
            for event_type, count in sorted(summary['events_by_type'].items()):
                report.append(f"  {event_type}: {count}")
            report.append("")

        # Metrics
        if summary['metrics']:
            report.append("METRICS:")
            for metric_name, stats in sorted(summary['metrics'].items()):
                report.append(f"  {metric_name}:")
                report.append(f"    Count: {stats['count']}")
                if stats['count'] > 0:
                    report.append(f"    Mean: {stats['mean']:.2f}")
                    report.append(f"    Min/Max: {stats['min']:.2f} / {stats['max']:.2f}")
                    if stats['count'] > 1:
                        report.append(f"    StdDev: {stats['stdev']:.2f}")
            report.append("")

        # Success rates
        report.append("SUCCESS RATES:")
        operations = set()
        for metric_name in self.current_session['metrics']:
            if metric_name.endswith('_success'):
                operation = metric_name[:-8]  # Remove '_success'
                operations.add(operation)

        for operation in sorted(operations):
            success_rate = self.get_success_rate(operation)
            report.append(f"  {operation}: {success_rate * 100:.1f}%")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)

    def save_session_data(self):
        """Save current session data to file"""
        try:
            summary = self.generate_session_summary()

            # Load existing data
            existing_data = []
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r') as f:
                    existing_data = json.load(f)

            # Append new session
            existing_data.append(summary)

            # Save
            with open(self.metrics_file, 'w') as f:
                json.dump(existing_data, f, indent=2)

            logger.info(f"Session data saved to {self.metrics_file}")

        except Exception as e:
            logger.error(f"Error saving session data: {e}")

    def load_historical_data(self) -> List[Dict]:
        """
        Load historical session data

        Returns:
            List of session summaries
        """
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            return []

    def analyze_trends(self, metric_name: str, num_sessions: int = 10) -> Dict:
        """
        Analyze trends for a metric across sessions

        Args:
            metric_name: Name of the metric
            num_sessions: Number of recent sessions to analyze

        Returns:
            Dictionary with trend analysis
        """
        historical_data = self.load_historical_data()

        if not historical_data:
            return {'error': 'No historical data available'}

        # Get metric values from recent sessions
        values = []
        timestamps = []

        for session in historical_data[-num_sessions:]:
            if metric_name in session.get('metrics', {}):
                stats = session['metrics'][metric_name]
                if stats['count'] > 0:
                    values.append(stats['mean'])
                    timestamps.append(session['start_time'])

        if not values:
            return {'error': f'No data for metric: {metric_name}'}

        # Calculate trend
        if len(values) > 1:
            # Simple linear trend (increasing/decreasing)
            diffs = [values[i] - values[i-1] for i in range(1, len(values))]
            avg_change = statistics.mean(diffs)
            trend = 'increasing' if avg_change > 0 else 'decreasing' if avg_change < 0 else 'stable'
        else:
            trend = 'insufficient_data'

        return {
            'metric': metric_name,
            'sessions_analyzed': len(values),
            'values': values,
            'timestamps': timestamps,
            'trend': trend,
            'average': statistics.mean(values),
            'latest': values[-1] if values else None
        }


class PerformanceTimer:
    """Context manager for timing operations"""

    def __init__(self, tracker: AnalyticsTracker, operation_name: str):
        self.tracker = tracker
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.tracker.track_duration(self.operation_name, duration)

        # Track success/failure
        success = exc_type is None
        self.tracker.track_success(self.operation_name, success)

        if not success:
            self.tracker.track_event('error', {
                'operation': self.operation_name,
                'error_type': exc_type.__name__ if exc_type else None
            })


def main():
    """Example usage"""
    tracker = AnalyticsTracker({'storage_path': 'analytics/data'})

    # Simulate workflow events
    print("Simulating workflow events...")

    # Track video generation
    with PerformanceTimer(tracker, 'video_generation'):
        time.sleep(0.1)  # Simulate work
        tracker.track_event('video_generated', {'quality': 'HD', 'duration': 60})

    # Track more operations
    for i in range(5):
        with PerformanceTimer(tracker, 'thumbnail_creation'):
            time.sleep(0.05)
        tracker.track_event('thumbnail_created')

    # Track uploads
    for i in range(3):
        with PerformanceTimer(tracker, 'video_upload'):
            time.sleep(0.08)
            success = i < 2  # Simulate one failure
            if success:
                tracker.track_event('upload_success', {'platform': 'youtube'})
            else:
                tracker.track_event('upload_failed', {'platform': 'youtube'})

    # Generate and print report
    print("\n" + tracker.generate_performance_report())

    # Save session
    tracker.save_session_data()
    print(f"\nSession data saved to: {tracker.metrics_file}")


if __name__ == '__main__':
    main()
