# Agentic DevSecOps Pipeline

> AI-assisted DevSecOps workflows for secure pull request analysis, infrastructure review, and CI/CD investigation.

[![CI](https://github.com/StarAndStripe/agentic-devsecops-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/StarAndStripe/agentic-devsecops-pipeline/actions/workflows/ci.yml)

## Overview

The Agentic DevSecOps Pipeline explores how AI agents can augment traditional CI/CD pipelines without replacing deterministic engineering controls.

The project combines:

- GitHub Actions
- GitHub Agentic Workflows
- AI-assisted pull request analysis
- Deterministic automated testing
- Least-privilege permissions
- Safe agent outputs
- Supply-chain hardening
- Dependabot
- Branch protection
- Human-in-the-loop approval

The core engineering principle is:

> **AI reasons → policy constrains → deterministic CI verifies → human decides.**

Rather than giving an AI agent unrestricted control over the software delivery lifecycle, the agent operates as an advisory security and engineering layer around conventional CI/CD controls.

---

## Why This Project?

Traditional CI pipelines are excellent at answering deterministic questions:

- Does the application build?
- Do the tests pass?
- Does linting succeed?
- Does a security scanner detect a known pattern?

However, a successful pipeline does not necessarily mean that a change is well tested, operationally safe, or free from contextual risk.

For example, a test suite may pass while important business edge cases remain completely untested.

This project introduces an AI reasoning layer capable of reviewing the broader context of a change while keeping deterministic CI and human approval authoritative.

---

## Architecture

```text
Developer
    |
    v
Feature Branch
    |
    v
Pull Request
    |
    +-----------------------+
    |                       |
    v                       v
Deterministic CI       AI PR Reviewer
Pytest                 Agentic Workflow
    |                       |
    |                       +--> Correctness
    |                       +--> Test coverage
    |                       +--> Edge cases
    |                       +--> Security risks
    |                       +--> CI/CD risks
    |                       +--> Maintainability
    |                       |
    v                       v
Required Check          Advisory Findings
    |                       |
    +-----------+-----------+
                |
                v
          Human Review
                |
                v
       Branch Protection
                |
                v
          Protected Main
```

The deterministic pipeline remains responsible for executing tests and enforcing required checks.

The AI reviewer performs contextual analysis and produces advisory findings.

The human reviewer retains the final merge decision.

---

## Demo 1 — AI-Powered Pull Request Reviewer

### Objective

Build an AI-assisted pull request reviewer capable of identifying risks that may not be detected by deterministic tests alone.

The reviewer analyzes pull request changes for:

- correctness
- missing test coverage
- edge cases
- security concerns
- maintainability
- potential regressions
- CI/CD and supply-chain risks

The agent is intentionally prevented from:

- approving pull requests
- merging code
- modifying source code
- deploying resources
- exposing secrets

Its role is advisory.

---

## Demo Scenario

A shipping-fee function was introduced with logic for:

- standard shipping
- express shipping
- free shipping above a threshold

The initial automated tests passed.

However, the AI reviewer identified that several important behaviors were not adequately covered, including boundary conditions and invalid monetary input.

### First Review

**Risk: MEDIUM**

The reviewer identified:

- insufficient branch coverage
- missing express-shipping tests
- missing free-shipping boundary tests
- missing invalid-order-total validation

The application was updated and the test suite expanded.

The deterministic test suite then reported:

```text
8 passed
```

### Second Review

The functional issues were resolved, but the AI reviewer identified a new DevSecOps concern.

The CI workflow referenced GitHub Actions using mutable major-version tags:

```yaml
uses: actions/checkout@v4
uses: actions/setup-python@v5
```

This introduced a potential software supply-chain risk because mutable tags may change over time.

### Supply-Chain Remediation

The actions were pinned to immutable full commit SHAs:

```yaml
uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0
uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5.6.0
```

Dependabot was then configured to monitor GitHub Actions dependencies and propose controlled updates through pull requests.

### Final Review

**Risk: LOW**

The AI reviewer confirmed:

- application decision branches were covered
- invalid monetary input was handled
- GitHub Actions were pinned to immutable SHAs
- CI retained least-privilege permissions
- no blocking application security issue was identified

All required checks passed before the human-controlled merge.

---

## Security Model

AI agents operating inside CI/CD environments introduce additional security considerations.

This project therefore applies several controls.

### Least Privilege

The CI workflow uses read-only repository permissions where write access is unnecessary.

```yaml
permissions:
  contents: read
```

The AI reviewer also operates with deliberately restricted permissions.

### Safe Agent Outputs

Agent reasoning is separated from privileged repository operations.

The reviewer can produce controlled outputs such as:

- pull request comments
- inline review comments
- advisory pull request reviews

The agent cannot directly merge or deploy code.

### Human-in-the-Loop

AI findings remain advisory.

A human reviewer evaluates the findings and retains authority over the final merge decision.

### Deterministic Enforcement

AI reasoning does not replace conventional CI.

Automated tests remain deterministic. In the current demonstration repository,
the `Python Tests` job from the `CI` workflow is configured as a required status
check through a GitHub repository ruleset before changes can be merged into `main`.

Repository rulesets are GitHub-side controls and are therefore not represented
by the versioned workflow files in this repository.

### Supply-Chain Hardening

Third-party GitHub Actions are pinned to immutable commit SHAs instead of mutable release tags.

Dependabot provides controlled dependency update proposals.

### Protected Main Branch

In the current demonstration repository, the `main` branch is protected through
a GitHub repository ruleset requiring pull-request-based changes and successful
required CI checks before merge.

Force pushes and branch deletion are restricted.

These protections are repository-level GitHub settings rather than controls
defined directly in the versioned CI workflow.

---

## Deterministic CI vs Agentic Reasoning

| Deterministic CI | Agentic Review |
|---|---|
| Executes tests | Evaluates whether important tests are missing |
| Produces repeatable pass/fail results | Performs contextual reasoning |
| Enforces required checks | Produces advisory findings |
| Validates known conditions | Identifies potential unknown gaps |
| Suitable for hard gates | Suitable for risk assessment |

These approaches are complementary rather than interchangeable.

---

## Technology Stack

- GitHub Actions
- GitHub Agentic Workflows (`gh-aw`)
- GitHub Copilot
- GPT-5.6 Terra
- Python 3.13
- Pytest
- Dependabot
- GitHub Repository Rulesets

---

## Repository Structure

```text
agentic-devsecops-pipeline/
|
|-- .github/
|   |-- workflows/
|   |   |-- ai-pr-reviewer.md
|   |   |-- ai-pr-reviewer.lock.yml
|   |   `-- ci.yml
|   |
|   `-- dependabot.yml
|
|-- src/
|   `-- pricing.py
|
|-- tests/
|   `-- test_pricing.py
|
|-- requirements.txt
`-- README.md
```

---

## Current Capabilities

### Demo 1 — AI Pull Request Reviewer

Status: **Completed**

Provides contextual AI-assisted review of application and CI/CD changes while preserving deterministic CI and human merge authority.

### Demo 2 — Terraform Infrastructure Risk Reviewer

Status: **Planned**

Planned analysis includes:

- IAM privilege risks
- network exposure
- encryption configuration
- destructive infrastructure changes
- infrastructure security posture

### Demo 3 — CI Failure Investigator

Status: **Planned**

Planned capabilities include:

- CI failure analysis
- probable root-cause identification
- supporting evidence
- remediation recommendations
- confidence assessment

---

## Engineering Principles

This project follows several design principles:

1. AI augments deterministic automation rather than replacing it.
2. Agents receive the minimum permissions required.
3. AI-generated findings are treated as untrusted advisory input.
4. Privileged operations remain policy controlled.
5. Human approval remains part of sensitive decisions.
6. CI/CD dependencies are treated as part of the software supply chain.
7. Agent behavior should be observable, auditable, and reproducible where possible.

---

## Roadmap

- [x] Deterministic Python CI pipeline
- [x] AI-powered pull request reviewer
- [x] Safe agent outputs
- [x] Human-controlled review workflow
- [x] Protected main branch
- [x] Immutable GitHub Action dependencies
- [x] Dependabot for GitHub Actions
- [ ] Terraform infrastructure risk reviewer
- [ ] CI failure investigation agent
- [ ] Agent evaluation and observability
- [ ] Multi-model comparison
- [ ] Production-oriented policy gates

---

## Project Status

This repository is an evolving engineering portfolio project focused on the intersection of:

**AI Infrastructure · Agentic DevSecOps · CI/CD · Cloud Security · MLOps**

The goal is to demonstrate practical patterns for introducing AI reasoning into software delivery systems while maintaining security boundaries, deterministic controls, and human oversight.