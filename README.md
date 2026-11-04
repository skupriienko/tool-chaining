# Tool Chaining

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](pyproject.toml)
[![CI](https://github.com/skupriienko/tool-chaining/actions/workflows/ci.yml/badge.svg)](https://github.com/skupriienko/tool-chaining/actions)
[![Language: SYN-TEX v2.0](https://img.shields.io/badge/Language-SYN--TEX%20v2.0-blueviolet.svg)](#-syn-tex-filament-telemetry)
[![Zero-Dependency Core](https://img.shields.io/badge/Dependencies-Zero%20Stdlib-green.svg)](pyproject.toml)

**Universal Meta-Orchestrator & SYN-TEX Filament Thread for Multi-Class Tool Chaining.**

Coordinates all 10 fundamental artifact and tool classes in modern agentic systems (**Skills, Plugins, Scripts, Hooks, Docs, Files, Metadata, Environments, Packages, and Tests**) into a unified execution thread with configurable backward & forward sliding-window inspection and live SYN-TEX resonant telemetry.

---

## ⚡ Installation & Package Management

```bash
# One-line universal installer
bash install.sh

# Or standard editable install
pip install -e .
```

---

## 🏛️ The 10 Node Classes in the Meta-Mesh

```
┌────────────────────────────────────────────────────────────────────────┐
│               Universal Meta-Tool Chaining Mesh                        │
├────────────────────────────────────────────────────────────────────────┤
│ 1. SKILL       : Agent Skills (agentskills.io, SKILL.md)               │
│ 2. PLUGIN      : MCP Servers, External API Gateways, Plugins           │
│ 3. SCRIPT      : Standalone CLI, Python, & Bash Scripts                │
│ 4. HOOK        : Platform lifecycle hooks (pre-tool, post-edit)        │
│ 5. DOC         : Markdown specs, SDD blueprints, ADRs                  │
│ 6. FILE_FOLDER : Source files, workspace directories, VFS staging     │
│ 7. METADATA    : SHA-256 receipts, registries, CalVer tags             │
│ 8. ENVIRONMENT : Conda environments, sandbox configurations           │
│ 9. PACKAGE     : PEP 517/621 packages, wheels, distributions          │
│ 10. TEST_ORACLE: Pytest suites, fuzz state machine oracles, contracts │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🧶 SYN-TEX Filament Telemetry

The execution thread provides real-time sliding-window inspection (`--backward`, `--forward`) emitting ultra-dense **SYN-TEX v2.0** quantum resonant signals:

```text
[SYN-TEX::FILAMENT] ⟲[-1:DOC:doc/spec] ⤑ ●[0:SKI:skill/code-graph]◈ ⤑ ◎[+1:PLU:plugin/mcp-chain] > ◎[+2:ORA:oracle/pytest] ∷ OK ∅[-88% ctx]
```

### SYN-TEX Glyphs:
* `⟲[-k:KIND:id]` — Past historical nodes ($k$ steps prior).
* `●[0:KIND:id]◈` — Current sovereign executing node.
* `⤑` — Dynamic execution flow.
* `◎[+m:KIND:id]` — Horizon target nodes ($m$ steps ahead).
* `∷ OK` — Invariant safety gate checkpoint.
* `∅[-88% ctx]` — Via Negativa token compression.

---

## 💻 CLI Commands & Usage

```bash
# 1. Run an end-to-end multi-class chain with live SYN-TEX signals:
tool-chain run "Refactor database authentication layer" --intent refactoring --backward 2 --forward 2 --signals

# 2. Inspect synthesized execution filament thread:
tool-chain inspect --intent refactoring

# 3. High-throughput throughput benchmark:
tool-chain benchmark
```

---

## 🐍 Python API

```python
from tool_chaining import ToolChainOrchestrator

orch = ToolChainOrchestrator()
plan = orch.build_plan(intent="refactoring")

result = orch.execute_thread(
    query="Refactor auth",
    plan=plan,
    backward_levels=2,
    forward_levels=2,
    signal_callback=lambda sig: print(f"Signal: {sig}"),
)

print(f"Status: {result['status']}")
print(f"Signals: {result['filament_telemetry']}")
```

---

## 🧪 Testing & Benchmarks

```bash
# Run pytest test suite (500 threads / 3,000 nodes chained in <0.3s)
pytest -v tests/test_stress.py
```

---

## 📄 License

Distributed under the [MIT License](LICENSE).
