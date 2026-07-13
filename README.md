# NetScope

> Universal diagnostics platform for neural networks.

NetScope is an open-source framework for inspecting, diagnosing, and understanding neural networks.

The project is designed to evolve from model observation toward actionable diagnostics and engineering recommendations.

---

## Current Status

Current milestone:

```text
v0.1 Foundation
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
* Foundation tests

In progress:

* Inspector
* Session
* Snapshot
* Model graph
* Hook system
* Collectors
* Analyzers
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
├── Collectors
├── Graph
├── Hooks
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

### Detect the runtime environment

```python
from netscope import EnvironmentDetector

environment = EnvironmentDetector.detect()
print(environment.to_dict())
```

### Create a workspace

```python
from pathlib import Path
from netscope import Workspace

workspace = Workspace(root_dir=Path.cwd())
workspace.initialize()
workspace.start()

report_path = workspace.save_text(
    name="summary",
    text="NetScope workspace is ready.",
    relative_path="reports/summary.txt",
)

workspace.stop()
workspace.dispose()
```

### Use the registry manager

```python
from netscope import GLOBAL_REGISTRY_MANAGER

GLOBAL_REGISTRY_MANAGER.register(
    namespace="plugin",
    name="example",
    obj=object(),
)
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
* ⏳ Core
* ⏳ Graph
* ⏳ Hooks
* ⏳ Collectors
* ⏳ Runtime
* ⏳ Serialization
* ⏳ CLI
* ⏳ Tests

---

## License

MIT