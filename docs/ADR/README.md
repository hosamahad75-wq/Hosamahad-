# ADRs (Architecture Decision Records)

This directory contains Architecture Decision Records (ADRs) for this repository.

What is an ADR?

An ADR is a short text file that captures an important architectural decision made along with its context and consequences. ADRs help preserve the history of why decisions were made.

How to add a new ADR

1. Copy this repository's ADR template and create a new file with the next sequential number, e.g. `0002-use-fastapi-for-api.md`.
2. Use a short, descriptive title in the filename and the document title header.
3. Fill in Status, Context, Decision, and Consequences sections.
4. Commit and reference the ADR in PRs that implement or change the decision.

Naming conventions

- Filenames should be zero-padded sequential numbers followed by a short slug: `0001-record-architecture-decisions.md`.
- Titles inside the file should match the slug but can be more descriptive.

Format

See `0001-record-architecture-decisions.md` for an example template.
