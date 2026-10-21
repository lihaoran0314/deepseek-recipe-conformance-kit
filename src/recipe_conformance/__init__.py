# SPDX-License-Identifier: Apache-2.0
"""Public API for the deepseek-recipe conformance kit."""

from .adapters import ChunkEchoMockAdapter, JoinedTextMockAdapter, OfficialPythonAdapter
from .models import ConformanceReport, StreamFixture, load_fixtures
from .runner import run_conformance

__version__ = "0.1.0"

__all__ = [
    "ChunkEchoMockAdapter",
    "ConformanceReport",
    "JoinedTextMockAdapter",
    "OfficialPythonAdapter",
    "StreamFixture",
    "__version__",
    "load_fixtures",
    "run_conformance",
]
