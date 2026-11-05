"""mesh.py — Universal Meta-Tool Dependency Graph & Topological Engine."""

from __future__ import annotations

import html
import math
import re
from typing import TYPE_CHECKING, Any

from .models import BranchKind, FilamentBranch

if TYPE_CHECKING:
    from .models import UniversalNode

SAFE_ID_REGEX = re.compile(r"[^a-zA-Z0-9_]")


class UniversalToolMesh:
    """Directed dependency graph spanning all 10 artifact and tool classes."""

    def __init__(self):
        self.nodes: dict[str, UniversalNode] = {}
        self.edges: list[dict[str, Any]] = []

    def add_node(self, node: UniversalNode) -> None:
        if not node.id or len(node.id) > 128:
            raise ValueError("Invalid node id")
        self.nodes[node.id] = node

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation: str = "PIPES_TO",
        weight: float = 1.0,
        rationale: str = "",
    ) -> None:
        if not source_id or not target_id:
            raise ValueError("source_id and target_id must be non-empty")
        if not math.isfinite(weight) or weight < 0.0 or weight > 100.0:
            raise ValueError("Invalid weight: must be a finite float between 0.0 and 100.0")

        clean_rel = SAFE_ID_REGEX.sub("", relation.upper()) or "PIPES_TO"
        clean_rationale = "".join(ch for ch in rationale if ch >= " ")[:512]

        self.edges.append(
            {
                "source": source_id,
                "target": target_id,
                "relation": clean_rel,
                "weight": weight,
                "rationale": clean_rationale,
            }
        )

    def has_cycle(self) -> bool:
        """Detect whether the directed mesh contains any cycles (infinite loop guard)."""
        visited: dict[str, int] = {}  # 0: unvisited, 1: visiting, 2: visited

        adj: dict[str, list[str]] = {nid: [] for nid in self.nodes}
        for e in self.edges:
            if e["source"] in adj:
                adj[e["source"]].append(e["target"])

        def dfs(u: str) -> bool:
            visited[u] = 1
            for v in adj.get(u, []):
                if visited.get(v, 0) == 1:
                    return True
                if visited.get(v, 0) == 0 and dfs(v):
                    return True
            visited[u] = 2
            return False

        return any(visited.get(node_id, 0) == 0 and dfs(node_id) for node_id in self.nodes)

    def get_node(self, node_id: str) -> UniversalNode | None:
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str, relation: str | None = None) -> list[UniversalNode]:
        targets = []
        for e in self.edges:
            if e["source"] == node_id:
                if relation is None or e["relation"] == relation:
                    if e["target"] in self.nodes:
                        targets.append(self.nodes[e["target"]])
        return targets

    def get_branches(self, node_id: str) -> list[FilamentBranch]:
        """Discover secondary pendant cords (similar, alternative, critique) for Quipu filament."""
        branches: list[FilamentBranch] = []
        for e in self.edges:
            if e["source"] == node_id:
                rel = e.get("relation", "PIPES_TO")
                target = e.get("target", "")
                weight = float(e.get("weight", 1.0))
                rationale = e.get("rationale", "")

                if rel in ("COMPLEMENTS", "PIPES_TO", "SIMILAR"):
                    branches.append(
                        FilamentBranch(
                            node_id=target,
                            kind=BranchKind.SIMILAR,
                            affinity=weight,
                            rationale=rationale or "Complementary partner tool",
                        )
                    )
                elif rel in ("OPPOSES", "CRITIQUES"):
                    branches.append(
                        FilamentBranch(
                            node_id=target,
                            kind=BranchKind.CRITIQUE,
                            affinity=weight,
                            rationale=rationale or "Adversarial quality gate",
                        )
                    )
                else:
                    branches.append(
                        FilamentBranch(
                            node_id=target,
                            kind=BranchKind.PROBABILISTIC,
                            affinity=weight,
                            rationale=rationale or "Contextually probable step",
                        )
                    )

        # Contextual fallback heuristic if no edges exist
        if not branches:
            if "search" in node_id or "doc" in node_id:
                branches.append(
                    FilamentBranch(
                        node_id="skill/bounded-search",
                        kind=BranchKind.PROBABILISTIC,
                        affinity=0.85,
                        rationale="High probability information retrieval branch",
                    )
                )
            elif "gate" in node_id or "oracle" in node_id or "test" in node_id:
                branches.append(
                    FilamentBranch(
                        node_id="oracle/pytest",
                        kind=BranchKind.CRITIQUE,
                        affinity=1.0,
                        rationale="Mandatory regression gate branch",
                    )
                )
            elif "plugin" in node_id or "mcp" in node_id:
                branches.append(
                    FilamentBranch(
                        node_id="plugin/mcp-chain",
                        kind=BranchKind.SIMILAR,
                        affinity=0.90,
                        rationale="Parallel MCP execution capability",
                    )
                )
        return branches

    def summary(self) -> dict[str, Any]:
        by_kind: dict[str, int] = {}
        for n in self.nodes.values():
            by_kind[n.kind.value] = by_kind.get(n.kind.value, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes_by_kind": by_kind,
        }

    def to_mermaid(self) -> str:
        """Render dependency graph to Mermaid flowchart with full XSS and delimiter sanitization."""
        lines = ["```mermaid", "flowchart TD"]
        for n in self.nodes.values():
            safe_id = SAFE_ID_REGEX.sub("_", n.id)
            clean_name = html.escape(n.name, quote=True).replace("[", "&#91;").replace("]", "&#93;")
            lines.append(f'    {safe_id}["[{n.kind.value.upper()}] {clean_name}"]')
        for e in self.edges:
            s_id = SAFE_ID_REGEX.sub("_", e["source"])
            t_id = SAFE_ID_REGEX.sub("_", e["target"])
            rel_label = html.escape(e["relation"], quote=True)
            lines.append(f"    {s_id} -->|{rel_label}| {t_id}")
        lines.append("```")
        return "\n".join(lines)
