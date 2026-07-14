# NetScope

> Universal diagnostics platform for neural networks.

NetScope is an open-source framework for inspecting, diagnosing, and understanding neural networks.

The project is designed to evolve from model observation toward actionable diagnostics and engineering recommendations.

---

## Current Status

Current milestone:

```text
v0.1 Foundation + Core Facade + Snapshot Model + Snapshot Builder + Graph + Layer Tree + Hook Registry/Manager
````

Implemented so far:

* Project layout
* Configuration system
* Logging subsystem
* Exception hierarchy
* Typing aliases
* Metadata and constants
* Component model
* Lifecycle management
* Identity primitives
* Runtime context
* Runtime environment discovery
* Registry infrastructure
* Resource and workspace infrastructure
* Base extension interfaces
* Session infrastructure
* Inspector facade
* Snapshot data model
* Snapshot builder
* Graph data model primitives
* FX graph builder
* Module metadata
* Layer tree
* Hook primitives
* Safe hook wrapper
* Hook registry
* Hook manager
* Foundation tests

In progress:

* Collectors
* Analyzers
* Runtime metrics
* Serialization
* Reporting pipeline
* CLI

---

## Project Vision

NetScope follows a three-stage workflow:

```text
Observe
    ↓
Diagnose
    ↓
Recommend
```

The long-term goal is to answer engineering questions such as:

* Why did the model fail?
* Which layers are underutilized?
* Which neurons are inactive?
* Where do gradients become unstable?
* Which components are redundant?
* What can be safely pruned?
* Which runtime settings should be changed?

---

## Architecture Overview

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
├── Snapshot Builder
├── Graph
├── Layer Tree
├── Hooks
├── Collectors
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

## Quick Start

### Inspect a Python object

```python
from netscope import Inspector

inspector = Inspector()
result = inspector.inspect({"hello": "world"})

print(result.summary())
print(result.to_dict())
```

### Build a snapshot from an inspection result

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

### Manage hooks safely

```python
from netscope import HookKind, HookManager

manager = HookManager()

# Attach to a torch module later, for example:
# handle = manager.attach_forward(module, callback)
# print(handle.to_dict())
```

### Wrap a hook safely

```python
from netscope import HookKind, HookTarget, SafeHookWrapper

def callback(x):
    return x * 2

wrapper = SafeHookWrapper(
    callback=callback,
    hook_kind=HookKind.CUSTOM,
    target=HookTarget.from_object(callback),
)

result = wrapper(3)
print(result.to_dict())
```

### Work with a snapshot model

```python
from netscope import Snapshot, SnapshotMetadata, SnapshotSummary

snapshot = Snapshot(
    metadata=SnapshotMetadata(
        inspector_name="demo",
        session_id="sess-001",
        session_state="running",
        target_type="dict",
    ),
    summary=SnapshotSummary(
        model_name="example",
        model_type="dict",
    ),
)

print(snapshot.to_dict())
```

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

## Roadmap

* ✅ Foundation
* ✅ Core facade
* ✅ Snapshot model
* ✅ Snapshot builder
* ✅ Graph primitives
* ✅ FX graph builder
* ✅ Module metadata
* ✅ Layer tree
* ✅ Hook primitives
* ✅ Safe hook wrapper
* ✅ Hook registry
* ✅ Hook manager
* ⏳ Collectors
* ⏳ Runtime
* ⏳ Serialization
* ⏳ CLI
* ⏳ Tests

---

## License

MIT