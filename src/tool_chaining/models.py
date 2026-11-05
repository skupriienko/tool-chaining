"""models.py — Universal 10-Class Node Schema & Filament Thread Models for Tool Chaining."""

from __future__ import annotations

import math
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


class BranchKind(StrEnum):
    """The 3 categories of Quipu auxiliary branches / pendant cords."""

    SIMILAR = "SIMILAR"
    PROBABILISTIC = "PROBABILISTIC"
    CRITIQUE = "CRITIQUE"


@dataclass
class FilamentBranch:
    """Quipu pendant / secondary auxiliary cord attached to a knot."""

    node_id: str
    kind: BranchKind
    affinity: float = 1.0
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "kind": self.kind.value,
            "affinity": round(self.affinity, 2),
            "rationale": self.rationale,
        }


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
    branches: list[FilamentBranch] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate node invariants on initialization."""
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Invalid node id: must be a non-empty string")
        if "\0" in self.id or len(self.id) > 128:
            raise ValueError("Security violation in node id: null byte or exceeds 128 characters")
        if not isinstance(self.name, str) or len(self.name) > 128:
            raise ValueError("Invalid node name: exceeds 128 characters")
        if not math.isfinite(self.capability_weight) or self.capability_weight < 0.0 or self.capability_weight > 100.0:
            raise ValueError("Invalid capability_weight: must be a finite float between 0.0 and 100.0")
        if not math.isfinite(self.duration_ms) or self.duration_ms < 0.0:
            raise ValueError("Invalid duration_ms: must be a finite non-negative float")

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
            "branches": [b.to_dict() for b in self.branches],
            "metadata": self.metadata,
        }


@dataclass
class FilamentSlidingWindow:
    """Sliding-window context around the active node on the execution thread, including Quipu branches."""

    past: list[UniversalNode]
    current: UniversalNode
    future: list[UniversalNode]

    @property
    def active_branches(self) -> list[FilamentBranch]:
        return self.current.branches

    def to_dict(self) -> dict[str, Any]:
        return {
            "past": [n.to_dict() for n in self.past],
            "current": self.current.to_dict(),
            "future": [n.to_dict() for n in self.future],
            "active_branches": [b.to_dict() for b in self.current.branches],
        }


def _clean_token(t: str) -> str:
    """Sanitize token to prevent SYN-TEX signal delimiter injection (CWE-117)."""
    return "".join(ch for ch in str(t) if ch not in "\r\n\t[]⑂●◈∷∅")[:64]


class SynTexFormatter:
    """SYN-TEX Quantum Resonant Telemetry Generator for Meta-Chaining.

    Uses formal operators from the SYN-TEX v2.0 specification:
    - ⟲ : Backward historical nodes (reminiscence / primary cord past)
    - ● ◈ : Active current execution node (sovereign knot)
    - ⤑ : Dynamic forward transition / flow
    - ◎ : Horizon target nodes (preview / primary cord future)
    - ⑂ : Branched pendant cord (Quipu secondary strand: similar/probable tools)
    - ∷ : Invariant checkpoint gate
    - ∅ : Via Negativa context savings
    """

    @staticmethod
    def format_signal(
        window: FilamentSlidingWindow,
        token_saving_ratio: float = 0.0,
        gate_status: str = "OK",
        include_branches: bool = True,
    ) -> str:
        parts: list[str] = ["[SYN-TEX::FILAMENT]"]

        # 1. Backward Nodes (Past)
        if window.past:
            past_strs = []
            for offset, n in enumerate(reversed(window.past), 1):
                clean_id = _clean_token(n.id)
                parts_str = f"⟲[-{offset}:{n.kind.value[:3].upper()}:{clean_id}]"
                past_strs.append(parts_str)
            parts.append(" ".join(reversed(past_strs)))
            parts.append("⤑")

        # 2. Current Node (Active)
        clean_curr_id = _clean_token(window.current.id)
        parts.append(f"●[0:{window.current.kind.value[:3].upper()}:{clean_curr_id}]◈")

        # 2b. Quipu Branches / Pendants (Auxiliary cords)
        if include_branches and window.current.branches:
            branch_tokens = []
            for b in window.current.branches[:3]:
                clean_b_id = _clean_token(b.node_id)
                branch_tokens.append(f"⑂{b.kind.value[:3]}~{clean_b_id}({b.affinity:.1f})")
            parts.append(f"[{' '.join(branch_tokens)}]")

        # 3. Forward Nodes (Future)
        if window.future:
            parts.append("⤑")
            future_strs = []
            for offset, n in enumerate(window.future, 1):
                clean_f_id = _clean_token(n.id)
                future_strs.append(f"◎[+{offset}:{n.kind.value[:3].upper()}:{clean_f_id}]")
            parts.append(" > ".join(future_strs))

        # 4. Invariant Gate & Token Savings
        savings_pct = int(token_saving_ratio * 100) if token_saving_ratio > 0 else 0
        clean_gate = _clean_token(gate_status)
        parts.append(f"∷ {clean_gate} ∅[-{savings_pct}% ctx]")

        return " ".join(parts)
