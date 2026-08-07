"""Fail when tracked project content resembles secrets or private infrastructure."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "cloud_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "databricks_token": re.compile(r"\bdapi[a-f0-9]{32,}\b", re.IGNORECASE),
    "secret_assignment": re.compile(
        r"(?i)(?:password|client_secret|api_key|access_token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
    ),
    "private_service_url": re.compile(r"(?i)https?://[^\s'\"]*(?:\.internal|\.corp|localhost)"),
    "private_ipv4": re.compile(r"https?://(?:10\.|127\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)"),
}

TEXT_SUFFIXES = {
    "",
    ".csv",
    ".example",
    ".ipynb",
    ".json",
    ".md",
    ".py",
    ".sql",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
ALLOWED_BINARY_SUFFIXES: set[str] = set()
IGNORED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
}


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    scanner = Path(__file__).resolve()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.resolve() == scanner:
            continue
        if path.name == ".env":
            findings.append(f"tracked environment file: {path}")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            if path.suffix.lower() not in ALLOWED_BINARY_SUFFIXES:
                findings.append(f"unexpected binary or file type: {path}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{label}: {path}")
        if path.suffix.lower() == ".ipynb":
            notebook = json.loads(text)
            if any(cell.get("outputs") for cell in notebook.get("cells", [])):
                findings.append(f"notebook contains outputs: {path}")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="?", default=Path.cwd())
    args = parser.parse_args(argv)
    findings = scan(args.root.resolve())
    if findings:
        print("\n".join(findings))
        return 1
    print("Security scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
