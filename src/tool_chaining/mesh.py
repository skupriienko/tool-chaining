"""mesh.py — Universal Meta-Tool Dependency Graph & Topological Engine."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .models import BranchKind, FilamentBranch

if TYPE_CHECKING:
    from .models import UniversalNode


class UniversalToolMesh:
    """Directed dependency graph spanning all 10 artifact and tool classes."""

    def __init__(self):
        self.nodes: dict[str, UniversalNode] = {}
        self.edges: list[dict[str, Any]] = []

    def add_node(self, node: UniversalNode) -> None:
        self.nodes[node.id] = node

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation: str = "PIPES_TO",
        weight: float = 1.0,
        rationale: str = "",
    ) -> None:
        self.edges.append(
            {
                "source": source_id,
                "target": target_id,
                "relation": relation,
                "weight": weight,
                "rationale": rationale,
            }
        )

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
        lines = ["```mermaid", "flowchart TD"]
        for n in self.nodes.values():
            safe_id = n.id.replace("/", "_").replace("-", "_").replace(".", "_")
            lines.append(f'    {safe_id}["[{n.kind.value.upper()}] {n.name}"]')
        for e in self.edges:
            s_id = e["source"].replace("/", "_").replace("-", "_").replace(".", "_")
            t_id = e["target"].replace("/", "_").replace("-", "_").replace(".", "_")
            lines.append(f"    {s_id} -->|{e['relation']}| {t_id}")
        lines.append("```")
        return "\n".join(lines)
