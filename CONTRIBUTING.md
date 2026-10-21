# Contributing

1. Fork the repository and create a focused branch.
2. Install `python -m pip install -e '.[dev]'`.
3. Run `python -m ruff check .`, `python -m ruff format --check .`, and `python -m pytest`.
4. For official-binding changes, run the Ubuntu CI or install `.[official]` with Rust, Clang, and OpenCV available.
5. Add a reproducible fixture for every protocol or streaming bug.
6. Never include API keys, model weights, private prompts, or proprietary traces.

Fixtures should be minimal, deterministic, and linked to an upstream issue when possible.
