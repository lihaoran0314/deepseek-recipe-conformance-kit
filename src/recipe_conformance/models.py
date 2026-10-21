# SPDX-License-Identifier: Apache-2.0
"""Data models for recipe conformance fixtures and reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Protocol = Literal["chat_completions", "responses", "messages"]
ScenarioMode = Literal["chunk_transparent", "semantic_transparent", "chunk_dependent_contract", "end_of_stream"]


@dataclass(frozen=True, slots=True)
class StreamFixture:
    id: str
    protocol: Protocol
    request: dict[str, Any]
    model: str
    model_text: str
    finish_reason: str = "stop"
    prompt_tokens: int = 1
    prompt_cache_hit_tokens: int = 0
    mode: ScenarioMode = "chunk_transparent"
    issue_refs: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True, slots=True)
class SplitPlan:
    label: str
    pieces: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


@dataclass(slots=True)
class RunResult:
    plan: SplitPlan
    events: list[Any]
    event_digest: str
    checks: list[CheckResult] = field(default_factory=list)
    error: str | None = None


@dataclass(slots=True)
class ScenarioResult:
    fixture_id: str
    protocol: str
    mode: str
    issue_refs: tuple[str, ...]
    notes: str
    runs: list[RunResult]
    checks: list[CheckResult]

    @property
    def passed(self) -> bool:
        return all(run.error is None for run in self.runs) and all(check.passed for check in self.checks)


@dataclass(slots=True)
class ConformanceReport:
    adapter: str
    seed: int
    random_split_samples: int
    scenarios: list[ScenarioResult]

    @property
    def passed(self) -> bool:
        return all(scenario.passed for scenario in self.scenarios)

    @property
    def scenario_count(self) -> int:
        return len(self.scenarios)

    @property
    def run_count(self) -> int:
        return sum(len(scenario.runs) for scenario in self.scenarios)

    @property
    def failure_count(self) -> int:
        return sum(1 for scenario in self.scenarios if not scenario.passed)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "adapter": self.adapter,
            "seed": self.seed,
            "random_split_samples": self.random_split_samples,
            "summary": {
                "passed": self.passed,
                "scenarios": self.scenario_count,
                "runs": self.run_count,
                "failures": self.failure_count,
            },
            "scenarios": [
                {
                    "fixture_id": scenario.fixture_id,
                    "protocol": scenario.protocol,
                    "mode": scenario.mode,
                    "issue_refs": list(scenario.issue_refs),
                    "notes": scenario.notes,
                    "passed": scenario.passed,
                    "checks": [asdict(check) for check in scenario.checks],
                    "runs": [
                        {
                            "plan": run.plan.label,
                            "pieces": len(run.plan.pieces),
                            "event_digest": run.event_digest,
                            "error": run.error,
                            "checks": [asdict(check) for check in run.checks],
                        }
                        for run in scenario.runs
                    ],
                }
                for scenario in self.scenarios
            ],
        }


def load_fixtures(value: list[dict[str, Any]]) -> list[StreamFixture]:
    fixtures: list[StreamFixture] = []
    for item in value:
        fixtures.append(
            StreamFixture(
                id=str(item["id"]),
                protocol=item["protocol"],
                request=dict(item["request"]),
                model=str(item.get("model", item["request"]["model"])),
                model_text=str(item["model_text"]),
                finish_reason=str(item.get("finish_reason", "stop")),
                prompt_tokens=int(item.get("prompt_tokens", 1)),
                prompt_cache_hit_tokens=int(item.get("prompt_cache_hit_tokens", 0)),
                mode=item.get("mode", "chunk_transparent"),
                issue_refs=tuple(str(ref) for ref in item.get("issue_refs", [])),
                notes=str(item.get("notes", "")),
            )
        )
    return fixtures
