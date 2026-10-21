# SPDX-License-Identifier: Apache-2.0
"""Command line entry point for the conformance runner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .adapters import ChunkEchoMockAdapter, JoinedTextMockAdapter, OfficialPythonAdapter, StreamAdapter
from .models import load_fixtures
from .runner import run_conformance

ROOT = Path(__file__).resolve().parents[2]


def _load_fixture_file(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, list):
        return value
    if isinstance(value, dict) and isinstance(value.get("fixtures"), list):
        return value["fixtures"]
    raise ValueError("fixture file must be a JSON list or an object with a 'fixtures' list")


def _adapter(name: str) -> StreamAdapter:
    if name == "official":
        return OfficialPythonAdapter()
    if name == "joined-mock":
        return JoinedTextMockAdapter()
    if name == "chunk-echo":
        return ChunkEchoMockAdapter()
    raise ValueError(f"unknown adapter: {name}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=ROOT / "fixtures" / "stream_cases.json")
    parser.add_argument("--adapter", choices=("official", "joined-mock", "chunk-echo"), default="official")
    parser.add_argument("--seed", type=int, default=20261021)
    parser.add_argument("--random-split-samples", type=int, default=12)
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "latest.json")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    fixtures = load_fixtures(_load_fixture_file(args.fixtures))
    report = run_conformance(
        fixtures,
        _adapter(args.adapter),
        seed=args.seed,
        random_split_samples=args.random_split_samples,
    )
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report.to_dict()["summary"], indent=2, sort_keys=True))
    print(f"output={output}")
    if not report.passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
