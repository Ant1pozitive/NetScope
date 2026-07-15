from __future__ import annotations

from pathlib import Path

import pytest
import torch
import torch.nn as nn

from netscope.collector_kind import CollectorKind
from netscope.gradient_collector import GradientCollector
from netscope.protocols import (
    BaseCollectorProtocol,
    CollectorBatchProtocol,
    CollectorRecordProtocol,
    CollectorResultProtocol,
    CollectorSummaryProtocol,
    CollectorTargetProtocol,
)
from netscope.weight_collector import WeightCollector


def test_gradient_collector_collects_nested_gradient_payloads(tmp_path: Path) -> None:
    torch.manual_seed(0)

    collector = GradientCollector(name="gradient_collector")

    payload = {
        "encoder": {
            "layer_1": torch.tensor([[1.0, -2.0], [0.0, 4.0]]),
            "layer_2": torch.zeros(2, 2),
        },
        "decoder": [
            torch.tensor([1.0, -1.0, 3.0]),
            torch.tensor([0.5, 0.0, -0.5]),
        ],
    }

    result = collector.collect(
        payload,
        context={"run_id": "demo"},
        metadata={"suite": "gradient"},
    )

    assert result.collector_kind is CollectorKind.GRADIENT
    assert result.batch_count == 1
    assert result.record_count == 4
    assert result.success_rate == 1.0
    assert collector.last_result is result
    assert len(collector.history) == 1

    batch = result.batches[0]
    assert isinstance(batch, CollectorBatchProtocol)
    assert batch.record_count == 4
    assert batch.success_count == 4
    assert batch.metadata["collector_kind"] == CollectorKind.GRADIENT.value
    assert batch.metadata["zero_tensor_count"] >= 1

    records = result.records
    assert len(records) == 4

    first_record = records[0]
    assert isinstance(first_record, CollectorRecordProtocol)
    assert first_record.value["kind"] == "tensor"
    assert first_record.value["shape"] == [2, 2]
    assert "l2_norm" in first_record.value
    assert "linf_norm" in first_record.value
    assert "positive_fraction" in first_record.value
    assert isinstance(first_record.target, CollectorTargetProtocol)

    summary = result.summary
    assert isinstance(summary, CollectorSummaryProtocol)
    assert summary.collector_name == "gradient_collector"
    assert summary.collector_kind is CollectorKind.GRADIENT
    assert summary.record_count == 4

    payload_dict = result.to_dict()
    assert payload_dict["collector_kind"] == "gradient"
    assert payload_dict["metadata"]["suite"] == "gradient"
    assert payload_dict["summary"]["record_count"] == 4

    saved = result.save_json(tmp_path / "gradient_result.json")
    assert saved.exists()
    assert '"collector_kind"' in saved.read_text(encoding="utf-8")


def test_weight_collector_collects_module_parameters(tmp_path: Path) -> None:
    torch.manual_seed(0)

    model = nn.Sequential(
        nn.Linear(4, 8),
        nn.ReLU(),
        nn.Linear(8, 2),
    )

    collector = WeightCollector(name="weight_collector")
    result = collector.collect(
        model,
        context={"run_id": "demo"},
        metadata={"suite": "weight"},
    )

    assert result.collector_kind is CollectorKind.WEIGHT
    assert result.batch_count == 1
    assert result.record_count == 4
    assert result.success_rate == 1.0
    assert collector.last_result is result
    assert len(collector.history) == 1

    batch = result.batches[0]
    assert isinstance(batch, CollectorBatchProtocol)
    assert batch.record_count == 4
    assert batch.metadata["collector_kind"] == CollectorKind.WEIGHT.value
    assert batch.metadata["module_class"] == "Sequential"
    assert batch.metadata["module_parameter_count"] == 4

    records = result.records
    assert len(records) == 4
    assert all(record.value["kind"] == "tensor" for record in records)
    assert all("l2_norm" in record.value for record in records)
    assert all("sparsity" in record.value for record in records)
    assert any(record.metadata["requires_grad"] is True for record in records)

    summary = result.summary
    assert isinstance(summary, CollectorSummaryProtocol)
    assert summary.collector_name == "weight_collector"
    assert summary.collector_kind is CollectorKind.WEIGHT
    assert summary.record_count == 4

    payload_dict = result.to_dict()
    assert payload_dict["collector_kind"] == "weight"
    assert payload_dict["metadata"]["suite"] == "weight"
    assert payload_dict["summary"]["record_count"] == 4

    saved = result.save_json(tmp_path / "weight_result.json")
    assert saved.exists()
    assert '"collector_kind"' in saved.read_text(encoding="utf-8")


def test_weight_collector_falls_back_to_generic_values() -> None:
    collector = WeightCollector(name="weight_collector")

    result = collector.collect(
        {
            "a": 1,
            "b": 2,
        }
    )

    assert result.record_count == 2
    assert all(record.value["kind"] == "non_tensor" for record in result.records)


def test_collector_protocol_compatibility_for_new_collectors() -> None:
    gradient_collector = GradientCollector(name="gradient_collector")
    weight_collector = WeightCollector(name="weight_collector")

    assert isinstance(gradient_collector, BaseCollectorProtocol)
    assert isinstance(weight_collector, BaseCollectorProtocol)
    assert isinstance(gradient_collector.collect(torch.randn(2, 2)), CollectorResultProtocol)
    assert isinstance(weight_collector.collect(torch.randn(2, 2)), CollectorResultProtocol)