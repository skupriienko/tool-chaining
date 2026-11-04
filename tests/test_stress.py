"""test_stress.py — Comprehensive Unit & Stress Test Suite for Meta-Tool Chaining."""

import time
import pytest
from tool_chaining import (
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
