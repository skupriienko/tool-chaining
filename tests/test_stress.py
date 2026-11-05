"""test_stress.py — Comprehensive Unit & Stress Test Suite for Meta-Tool Chaining."""

import sys
import time
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tool_chaining import (
    BranchKind,
    FilamentBranch,
    FilamentSlidingWindow,
    NodeKind,
    NodeStatus,
    SynTexFormatter,
    ToolChainOrchestrator,
    UniversalFilamentThread,
    UniversalNode,
    UniversalToolMesh,
)


def test_01_models_and_syntex_formatting():
    n_past = UniversalNode("doc/spec", NodeKind.DOC, "Spec", "Spec doc")
    n_curr = UniversalNode("skill/scanner", NodeKind.SKILL, "Scanner", "Security scanner")
    n_next = UniversalNode("plugin/mcp", NodeKind.PLUGIN, "MCP", "MCP sub-loop")

    window = FilamentSlidingWindow(past=[n_past], current=n_curr, future=[n_next])
    signal = SynTexFormatter.format_signal(window, token_saving_ratio=0.88, gate_status="OK")

    assert "[SYN-TEX::FILAMENT]" in signal
    assert "⟲[-1:DOC:doc/spec]" in signal
    assert "●[0:SKI:skill/scanner]◈" in signal
    assert "◎[+1:PLU:plugin/mcp]" in signal
    assert "∷ OK" in signal
    assert "∅[-88% ctx]" in signal


def test_02_sliding_window_levels():
    nodes = [
        UniversalNode(f"node_{i}", NodeKind.SCRIPT, f"Script {i}", f"Task {i}")
        for i in range(6)
    ]
    thread = UniversalFilamentThread(nodes, backward_levels=2, forward_levels=3)

    # Step at index 3
    window, signal = thread.step(3)
    assert len(window.past) == 2
    assert window.past[0].id == "node_1"
    assert window.past[1].id == "node_2"
    assert window.current.id == "node_3"
    assert len(window.future) == 2  # node_4, node_5
    assert window.future[0].id == "node_4"
    assert window.future[1].id == "node_5"


def test_03_orchestrator_execution():
    orch = ToolChainOrchestrator()
    signals = []

    def on_sig(s):
        signals.append(s)

    res = orch.execute_thread(
        "Refactor auth logic",
        plan=orch.build_plan("refactoring"),
        backward_levels=2,
        forward_levels=2,
        signal_callback=on_sig,
    )
    assert res["status"] == "SUCCESS"
    assert res["chain_length"] == 5
    assert len(signals) == 5
    assert len(res["filament_telemetry"]) == 5


def test_04_stress_throughput():
    """Execute 500 multi-class threads under 1.5 seconds."""
    orch = ToolChainOrchestrator()
    t0 = time.time()
    for _ in range(500):
        res = orch.execute_thread("Stress iteration", backward_levels=2, forward_levels=2)
        assert res["status"] == "SUCCESS"
    elapsed = time.time() - t0
    assert elapsed < 1.5, f"Stress test took too long: {elapsed:.2f}s"
    print(f"\nExecuted 500 threads in {elapsed:.3f}s ({500 / elapsed:.1f} threads/sec)")


def test_05_quipu_branched_filament():
    """Verify Incan Quipu pendant cords (similar, critique, probabilistic) in tool-chaining."""
    mesh = UniversalToolMesh()
    mesh.add_edge("skill/scanner", "oracle/pytest", relation="CRITIQUES", weight=1.0)
    mesh.add_edge("skill/scanner", "plugin/mcp-chain", relation="COMPLEMENTS", weight=0.95)

    n_curr = UniversalNode("skill/scanner", NodeKind.SKILL, "Scanner", "Security scanner")
    thread = UniversalFilamentThread([n_curr], backward_levels=1, forward_levels=1, mesh=mesh)

    window, signal = thread.step(0)
    assert len(window.active_branches) == 2
    assert any(b.kind == BranchKind.CRITIQUE for b in window.active_branches)
    assert any(b.kind == BranchKind.SIMILAR for b in window.active_branches)

    assert "[SYN-TEX::FILAMENT]" in signal
    assert "●[0:SKI:skill/scanner]◈" in signal
    assert "⑂" in signal
    assert "⑂CRI~oracle/pytest(1.0)" in signal
    assert "⑂SIM~plugin/mcp-chain(0.9)" in signal


def test_06_security_hardening():
    """Verify input validation, cycle detection, XSS sanitization, and DoS guards."""
    # 1. Null byte and invalid node rejection
    with pytest.raises(ValueError):
        UniversalNode("bad\0node", NodeKind.SKILL, "Bad", "Desc")

    with pytest.raises(ValueError):
        UniversalNode("node_1", NodeKind.SKILL, "Bad", "Desc", capability_weight=float("nan"))

    with pytest.raises(ValueError):
        UniversalNode("node_1", NodeKind.SKILL, "Bad", "Desc", capability_weight=float("inf"))

    # 2. Cycle detection guard
    mesh = UniversalToolMesh()
    n1 = UniversalNode("step_a", NodeKind.SKILL, "A", "Step A")
    n2 = UniversalNode("step_b", NodeKind.SKILL, "B", "Step B")
    mesh.add_node(n1)
    mesh.add_node(n2)
    mesh.add_edge("step_a", "step_b")
    assert not mesh.has_cycle()
    mesh.add_edge("step_b", "step_a")
    assert mesh.has_cycle()

    # 3. Mermaid XSS / HTML sanitization
    n_xss = UniversalNode("xss_node", NodeKind.DOC, '<script>alert("xss")</script>', "Desc")
    mesh_xss = UniversalToolMesh()
    mesh_xss.add_node(n_xss)
    mermaid = mesh_xss.to_mermaid()
    assert "<script>" not in mermaid
    assert "&lt;script&gt;" in mermaid

    # 4. SYN-TEX Delimiter Injection Prevention (CWE-117)
    n_del = UniversalNode("evil\n[INJECTED] ∷ HACK", NodeKind.DOC, "Evil", "Desc")
    thread = UniversalFilamentThread([n_del], backward_levels=1, forward_levels=1)
    _, sig = thread.step(0)
    assert "\n" not in sig
    assert "[INJECTED]" not in sig

    # 5. Query DoS limit
    orch = ToolChainOrchestrator()
    with pytest.raises(ValueError):
        orch.execute_thread("Q" * 70000)
