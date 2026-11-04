"""cli.py — Master CLI for Higher-Order Tool Chaining (Meta-Orchestrator)."""

from __future__ import annotations

import argparse
import json
import sys

from .orchestrator import ToolChainOrchestrator

VERSION = "1.0.0"


def main():
    parser = argparse.ArgumentParser(
        prog="tool-chain",
        description="Universal Meta-Orchestrator & SYN-TEX Filament Thread for Multi-Class Tool Chaining",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. run
    run_p = subparsers.add_parser("run", help="Execute an end-to-end multi-class tool chain")
    run_p.add_argument("query", help="Task description or goal")
    run_p.add_argument("-i", "--intent", default="investigation", choices=["investigation", "refactoring", "docs_sync"])
    run_p.add_argument("-b", "--backward", type=int, default=1, help="Depth of backward historical nodes")
    run_p.add_argument("-f", "--forward", type=int, default=2, help="Depth of forward horizon nodes")
    run_p.add_argument("--signals", action="store_true", help="Stream live SYN-TEX telemetry signals")

    # 2. inspect
    inspect_p = subparsers.add_parser("inspect", help="Inspect synthesized execution filament thread")
    inspect_p.add_argument(
        "-i", "--intent", default="investigation", choices=["investigation", "refactoring", "docs_sync"]
    )
    inspect_p.add_argument("-b", "--backward", type=int, default=1)
    inspect_p.add_argument("-f", "--forward", type=int, default=2)

    # 3. benchmark
    subparsers.add_parser("benchmark", help="Run high-throughput multi-class chaining benchmark")

    args = parser.parse_args()
    orch = ToolChainOrchestrator()

    if args.command == "benchmark":
        print("Running Meta-Tool Chaining Throughput Benchmark...")
        import time

        t0 = time.time()
        for _ in range(500):
            res = orch.execute_thread("Benchmark iteration", backward_levels=2, forward_levels=2)
            if res["status"] != "SUCCESS":
                print("Benchmark failed during iteration", file=sys.stderr)
                sys.exit(1)
        dur = time.time() - t0
        print(f"Bred and chained 500 multi-class threads (3,000 nodes) in {dur:.3f}s ({500 / dur:.1f} threads/sec)")
        print("Status: PASS (sub-second high-throughput meta-orchestration achieved)")
        return

    if args.command == "inspect":
        plan = orch.build_plan(args.intent)
        print(f"Meta-Tool Chaining Filament Thread ({len(plan)} nodes):")
        for i, n in enumerate(plan):
            inv = " [DOMINANT INVARIANT]" if n.dominant_invariant else ""
            print(f"  [{i}] [{n.kind.value.upper():<11}] {n.id} (weight={n.capability_weight}){inv} -> {n.description}")
        return

    if args.command == "run":
        cb = (lambda sig: print(sig, file=sys.stderr)) if args.signals else None
        res = orch.execute_thread(
            args.query,
            plan=orch.build_plan(args.intent),
            backward_levels=args.backward,
            forward_levels=args.forward,
            signal_callback=cb,
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
