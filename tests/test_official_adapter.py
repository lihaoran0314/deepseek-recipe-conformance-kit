# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import pytest

from recipe_conformance.adapters import OfficialPythonAdapter
from recipe_conformance.models import StreamFixture
from recipe_conformance.runner import run_conformance


def test_official_adapter_runs_when_deepseek_recipe_is_installed() -> None:
    pytest.importorskip("deepseek_recipe")
    fixture = StreamFixture(
        id="official-smoke",
        protocol="chat_completions",
        request={
            "model": "DeepSeek-V4.1-Flash",
            "messages": [{"role": "user", "content": "Say hello"}],
            "thinking": {"type": "disabled"},
            "stream": True,
        },
        model="DeepSeek-V4.1-Flash",
        model_text="Hello, world!",
        mode="chunk_transparent",
        issue_refs=("deepseek-recipe#28",),
    )
    report = run_conformance([fixture], OfficialPythonAdapter(), seed=3, random_split_samples=2)
    assert report.passed is True, report.to_dict()
