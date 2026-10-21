# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from recipe_conformance.splits import all_plans, random_k_way_splits, two_way_splits


def test_two_way_splits_cover_every_character_boundary() -> None:
    plans = two_way_splits("abc")
    assert len(plans) == 4
    assert ["".join(plan.pieces) for plan in plans] == ["abc"] * 4
    assert plans[0].pieces == ("", "abc")
    assert plans[-1].pieces == ("abc", "")


def test_random_splits_are_deterministic_and_reconstruct_text() -> None:
    first = random_k_way_splits("abcdefghij", count=12, seed=7, max_parts=5)
    second = random_k_way_splits("abcdefghij", count=12, seed=7, max_parts=5)
    assert first == second
    assert all("".join(plan.pieces) == "abcdefghij" for plan in first)


def test_all_plans_are_deduplicated() -> None:
    plans = all_plans("abc", random_samples=10, seed=1)
    piece_sets = [plan.pieces for plan in plans]
    assert len(piece_sets) == len(set(piece_sets))
    assert ("abc",) in piece_sets
    assert tuple("abc") in piece_sets
