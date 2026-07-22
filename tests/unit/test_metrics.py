"""DriftAdapt Metrics Unit Tests.

Author: DriftAdapt Contributors
Purpose: Verifies metrics validation, store queries, thread-safety, math calculations, and file exports.
Future Integration: Executed as part of the test suite in CI.
"""

import time
import json
from pathlib import Path
import threading
import pytest


from app.core.metrics import (
    MetricsBus,
    Metric,
    MetricType,
    MetricValidationError,
    aggregate_mean,
    aggregate_max,
    aggregate_min,
    aggregate_median,
    aggregate_stddev,
    aggregate_variance,
    aggregate_latest,
    aggregate_running_average,
    aggregate_grouped,
    MetricPublished,
)
from app.core.config import ConfigManager


@pytest.fixture(autouse=True)
def clean_metrics_bus_store() -> None:
    """Fixture to ensure the MetricsBus singleton store is cleared between tests."""
    bus = MetricsBus()
    bus._store.clear()
    bus.end_experiment()


def test_metrics_schema_validation() -> None:
    """Verifies that MetricRegistry enforces category schema checks."""
    bus = MetricsBus()

    # 1. Register a test schema
    bus.register_schema("test.accuracy", MetricType.ACCURACY, "Test classification accuracy.")
    bus.register_schema("test.loss", MetricType.LOSS, "Test training loss.")

    # 2. Publish valid accuracy
    valid_acc = Metric(name="test.accuracy", value=95.5, module="EvaluationCheck")
    bus.publish(valid_acc)

    # 3. Publish invalid accuracy (out of bounds)
    invalid_acc = Metric(name="test.accuracy", value=150.0, module="EvaluationCheck")
    with pytest.raises(MetricValidationError):
        bus.publish(invalid_acc)

    # 4. Publish invalid loss (negative)
    invalid_loss = Metric(name="test.loss", value=-0.1, module="TrainingCheck")
    with pytest.raises(MetricValidationError):
        bus.publish(invalid_loss)


def test_metrics_store_query_and_history() -> None:
    """Verifies retrieval, filtering, and values history in MetricStore."""
    bus = MetricsBus()

    # Seed values
    bus.publish(Metric(name="val_loss", value=0.5, module="ModelLoader", step=1))
    bus.publish(Metric(name="val_loss", value=0.4, module="ModelLoader", step=2))
    bus.publish(Metric(name="val_loss", value=0.3, module="ModelLoader", step=3, client_id="client_01"))

    # Assert retrieve
    assert len(bus.retrieve("val_loss")) == 3
    assert bus.history("val_loss") == [0.5, 0.4, 0.3]
    assert bus.latest("val_loss").value == 0.3

    # Assert filtering
    filtered_step = bus.filter(name="val_loss", module="ModelLoader")
    assert len(filtered_step) == 3

    filtered_client = bus.filter(client_id="client_01")
    assert len(filtered_client) == 1
    assert filtered_client[0].value == 0.3


def test_asynchronous_publishing() -> None:
    """Verifies that publishing asynchronously is processed in the background."""
    bus = MetricsBus()

    async_metric = Metric(name="val_loss", value=0.99, module="AsyncWorkerTest")
    bus.publish_async(async_metric)

    # Allow background thread worker to pick up and process queue
    time.sleep(1.0)

    latest = bus.latest("val_loss")
    assert latest is not None
    assert latest.value == 0.99


def test_metrics_event_observer() -> None:
    """Verifies that subscribers receive notifications when metrics are published."""
    bus = MetricsBus()

    received_events = []

    def on_publish(event: MetricPublished) -> None:
        received_events.append(event.metric)

    # Subscribe
    bus.subscribe(MetricPublished, on_publish)

    # Publish
    metric = Metric(name="val_loss", value=0.12, module="EventTest")
    bus.publish(metric)

    assert len(received_events) == 1
    assert received_events[0].value == 0.12

    # Unsubscribe
    bus.unsubscribe(MetricPublished, on_publish)
    bus.publish(Metric(name="val_loss", value=0.08, module="EventTest"))
    assert len(received_events) == 1  # count should not increment


def test_metrics_aggregations() -> None:
    """Verifies math aggregations (mean, median, variance, stddev) over Metric objects."""
    metrics = [
        Metric(name="loss", value=10.0, module="A", timestamp=1.0),
        Metric(name="loss", value=20.0, module="B", timestamp=2.0),
        Metric(name="loss", value=30.0, module="A", timestamp=3.0),
    ]

    assert aggregate_mean(metrics) == 20.0
    assert aggregate_max(metrics) == 30.0
    assert aggregate_min(metrics) == 10.0
    assert aggregate_median(metrics) == 20.0
    assert aggregate_variance(metrics) == 100.0
    assert aggregate_stddev(metrics) == 10.0
    assert aggregate_latest(metrics) == 30.0
    assert aggregate_running_average(metrics) == [10.0, 15.0, 20.0]

    # Test grouped aggregation
    grouped = aggregate_grouped(metrics, "module")
    assert len(grouped["A"]) == 2
    assert len(grouped["B"]) == 1


def test_metrics_file_exporters(tmp_path: Path) -> None:
    """Verifies exporting cached metrics to CSV and JSON formats."""
    bus = MetricsBus()

    bus.publish(Metric(name="val_loss", value=0.45, module="ExporterTest", step=5))
    bus.publish(Metric(name="val_loss", value=0.35, module="ExporterTest", step=10))

    csv_out = tmp_path / "metrics.csv"
    json_out = tmp_path / "metrics.json"

    bus.export_all(csv_out, json_out)

    assert csv_out.exists()
    assert json_out.exists()

    # Read json output content
    with open(json_out, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert len(data) == 2
        assert data[0]["name"] == "val_loss"
        assert data[0]["value"] == 0.45


def test_metrics_bus_thread_safety() -> None:
    """Verifies that publishing concurrently from multiple threads does not crash the system."""
    bus = MetricsBus()

    num_threads = 5
    messages_per_thread = 50

    def worker() -> None:
        for idx in range(messages_per_thread):
            m = Metric(name="train_loss", value=0.1, module="ThreadWorker", step=idx)
            bus.publish(m)

    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Assert total records equal expected
    total_expected = num_threads * messages_per_thread
    assert len(bus.retrieve("train_loss")) == total_expected


def test_system_telemetry_collection() -> None:
    """Verifies that the background system telemetry gathers core resource usage."""
    bus = MetricsBus()
    # Explicitly trigger resource collection
    bus.collect_system_metrics()

    # Assert that process time and uptime have been populated
    uptime_metrics = bus.retrieve("system.uptime_seconds")
    proc_metrics = bus.retrieve("system.process_time_seconds")

    assert len(uptime_metrics) >= 1
    assert len(proc_metrics) >= 1
    assert uptime_metrics[0].value >= 0.0

