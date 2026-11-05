"""filament.py — Universal Execution Thread Engine for Meta-Tool Chaining."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from .models import FilamentSlidingWindow, NodeStatus, SynTexFormatter, UniversalNode

if TYPE_CHECKING:
    from .mesh import UniversalToolMesh


class UniversalFilamentThread:
    """Manages the full ordered execution thread of multi-class nodes with sliding window inspection."""

    def __init__(
        self,
        nodes: list[UniversalNode],
        *,
        backward_levels: int = 1,
        forward_levels: int = 2,
        token_saving_ratio: float = 0.0,
        signal_callback: Callable[[str], None] | None = None,
        mesh: UniversalToolMesh | None = None,
    ):
        self.nodes = list(nodes)
        self.backward_levels = max(0, backward_levels)
        self.forward_levels = max(0, forward_levels)
        self.token_saving_ratio = token_saving_ratio
        self.signal_callback = signal_callback
        self.mesh = mesh
        self.telemetry_history: list[str] = []

        if self.mesh:
            for n in self.nodes:
                if not n.branches:
                    n.branches = self.mesh.get_branches(n.id)

    def step(self, current_index: int) -> tuple[FilamentSlidingWindow, str]:
        """Activate the node at current_index and emit a SYN-TEX telemetry signal."""
        if not (0 <= current_index < len(self.nodes)):
            err_msg = f"Filament node index out of bounds: {current_index}"
            raise IndexError(err_msg)

        current_node = self.nodes[current_index]
        current_node.status = NodeStatus.ACTIVE

        start_idx = max(0, current_index - self.backward_levels)
        past_nodes = self.nodes[start_idx:current_index]

        end_idx = min(len(self.nodes), current_index + 1 + self.forward_levels)
        future_nodes = self.nodes[current_index + 1 : end_idx]

        window = FilamentSlidingWindow(past=past_nodes, current=current_node, future=future_nodes)
        signal = SynTexFormatter.format_signal(
            window=window,
            token_saving_ratio=self.token_saving_ratio,
            gate_status="OK",
        )

        self.telemetry_history.append(signal)
        if self.signal_callback:
            self.signal_callback(signal)

        return window, signal

    def complete_step(
        self,
        current_index: int,
        status: NodeStatus = NodeStatus.EXECUTED,
        summary: str = "",
        duration_ms: float = 0.0,
    ) -> None:
        """Mark the node at current_index as completed with telemetry metadata."""
        if 0 <= current_index < len(self.nodes):
            node = self.nodes[current_index]
            node.status = status
            node.summary = summary
            node.duration_ms = duration_ms

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_nodes": len(self.nodes),
            "backward_levels": self.backward_levels,
            "forward_levels": self.forward_levels,
            "telemetry_signals": self.telemetry_history,
            "nodes": [n.to_dict() for n in self.nodes],
        }
