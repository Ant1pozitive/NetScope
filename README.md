# NetScope

> Universal diagnostics platform for neural networks.

NetScope is an engineering toolkit designed to inspect, diagnose, benchmark,
and understand neural networks.

Unlike visualization tools, NetScope focuses on automatic diagnostics,
actionable recommendations, and model health assessment.

---

## Features

- Activation collection
- Gradient collection
- Weight inspection
- Runtime profiling
- FX graph extraction
- Layer diagnostics
- Plugin architecture
- HTML reporting
- Python API
- CLI

---

## Installation

```bash
pip install -e .
```

---

## Example

```python
from netscope import Inspector

report = (
    Inspector(model)
    .analyze()
    .save("report.html")
)
```

---

## Project Status

Current development stage:

```
v0.1 Foundation
```

---

## License

MIT