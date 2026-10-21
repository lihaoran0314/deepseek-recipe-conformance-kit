# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from recipe_conformance.adapters import ChunkEchoMockAdapter, JoinedTextMockAdapter
from recipe_conformance.models import StreamFixture
from recipe_conformance.runner import run_conformance


def _fixture(*, mode: str = "chunk_transparent", text: str = "hello") -> StreamFixture:
    return StreamFixture(
        id="test",
        protocol="chat_completions",
        request={
            "model": "DeepSeek-V4.1-Flash",
            "messages": [{"role": "user", "content": "hello"}],
            "thinking": {"type": "disabled"},
            "stream": True,
        },
        model="DeepSeek-V4.1-Flash",
        model_text=text,
        mode=mode,
    )


def test_transparent_adapter_passes_chunk_invariance() -> None:
    report = run_conformance([_fixture()], JoinedTextMockAdapter(), seed=7, random_split_samples=5)
    assert report.passed is True
    assert report.run_count > 5


def test_chunk_exposing_adapter_fails_chunk_invariance() -> None:
    report = run_conformance([_fixture()], ChunkEchoMockAdapter(), seed=7, random_split_samples=5)
    assert report.passed is False
    transparent = next(check for check in report.scenarios[0].checks if check.name == "chunk_transparent")
    assert transparent.passed is False


def test_end_of_stream_check_requires_replacement_character() -> None:
    report = run_conformance(
        [_fixture(mode="end_of_stream", text="prefix-\ufffd")],
        JoinedTextMockAdapter(),
        seed=7,
        random_split_samples=3,
    )
    assert report.passed is True
