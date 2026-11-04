"""models.py — Universal 10-Class Node Schema & Filament Thread Models for Tool Chaining."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class NodeKind(StrEnum):
    """The 10 fundamental node classes in the Meta-Tool Mesh."""

    SKILL = "skill"
    PLUGIN = "plugin"
    SCRIPT = "script"
    HOOK = "hook"
    DOC = "doc"
    FILE_FOLDER = "file_folder"
    METADATA = "metadata"
    ENVIRONMENT = "environment"
    PACKAGE = "package"
    TEST_ORACLE = "test_oracle"


class NodeStatus(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    EXECUTED = "EXECUTED"
    HALTED = "HALTED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class UniversalNode:
    """Universal node representing any artifact or tool in the execution mesh."""

    id: str
    kind: NodeKind
    name: str
    description: str
    status: NodeStatus = NodeStatus.PENDING
    capability_weight: float = 1.0
    dominant_invariant: bool = False
    duration_ms: float = 0.0
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind.value,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "capability_weight": round(self.capability_weight, 2),
            "dominant_invariant": self.dominant_invariant,
            "duration_ms": round(self.duration_ms, 2),
            "summary": self.summary,
            "metadata": self.metadata,
        }


@dataclass
class FilamentSlidingWindow:
    """Sliding-window context around the active node on the execution thread."""

    past: list[UniversalNode]
    current: UniversalNode
    future: list[UniversalNode]

    def to_dict(self) -> dict[str, Any]:
        return {
            "past": [n.to_dict() for n in self.past],
            "current": self.current.to_dict(),
            "future": [n.to_dict() for n in self.future],
        }


class SynTexFormatter:
    """SYN-TEX Quantum Resonant Telemetry Generator for Meta-Chaining.

    Uses formal operators from the SYN-TEX v2.0 specification:
    - ⟲ : Backward historical nodes (reminiscence)
    - ● ◈ : Active current execution node (sovereign unit)
    - ⤑ : Dynamic forward transition / flow
    - ◎ : Horizon target nodes (preview)
    - ∷ : Invariant checkpoint gate
    - ∅ : Via Negativa context savings
    """

    @staticmethod
    def format_signal(
        window: FilamentSlidingWindow,
        token_saving_ratio: float = 0.0,
        gate_status: str = "OK",
    ) -> str:
        parts: list[str] = ["[SYN-TEX::FILAMENT]"]

        # 1. Backward Nodes (Past)
        if window.past:
            past_strs = []
            for offset, n in enumerate(reversed(window.past), 1):
                past_strs.append(f"⟲[-{offset}:{n.kind.value[:3].upper()}:{n.id}]")
            parts.append(" ".join(reversed(past_strs)))
            parts.append("⤑")

        # 2. Current Node (Active)
        parts.append(f"●[0:{window.current.kind.value[:3].upper()}:{window.current.id}]◈")

        # 3. Forward Nodes (Future)
        if window.future:
            parts.append("⤑")
            future_strs = []
            for offset, n in enumerate(window.future, 1):
                future_strs.append(f"◎[+{offset}:{n.kind.value[:3].upper()}:{n.id}]")
            parts.append(" > ".join(future_strs))

        # 4. Invariant Gate & Token Savings
        savings_pct = int(token_saving_ratio * 100) if token_saving_ratio > 0 else 0
        parts.append(f"∷ {gate_status} ∅[-{savings_pct}% ctx]")

        return " ".join(parts)
