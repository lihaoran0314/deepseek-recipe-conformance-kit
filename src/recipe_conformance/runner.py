# SPDX-License-Identifier: Apache-2.0
"""Conformance runner and semantic checks."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from .adapters import StreamAdapter
from .models import CheckResult, ConformanceReport, RunResult, ScenarioResult, StreamFixture
from .splits import all_plans

VOLATILE_KEYS = {"created", "created_at", "timestamp"}


def normalize_events(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize_events(item) for key, item in value.items() if key not in VOLATILE_KEYS}
    if isinstance(value, list):
        return [normalize_events(item) for item in value]
    return value


def event_digest(events: list[Any]) -> str:
    normalized = normalize_events(copy.deepcopy(events))
    encoded = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def event_text(events: list[Any]) -> str:
    return json.dumps(normalize_events(events), ensure_ascii=False, sort_keys=True)


def run_scenario(
    fixture: StreamFixture,
    adapter: StreamAdapter,
    *,
    seed: int,
    random_split_samples: int,
) -> ScenarioResult:
    plans = all_plans(fixture.model_text, random_samples=random_split_samples, seed=seed)
    runs: list[RunResult] = []
    for plan in plans:
        if "".join(plan.pieces) != fixture.model_text:
            runs.append(RunResult(plan=plan, events=[], event_digest="", error="split plan changed the model text"))
            continue
        try:
            events = adapter.run(fixture, plan)
            runs.append(RunResult(plan=plan, events=events, event_digest=event_digest(events)))
        except Exception as exc:  # noqa: BLE001 - adapter failures are conformance data
            runs.append(
                RunResult(
                    plan=plan,
                    events=[],
                    event_digest="",
                    error=f"{type(exc).__name__}: {exc}",
                )
            )

    checks: list[CheckResult] = []
    errors = [run for run in runs if run.error]
    checks.append(CheckResult("split_reconstructs_text", not errors, f"{len(errors)} failed split plans"))
    checks.append(CheckResult("all_runs_execute", not errors, errors[0].error if errors else "all runs executed"))

    if fixture.mode == "chunk_transparent" and not errors:
        baseline = runs[0].event_digest
        mismatches = [run.plan.label for run in runs[1:] if run.event_digest != baseline]
        checks.append(
            CheckResult(
                "chunk_transparent",
                not mismatches,
                "all split plans produced identical normalized events"
                if not mismatches
                else f"mismatched split plans: {', '.join(mismatches[:8])}",
            )
        )
    elif fixture.mode == "chunk_dependent_contract" and not errors:
        empty_runs = [run.plan.label for run in runs if not run.events]
        checks.append(
            CheckResult(
                "contract_output_nonempty",
                not empty_runs,
                "chunk-dependent outputs may differ but must emit events"
                if not empty_runs
                else f"empty output for: {', '.join(empty_runs[:8])}",
            )
        )
    elif fixture.mode == "end_of_stream" and not errors:
        marker = "\ufffd"
        missing = [run.plan.label for run in runs if marker not in event_text(run.events)]
        checks.append(
            CheckResult(
                "end_of_stream_preserves_replacement_character",
                not missing,
                "U+FFFD is present for every split" if not missing else f"lost U+FFFD in: {', '.join(missing[:8])}",
            )
        )

    return ScenarioResult(
        fixture_id=fixture.id,
        protocol=fixture.protocol,
        mode=fixture.mode,
        issue_refs=fixture.issue_refs,
        notes=fixture.notes,
        runs=runs,
        checks=checks,
    )


def run_conformance(
    fixtures: list[StreamFixture],
    adapter: StreamAdapter,
    *,
    seed: int,
    random_split_samples: int,
) -> ConformanceReport:
    scenarios = [
        run_scenario(fixture, adapter, seed=seed, random_split_samples=random_split_samples) for fixture in fixtures
    ]
    return ConformanceReport(
        adapter=adapter.name,
        seed=seed,
        random_split_samples=random_split_samples,
        scenarios=scenarios,
    )
