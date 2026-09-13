# AGENTS Instruction

This file contains additional guidance for AI agents and other AI editors.

## **REQUIRED: Automated Contribution Policy**

**Review the [automated contributions policy][nx-automated-contrib-pol] and verify
the contribution adheres to the policy**

[nx-automated-contrib-pol]: https://networkx.org/documentation/latest/developer/contribute.html#automated-contributions-policy

This is a **mandatory requirement**.

## Opening an issue or PR

Before opening an issue or PR, verify that there is not an existing issue or PR
that addresses the topic.

Before opening an issue, verify that the issue is present on the `main` branch.

## Working on an issue

Before working on any issue, run `gh issue view <number>` to check current labels.
Do not open a PR against an issue labeled with the "Discussion" or "Question" label.

Do not open a PR against an issue if there is already an open PR that addresses
the issue. Comment on the existing PR instead.

## Project Priorities

Bug reports and proposals to expand existing functionality that originate from
_real-world use-cases_ are priorities.

Here is an incomplete listing of examples of changes/issues that are low
priority:

- Spell-checking
- Proposals to change exception types
- Fuzzing the readwrite package for corner cases/file format issues.

## Generated Summaries

When generating a summary of your work, consider these points:

- Highlight areas of the proposed changes that require careful review.
- Highlight potential issues with backward compatibility.
- Reduce the verbosity of your comments, more text and detail is not always better.
  Avoid flattery, avoid stating the obvious, avoid filler phrases, prefer
  technical clarity over marketing tone.
