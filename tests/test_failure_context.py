import json
import subprocess
import sys
from pathlib import Path

from scripts.collect_failure_context import clean_log, prepare_log
from scripts.collect_failure_context import extract_failure_signal

def test_ansi_escape_sequences_are_removed():
    log = "\x1b[36;1mpython -m pytest\x1b[0m"

    result = clean_log(log)

    assert result == "python -m pytest"


def test_control_characters_are_removed():
    log = "pytest\x00 failed\x07\nassert 5 == 0"

    result = clean_log(log)

    assert "\x00" not in result
    assert "\x07" not in result
    assert "pytest failed" in result
    assert "assert 5 == 0" in result


def test_newlines_and_tabs_are_preserved():
    log = "Python Tests\tFAILED\nassert 5 == 0"

    result = clean_log(log)

    assert "\t" in result
    assert "\n" in result


def test_prepare_log_cleans_before_truncating():
    log = "\x1b[31m" + ("A" * 20_000) + "FINAL ERROR\x1b[0m"

    result = prepare_log(log, max_chars=1_000)

    assert len(result) <= 1_000
    assert "\x1b" not in result
    assert result.endswith("FINAL ERROR")

def test_extract_failure_signal_keeps_pytest_failure():
    log = """
Installing dependencies
Everything installed successfully
============================= test session starts =============================
tests/test_pricing.py .....F..
=================================== FAILURES ===================================
________________________ test_free_shipping_at_boundary ________________________

def test_free_shipping_at_boundary():
    assert calculate_shipping_fee(100) == 0
E   assert 5 == 0
E    + where 5 = calculate_shipping_fee(100)

tests/test_pricing.py:27: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pricing.py::test_free_shipping_at_boundary - assert 5 == 0
========================= 1 failed, 7 passed =========================
##[error]Process completed with exit code 1.
Post job cleanup
"""

    result = extract_failure_signal(log)

    assert "test_free_shipping_at_boundary" in result
    assert "assert 5 == 0" in result
    assert "AssertionError" in result
    assert "FAILED tests/test_pricing.py" in result
    assert "exit code 1" in result


def test_extract_failure_signal_removes_unrelated_noise():
    log = """
Downloading pytest
Installing collected packages
Successfully installed pytest
Some unrelated setup information
=================================== FAILURES ===================================
test_example
E   assert 5 == 0
FAILED tests/test_example.py::test_example
##[error]Process completed with exit code 1.
Post job cleanup
Cleaning up orphan processes
"""

    result = extract_failure_signal(log)

    assert "Downloading pytest" not in result
    assert "Installing collected packages" not in result
    assert "Cleaning up orphan processes" not in result

    assert "FAILURES" in result
    assert "assert 5 == 0" in result


def test_extract_failure_signal_falls_back_when_no_marker_exists():
    log = """
Unknown CI output
Something unexpected happened
No recognized failure marker
"""

    result = extract_failure_signal(log)

    assert result == log


def test_cli_generates_valid_json_with_changed_files(tmp_path):
    log_file = tmp_path / "failed-ci.log"
    changed_files_file = tmp_path / "changed-files.txt"
    output_file = tmp_path / "failure-context.json"

    log_file.write_text(
        "FAILED tests/test_pricing.py::test_free_shipping_at_boundary\n"
        "AssertionError: expected free shipping\n",
        encoding="utf-8",
    )

    changed_files_file.write_text(
        "src/pricing.py\n"
        "tests/test_pricing.py\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            "scripts/collect_failure_context.py",
            "--workflow",
            "CI",
            "--job",
            "Python Tests",
            "--commit-sha",
            "test-sha-123",
            "--changed-files-file",
            str(changed_files_file),
            "--log-file",
            str(log_file),
            "--output",
            str(output_file),
        ],
        check=True,
    )

    context = json.loads(
        output_file.read_text(encoding="utf-8")
    )

    assert context["workflow"] == "CI"
    assert context["job"] == "Python Tests"
    assert context["commit_sha"] == "test-sha-123"

    assert context["changed_files"] == [
        "src/pricing.py",
        "tests/test_pricing.py",
    ]

    assert "FAILED tests/test_pricing.py" in context["failure_log"]
    assert "AssertionError" in context["failure_log"]


def test_cli_generates_valid_json_for_dependency_failure(tmp_path):
    log_file = tmp_path / "failed-ci.log"
    changed_files_file = tmp_path / "changed-files.txt"
    output_file = tmp_path / "failure-context.json"

    log_file.write_text(
        "Collecting requests\n"
        "ERROR: Could not find a version that satisfies the requirement "
        "nonexistent-package==99.99.99\n"
        "ERROR: No matching distribution found for "
        "nonexistent-package==99.99.99\n",
        encoding="utf-8",
    )

    changed_files_file.write_text(
        "requirements.txt\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            "scripts/collect_failure_context.py",
            "--workflow",
            "CI",
            "--job",
            "Python Tests",
            "--commit-sha",
            "dependency-failure-sha",
            "--changed-files-file",
            str(changed_files_file),
            "--log-file",
            str(log_file),
            "--output",
            str(output_file),
        ],
        check=True,
    )

    context = json.loads(
        output_file.read_text(encoding="utf-8")
    )

    assert context["workflow"] == "CI"
    assert context["job"] == "Python Tests"
    assert context["commit_sha"] == "dependency-failure-sha"
    assert context["changed_files"] == ["requirements.txt"]

    assert "Could not find a version" in context["failure_log"]
    assert "No matching distribution" in context["failure_log"]
    assert "nonexistent-package==99.99.99" in context["failure_log"]

def test_cli_generates_context_when_failure_log_is_missing(tmp_path):
    missing_log_file = tmp_path / "failed-ci.log"
    changed_files_file = tmp_path / "changed-files.txt"
    output_file = tmp_path / "failure-context.json"

    changed_files_file.write_text(
        "requirements.txt\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            "scripts/collect_failure_context.py",
            "--workflow",
            "CI",
            "--job",
            "Python Tests",
            "--commit-sha",
            "missing-log-sha",
            "--changed-files-file",
            str(changed_files_file),
            "--log-file",
            str(missing_log_file),
            "--output",
            str(output_file),
        ],
        check=True,
    )

    context = json.loads(
        output_file.read_text(encoding="utf-8")
    )

    assert context["workflow"] == "CI"
    assert context["commit_sha"] == "missing-log-sha"
    assert context["changed_files"] == ["requirements.txt"]

    assert "failure log unavailable" in context["failure_log"].lower()