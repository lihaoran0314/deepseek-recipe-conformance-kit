# SPDX-License-Identifier: Apache-2.0
"""Deterministic chunk-split generation."""

from __future__ import annotations

import random

from .models import SplitPlan


def two_way_splits(text: str) -> list[SplitPlan]:
    """Return every two-way split at Python character boundaries."""
    return [SplitPlan(f"two-way@{index}", (text[:index], text[index:])) for index in range(len(text) + 1)]


def char_by_char(text: str) -> SplitPlan:
    return SplitPlan("char-by-char", tuple(text) if text else ("",))


def whole(text: str) -> SplitPlan:
    return SplitPlan("whole", (text,))


def random_k_way_splits(
    text: str,
    *,
    count: int,
    seed: int,
    max_parts: int = 8,
) -> list[SplitPlan]:
    """Generate deterministic random k-way partitions at character boundaries."""
    if count < 0:
        raise ValueError("count must be non-negative")
    if max_parts <= 0:
        raise ValueError("max_parts must be positive")
    rng = random.Random(seed)
    plans: list[SplitPlan] = []
    seen: set[tuple[str, ...]] = set()
    for sample in range(count):
        cuts = sorted(rng.sample(range(len(text) + 1), k=min(max_parts - 1, len(text) + 1)))
        boundaries = [0, *cuts, len(text)]
        pieces = tuple(text[start:end] for start, end in zip(boundaries, boundaries[1:], strict=False))
        if pieces in seen:
            continue
        seen.add(pieces)
        plans.append(SplitPlan(f"random-{sample}@{cuts}", pieces))
    return plans


def all_plans(text: str, *, random_samples: int, seed: int) -> list[SplitPlan]:
    plans = [
        whole(text),
        *two_way_splits(text),
        char_by_char(text),
        *random_k_way_splits(text, count=random_samples, seed=seed),
    ]
    deduped: list[SplitPlan] = []
    seen: set[tuple[str, ...]] = set()
    for plan in plans:
        if plan.pieces in seen:
            continue
        seen.add(plan.pieces)
        deduped.append(plan)
    return deduped
