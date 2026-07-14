from __future__ import annotations

from datetime import datetime, timezone

from netscope.base_collector import BaseCollector
from netscope.collector_batch import CollectorBatch
from netscope.collector_config import CollectorConfig
from netscope.collector_kind import CollectorKind
from netscope.collector_record import CollectorRecord
from netscope.collector_result import CollectorResult
from netscope.collector_target import CollectorTarget
from netscope.protocols import (
    BaseCollectorProtocol,
    CollectorBatchProtocol,
    CollectorRecordProtocol,
    CollectorResultProtocol,
    CollectorSummaryProtocol,
    CollectorTargetProtocol,
)


class EchoCollector(BaseCollector):
    collector_kind = CollectorKind.CUSTOM

    def collect(
        self,
        target: object,
        *,
        context: object | None = None,
        metadata: dict[str, object] | None = None,
    ) -> CollectorResult:
        resolved_target = self._new_target(
            target,
            name="echo",
            metadata={"source": "test"},
        )
        record = self._new_record(
            target=resolved_target,
            value=target,
            value_type=type(target).__name__,
            metadata={
                "context_present": context is not None,
                **dict(metadata or {}),
            },
        )
        batch = self._new_batch(
            records=[record],
            metadata={"phase": "collect"},
            started_at=datetime.now(timezone.utc),
        ).complete()
        return self._new_result(
            batches=[batch],
            metadata={"suite": "collectors"},
        )


def test_collector_primitives_to_dict_and_json() -> None:
    target = CollectorTarget.from_object({"hello": "world"}, target_id="target-1")
    record = CollectorRecord(
        collector_kind=CollectorKind.ACTIVATION,
        target=target,
        value={"shape": [1, 2, 3]},
        value_type="dict",
        metadata={"source": "unit"},
    )
    batch = CollectorBatch(
        collector_name="activation",
        collector_kind=CollectorKind.ACTIVATION,
        records=(record,),
    ).complete()
    summary = batch.complete().to_dict()

    assert target.target_id == "target-1"
    assert record.status == "success"
    assert record.target_name == target.name
    assert batch.record_count == 1
    assert batch.success_count == 1
    assert summary["record_count"] == 1
    assert summary["success_count"] == 1


def test_collector_result_and_base_collector_contract() -> None:
    collector = EchoCollector(
        name="echo_collector",
        config=CollectorConfig(
            name="echo_collector",
            collector_kind=CollectorKind.CUSTOM,
            metadata={"suite": "collectors"},
        ),
    )

    result = collector.collect({"value": 42}, context={"run": True})

    assert isinstance(result, CollectorResult)
    assert result.collector_name == "echo_collector"
    assert result.collector_kind is CollectorKind.CUSTOM
    assert result.batch_count == 1
    assert result.record_count == 1
    assert result.success_rate == 1.0
    assert collector.last_result is result
    assert len(collector.history) == 1

    payload = result.to_dict()
    assert payload["summary"]["collector_name"] == "echo_collector"
    assert payload["batches"][0]["record_count"] == 1

    json_text = result.to_json()
    assert '"collector_name"' in json_text


def test_collector_protocol_compatibility() -> None:
    collector = EchoCollector(name="echo_collector")
    result = collector.collect({"x": 1})

    assert isinstance(collector, BaseCollectorProtocol)
    assert isinstance(result.summary, CollectorSummaryProtocol)
    assert isinstance(result.batches[0], CollectorBatchProtocol)
    assert isinstance(result.records[0], CollectorRecordProtocol)
    assert isinstance(result.records[0].target, CollectorTargetProtocol)
    assert isinstance(result, CollectorResultProtocol)