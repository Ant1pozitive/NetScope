# NetScope

> Universal diagnostics platform for neural networks.

NetScope is an open-source framework for diagnosing, inspecting, and understanding neural networks.

Instead of only visualizing model internals, NetScope aims to automatically identify model pathologies, explain their causes, and recommend engineering improvements.

The long-term vision is to provide a unified diagnostics platform for modern deep learning architectures including:

- CNN
- Vision Transformer (ViT)
- Transformer
- Diffusion Models
- Mamba
- RWKV
- Graph Neural Networks (GNN)
- Whisper
- CLIP
- Custom PyTorch models

---

# Project Vision

NetScope follows a three-stage diagnostics workflow:

```
Observe
    ↓
Diagnose
    ↓
Recommend
```

Instead of simply exposing tensors or activations, NetScope is designed to answer engineering questions such as:

- Why did the model fail?
- Which layers are underutilized?
- Which neurons are inactive?
- Where do gradients become unstable?
- Which attention heads are redundant?
- Which layers can be pruned?
- Which architectural changes are expected to improve performance?

---

# Current Status

Current milestone:

```
Core Foundation (v0.1)
```

Implemented:

- Project infrastructure
- Configuration system
- Logging
- Lifecycle management
- Component model
- Runtime context
- Registry infrastructure
- Extension interfaces
- Plugin registration
- Testing infrastructure

In Progress:

- Inspector
- Snapshot
- Session
- Model graph
- Hook system

Planned:

- Collectors
- Runtime profiler
- Graph analysis
- Health engine
- Recommendation engine
- HTML reporting
- CLI
- Python SDK

---

# Architecture

```
NetScope

├── Core
├── Registry
├── Runtime
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

# Installation

```bash
pip install -e .
```

---

# Development

Clone the repository:

```bash
git clone https://github.com/Ant1pozitive/NetScope.git
cd netscope
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

Linux/macOS

```bash
source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run formatting:

```bash
ruff check .
ruff format .
```

---

# Roadmap

- ✅ Foundation
- 🚧 Core Runtime
- ⏳ Model Graph
- ⏳ Hook System
- ⏳ Collectors
- ⏳ Runtime Metrics
- ⏳ Serialization
- ⏳ CLI
- ⏳ Health Engine
- ⏳ Recommendation Engine

---

# License

MIT