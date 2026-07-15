from __future__ import annotations

from pathlib import Path

import pytest
import torch

from netscope.activation_collector import ActivationCollector
from netscope.collector_kind import CollectorKind
from netscope.protocols import (
    BaseCollectorProtocol,
    CollectorBatchProtocol,
    CollectorRecordProtocol,
    CollectorResultProtocol,
    CollectorSummaryProtocol,
    CollectorTargetProtocol,
)


def test_activation_collector_collects_nested_tensor_payloads(tmp_path: Path) -> None:
    torch.manual_seed(0)

    collector = ActivationCollector(name="activation_collector")

    payload = {
        "encoder": {
            "layer_1": torch.randn(2, 4),
            "layer_2": torch.zeros(2, 4),
        },
        "decoder": [
            torch.ones(1, 3),
            torch.tensor([1.0, 2.0, 3.0]),
        ],
    }

    result = collector.collect(
        payload,
        context={"run_id": "demo"},
        metadata={"suite": "activation"},
    )

    assert result.collector_kind is CollectorKind.ACTIVATION
    assert result.batch_count == 1
    assert result.record_count == 4
    assert result.success_rate == 1.0
    assert collector.last_result is result
    assert len(collector.history) == 1

    batch = result.batches[0]
    assert isinstance(batch, CollectorBatchProtocol)
    assert batch.record_count == 4
    assert batch.success_count == 4
    assert batch.metadata["collector_kind"] == CollectorKind.ACTIVATION.value

    records = result.records
    assert len(records) == 4

    first_record = records[0]
    assert isinstance(first_record, CollectorRecordProtocol)
    assert first_record.value["kind"] == "tensor"
    assert first_record.value["shape"] == [2, 4]
    assert "mean" in first_record.value
    assert "std" in first_record.value
    assert isinstance(first_record.target, CollectorTargetProtocol)

    summary = result.summary
    assert isinstance(summary, CollectorSummaryProtocol)
    assert summary.collector_name == "activation_collector"
    assert summary.collector_kind is CollectorKind.ACTIVATION
    assert summary.record_count == 4

    payload_dict = result.to_dict()
    assert payload_dict["collector_kind"] == "activation"
    assert payload_dict["metadata"]["suite"] == "activation"
    assert payload_dict["summary"]["record_count"] == 4

    saved = result.save_json(tmp_path / "activation_result.json")
    assert saved.exists()
    assert '"collector_kind"' in saved.read_text(encoding="utf-8")


def test_activation_collector_collects_non_tensor_leaf_values() -> None:
    collector = ActivationCollector(name="activation_collector")

    result = collector.collect(
        {
            "layer": "not-a-tensor",
            "value": 42,
        }
    )

    assert result.record_count == 2
    assert all(record.value["kind"] == "non_tensor" for record in result.records)
    assert all(record.value_type == "activation_leaf" for record in result.records)


def test_activation_collector_protocol_compatibility() -> None:
    collector = ActivationCollector(name="activation_collector")
    result = collector.collect(torch.randn(2, 2))

    assert isinstance(collector, BaseCollectorProtocol)
    assert isinstance(result, CollectorResultProtocol)
    assert isinstance(result.summary, CollectorSummaryProtocol)
    assert isinstance(result.batches[0], CollectorBatchProtocol)
    assert isinstance(result.records[0], CollectorRecordProtocol)
    assert isinstance(result.records[0].target, CollectorTargetProtocol)