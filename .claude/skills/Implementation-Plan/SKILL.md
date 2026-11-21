---
name: implementation-plan
description: Use when working on features or bug fixes to enforce a Test-Driven API Implementation Design (TDAID) workflow with Red, Green, and Refactor phases.
---

# TDAID Development Workflow

When working on features or bug fixes in this project, you MUST strictly follow the Test-Driven API Implementation Design (TDAID) methodology outlined below.

## Ground Rules
1. **Act like a Senior Backend Developer and Senior QA Tester:** Every change must be approached with the discipline, care, and quality assurance expected of a senior engineer.
2. **Pull Latest:** Make sure to pull `origin/development` first before starting any work to ensure no merge conflicts.
3. **Branching:** Create a dedicated branch for that specific phase/feature off of `development`.
4. **Phased Approach:** Each feature or fix should go through the Red, Green, and Refactor phases.
5. **Wait for Go Signal:** You MUST stop and wait for a go signal from the user before proceeding to the next phase (unless the user stated otherwise).

## Phases

### Red Phase (Tests)
- Write **failing tests** that enforce the expected behavior of the feature or bug fix.
- Do not write any implementation code during this phase.

### Green Phase (Code)
- Write the minimum implementation code required to make the tests pass.
- **Linting & Types:** Ensure all code passes linting rules and type error checks before finishing this phase.
- **CRITICAL:** When in the Green step, DO NOT change any testing files, their logic, or test data.

### Refactor Phase (Optimization)
Perform the 3 types of refactoring:
1. **Code Quality Refactoring:** Improve readability, remove dead code, and apply the DRY principle (extracting methods/constants).
2. **Performance Refactoring:** Optimize loops, database queries, and algorithmic efficiency.
3. **Structural Refactoring:** Enforce design patterns, clean architectural boundaries, and proper dependency injection.
- Ensure all tests still pass and no underlying behavior has changed after refactoring.

## Post-Merge Milestone Logging
- **Trigger:** Execute ONLY after a feature/fix branch has passed all tests and been merged into `development`.
- **Action:** Append one concise entry to `docs/MEMORY.md` (or `docs/DECISIONS.md`) recording:
  1. Date & merged branch/feature name.
  2. Key architectural or invariant decisions made.
  3. Any schema, Redis keyspace, or concurrency edge cases resolved.
- **Constraint:** Keep each entry under 6 bullet points; never log raw command outputs or intermediate failed attempts.