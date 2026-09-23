"""Build a bounded and normalized CI failure context for AI-assisted investigation."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path


MAX_LOG_CHARS = 12_000

ANSI_ESCAPE_RE = re.compile(
    r"""
    \x1B
    (?:
        [@-Z\\-_]
        |
        \[
        [0-?]*
        [ -/]*
        [@-~]
    )
    """,
    re.VERBOSE,
)

def load_changed_files(
    changed_files: str | None = None,
    changed_files_file: str | None = None,
) -> list[str]:
    """Return normalized changed-file paths from CLI input or a file."""

    if changed_files_file:
        path = Path(changed_files_file)

        if not path.exists():
            raise FileNotFoundError(
                f"Changed-files file does not exist: {changed_files_file}"
            )

        files = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        return files

    if changed_files:
        return [
            item.strip()
            for item in changed_files.split(",")
            if item.strip()
        ]

    return []

def load_failure_log(log_file: str) -> str:
    """Load a CI failure log or return a safe fallback when it is unavailable."""

    path = Path(log_file)

    if not path.exists():
        return (
            "CI failure log unavailable. "
            "The expected log file was not produced."
        )

    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )

def clean_log(log: str) -> str:
    """Normalize CI logs before they are provided to an AI investigator."""

    # Remove ANSI terminal escape sequences.
    cleaned = ANSI_ESCAPE_RE.sub("", log)

    # Normalize Unicode representation.
    cleaned = unicodedata.normalize("NFKC", cleaned)

    # Remove non-printable control characters while preserving
    # newlines and tabs because they remain useful for log structure.
    cleaned = "".join(
        char
        for char in cleaned
        if char in ("\n", "\r", "\t") or char.isprintable()
    )

    return cleaned

def extract_failure_signal(log: str) -> str:
    """Extract high-signal failure evidence from a normalized CI log."""

    lines = log.splitlines()
    selected_indexes: set[int] = set()

    signal_markers = (
        "FAILED ",
        "ERROR ",
        "AssertionError",
        "assert ",
        "##[error]",
        "Process completed with exit code",
        "Traceback",
    )

    # Pytest failure sections are already semantically bounded.
    in_failure_section = False

    for index, line in enumerate(lines):
        stripped = line.strip()

        if "FAILURES" in stripped:
            in_failure_section = True

        if in_failure_section:
            selected_indexes.add(index)

        # Explicit high-signal markers outside a recognized section.
        if any(marker in line for marker in signal_markers):
            selected_indexes.add(index)

            # Preserve immediate context around most failure markers.
            # Exit-code markers are terminal evidence and should not pull
            # unrelated post-failure warnings into the investigation context.
            if "Process completed with exit code" not in line:
                if index > 0:
                    selected_indexes.add(index - 1)

                if index + 1 < len(lines):
                    selected_indexes.add(index + 1)


        # GitHub's exit-code marker gives us a natural end boundary.
        if in_failure_section and "Process completed with exit code" in line:
            in_failure_section = False

    if not selected_indexes:
        # Conservative fallback for unknown CI failure formats.
        return log

    return "\n".join(
        lines[index]
        for index in sorted(selected_indexes)
    )

def truncate_log(log: str, max_chars: int = MAX_LOG_CHARS) -> str:
    """Keep failure context bounded while preserving the end of the log."""

    if len(log) <= max_chars:
        return log

    marker = "\n...[log truncated]...\n"
    available = max_chars - len(marker)

    return marker + log[-available:]


def prepare_log(log: str, max_chars: int = MAX_LOG_CHARS) -> str:
    """Clean, extract relevant failure evidence, and bound CI log data."""

    cleaned = clean_log(log)
    signal = extract_failure_signal(cleaned)

    return truncate_log(signal, max_chars=max_chars)


def build_failure_context(
    workflow: str,
    job: str,
    commit_sha: str,
    changed_files: list[str],
    failure_log: str,
) -> dict:
    """Create the structured context consumed by the AI investigator."""

    return {
        "workflow": workflow,
        "job": job,
        "commit_sha": commit_sha,
        "changed_files": changed_files,
        "failure_log": prepare_log(failure_log),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build bounded context for CI failure investigation."
    )

    parser.add_argument("--workflow", required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--changed-files", nargs="*", default=[])
    parser.add_argument("--changed-files-file")
    parser.add_argument("--log-file", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    log = load_failure_log(args.log_file)

    changed_files = load_changed_files(
        changed_files=",".join(args.changed_files) if args.changed_files else None,
        changed_files_file=args.changed_files_file,
    )

    context = build_failure_context(
        workflow=args.workflow,
        job=args.job,
        commit_sha=args.commit_sha,
        changed_files=changed_files,
        failure_log=log,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(
            context,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Failure context written to {output}")


if __name__ == "__main__":
    main()