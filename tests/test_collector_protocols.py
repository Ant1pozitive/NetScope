from __future__ import annotations

from netscope.base_collector import BaseCollector
from netscope.collector_batch import CollectorBatch
from netscope.collector_kind import CollectorKind
from netscope.collector_record import CollectorRecord
from netscope.collector_result import CollectorResult
from netscope.collector_summary import CollectorSummary
from netscope.collector_target import CollectorTarget
from netscope.protocols import (
    BaseCollectorProtocol,
    CollectorBatchProtocol,
    CollectorRecordProtocol,
    CollectorResultProtocol,
    CollectorSummaryProtocol,
    CollectorTargetProtocol,
)


def test_collector_protocols_are_satisfied() -> None:
    target = CollectorTarget.from_object([1, 2, 3], target_id="t1")
    record = CollectorRecord(
        collector_kind=CollectorKind.RUNTIME,
        target=target,
        value={"latency_ms": 12.5},
        value_type="dict",
    )
    batch = CollectorBatch(
        collector_name="runtime",
        collector_kind=CollectorKind.RUNTIME,
        records=(record,),
    ).complete()
    summary = CollectorSummary.from_batches(
        collector_name="runtime",
        collector_kind=CollectorKind.RUNTIME,
        batches=(batch,),
    )
    result = CollectorResult(
        collector_name="runtime",
        collector_kind=CollectorKind.RUNTIME,
        batches=(batch,),
        summary=summary,
    )

    assert isinstance(target, CollectorTargetProtocol)
    assert isinstance(record, CollectorRecordProtocol)
    assert isinstance(batch, CollectorBatchProtocol)
    assert isinstance(summary, CollectorSummaryProtocol)
    assert isinstance(result, CollectorResultProtocol)
    assert isinstance(result, BaseCollectorProtocol) is False


def test_base_collector_protocol_with_real_instance() -> None:
    class DummyCollector(BaseCollector):
        def collect(self, target, *, context=None, metadata=None):
            resolved_target = self._new_target(target, name="dummy")
            record = self._new_record(target=resolved_target, value=target)
            batch = self._new_batch(records=(record,)).complete()
            return self._new_result(batches=(batch,))

    collector = DummyCollector(name="dummy_collector")

    assert isinstance(collector, BaseCollectorProtocol)