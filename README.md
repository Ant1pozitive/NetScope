# NetScope

> A diagnostics platform for neural networks.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-red)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-pre--alpha-orange)

NetScope is an open-source engineering toolkit for inspecting, analyzing, and diagnosing neural networks.

It is designed to move beyond simple visualization and help answer practical questions about model behavior, structure, efficiency, and stability.

---

## What NetScope is for

NetScope helps you understand:

- why a model made a mistake;
- which layers are underused;
- where gradients become unstable;
- which parameters are redundant;
- which parts of the model may be pruned or optimized;
- how a model's internal structure changes over time.

The project is built around a diagnostic workflow:

```text
Observe → Diagnose → Recommend
```

---

## What is included right now

NetScope currently provides the core foundation for the platform:

* configuration and logging
* exception hierarchy
* runtime context and environment discovery
* registry infrastructure
* session infrastructure
* inspector facade
* snapshot data model
* snapshot builder
* graph primitives
* FX graph builder
* module metadata
* layer tree
* hook primitives
* safe hook wrapper
* hook registry
* hook manager
* forward and backward hook adapters
* collector primitives
* collector base contract
* activation collector
* gradient collector
* weight collector
* runtime collector
* runtime metric models
* runtime snapshot and series models

This is an early engineering foundation, not a finished user-facing analytics suite yet.

---

## Design principles

NetScope is being built with a few clear principles:

* **Framework-aware, but not framework-locked**
* **Observation-first**
* **Immutable data models where possible**
* **Plugin-friendly architecture**
* **Structured outputs that can be serialized**
* **Clean separation between acquisition, analysis, and reporting**

---

## Architecture overview

```text
NetScope

├── Core
├── Context
├── Environment
├── Registry
├── Resources
├── Interfaces
├── Sessions
├── Inspector
├── Snapshots
├── Graph
├── Layer Tree
├── Hooks
├── Collectors
├── Runtime
├── Analyzers
├── Serialization
├── Reporting
└── CLI
```

---

## Installation

```bash
pip install -e .
```

For development dependencies:

```bash
pip install -e ".[dev]"
```

---

## Quick start

### Inspect an object

```python
from netscope import Inspector

inspector = Inspector()
result = inspector.inspect({"hello": "world"})

print(result.summary())
print(result.to_dict())
```

### Build a snapshot

```python
from netscope import Inspector, SnapshotBuilder

inspector = Inspector()
result = inspector.inspect({"hello": "world"})

snapshot = SnapshotBuilder().from_result(result)
print(snapshot.to_dict())
```

### Build an FX graph

```python
import torch.nn as nn
from netscope import FXGraphBuilder

model = nn.Sequential(
    nn.Linear(4, 8),
    nn.ReLU(),
    nn.Linear(8, 2),
)

graph = FXGraphBuilder().build(model)
print(graph.to_dict())
```

### Build a layer tree

```python
import torch.nn as nn
from netscope import LayerTreeBuilder

model = nn.Sequential(
    nn.Linear(4, 8),
    nn.ReLU(),
    nn.Linear(8, 2),
)

tree = LayerTreeBuilder().build(model)
print(tree.to_dict())
```

### Attach hooks recursively

```python
import torch.nn as nn
from netscope import ForwardHookAdapter, HookManager

model = nn.Sequential(
    nn.Linear(4, 8),
    nn.ReLU(),
    nn.Linear(8, 2),
)

manager = HookManager(module=model)
adapter = ForwardHookAdapter(manager)

def callback(module, inputs, output):
    return output

group = adapter.attach(model, callback)
print(group.snapshot())
```

### Collect activation summaries

```python
import torch
from netscope import ActivationCollector

collector = ActivationCollector(name="activation_collector")

payload = {
    "layer_1": torch.randn(2, 8),
    "layer_2": torch.randn(2, 4),
}

result = collector.collect(payload)
print(result.to_dict())
```

### Collect gradient summaries

```python
import torch
from netscope import GradientCollector

collector = GradientCollector(name="gradient_collector")

payload = {
    "layer_1": torch.randn(2, 8),
    "layer_2": torch.tensor([[0.0, 1.0], [-1.0, 2.0]]),
}

result = collector.collect(payload)
print(result.to_dict())
```

### Collect weight summaries from a module

```python
import torch.nn as nn
from netscope import WeightCollector

model = nn.Sequential(
    nn.Linear(4, 8),
    nn.ReLU(),
    nn.Linear(8, 2),
)

collector = WeightCollector(name="weight_collector")
result = collector.collect(model)

print(result.to_dict())
```

### Collect runtime telemetry

```python
from dataclasses import dataclass
from netscope import RuntimeCollector

@dataclass
class RuntimeState:
    latency_ms: float
    cpu_percent: float
    memory_mb: float
    throughput: float

state = RuntimeState(
    latency_ms=12.5,
    cpu_percent=48.0,
    memory_mb=812.3,
    throughput=153.0,
)

collector = RuntimeCollector(name="runtime_collector")
result = collector.collect(state)

print(result.to_dict())
```

### Build runtime series and snapshots

```python
from netscope import RuntimeMetric, RuntimeMetricKind, RuntimeSample, RuntimeSeries, RuntimeSnapshot

metric = RuntimeMetric(
    name="latency_ms",
    kind=RuntimeMetricKind.LATENCY,
    value=12.5,
    unit="ms",
    scope="batch",
    source="profiler",
)

sample = RuntimeSample.from_metric(metric, step=1, batch_index=0)

series = RuntimeSeries(
    series_id="latency-series",
    name="latency_ms",
    kind=RuntimeMetricKind.LATENCY,
    samples=(sample,),
)

snapshot = RuntimeSnapshot(
    name="runtime_snapshot",
    metrics=(metric,),
    samples=(sample,),
    series=(series,),
)

print(snapshot.to_dict())
```

---

## Project status

NetScope is under active development.

Current focus areas:

* serialization
* reporting
* CLI
* test expansion

---

## Roadmap

* [x] Foundation
* [x] Core facade
* [x] Snapshot model
* [x] Snapshot builder
* [x] Graph primitives
* [x] FX graph builder
* [x] Module metadata
* [x] Layer tree
* [x] Hook primitives
* [x] Hook registry and manager
* [x] Forward/backward hook adapters
* [x] Collector primitives
* [x] Collector base contract
* [x] Activation collector
* [x] Gradient collector
* [x] Weight collector
* [x] Runtime collector
* [x] Runtime metric models
* [x] Runtime snapshot and series models
* [ ] Serialization
* [ ] Reporting
* [ ] CLI
* [ ] Broader test coverage

---

## Development

Run tests:

```bash
pytest
```

Run formatting and linting:

```bash
ruff format .
ruff check .
```

---

## License

MIT