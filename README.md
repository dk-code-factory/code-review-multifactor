# code-review-multifactor

A standalone Claude Code and Codex plugin for multi-actor GitHub pull-request reviews. Version 1.1.1. MIT licensed.

## Install

Claude Code:

```text
/plugin marketplace add dk-code-factory/code-review-multifactor
/plugin install code-review-multifactor@code-review-multifactor
```

Codex CLI:

```sh
codex plugin marketplace add dk-code-factory/code-review-multifactor
codex plugin add code-review-multifactor@code-review-multifactor
```

Start a new host session after installation. This repository catalogs only its own plugin and requires no other review plugin. Each host manifest selects its own native skill directory.

The repository and plugin are named `code-review-multifactor`. The included skill keeps its existing name, `review-multiactor`.

## Use

In Claude Code, invoke the namespaced skill:

```text
/code-review-multifactor:review-multiactor OWNER/REPO#123
```

In Codex, select `review-multiactor`, or invoke it with an optional pull-request URL, `OWNER/REPO#N`, or PR number when the repository is known, plus an optional design document URL:

```text
$review-multiactor https://github.com/OWNER/REPO/pull/123
$review-multiactor OWNER/REPO#123 https://example.com/design
$review-multiactor 123
```

Both hosts resolve the PR from the invocation, governing prompt, or caller context, including referenced handoff files. Without a supplied target, they discover the PR for the current branch in the matching repository. For example, run either command from a branch with an open PR:

```text
/code-review-multifactor:review-multiactor
$review-multiactor
```

They ask only when the target cannot be resolved unambiguously or conflicting target instructions need clarification. A known PR's access failure is reported as an access problem.

When called by dk-workflows, both hosts reuse supplied metadata, diffs, pinned commits, checkouts/worktrees, and discussion for the selected PR and comparison. They collect only missing inputs, preserve the caller's pinned comparison and review/output constraints, and keep freshness checks before authorized GitHub writes. A handoff can be referenced in the governing prompt without repeating the PR as a positional argument:

```text
Use $review-multiactor with the dk-workflows handoff at /tmp/pr-review/handoff.md.
It identifies the PR and pinned comparison and supplies the diff and worktrees.
Return findings locally; do not write to GitHub.
```

The same handoff instructions apply to Claude's `/code-review-multifactor:review-multiactor`. No workflow configuration changes or runtime helper are required.

Each host's skill coordinates three native subagents:

- **E2E Reviewer:** checks requirements, implementation, commit messages, PR description, discussion, and tests.
- **Independent Inventor:** develops an independent solution plan, then evaluates the description, production code, and tests through staged disclosure.
- **Code Inspector:** checks reuse, clarity, performance, and unnecessary code.

The foreground agent reconciles findings and returns final comments to their source actors for validation. It prepares inline findings in the authenticated user's pending GitHub review and leaves submission to the user. Existing pending comments are preserved. A local-only request keeps all findings in the host conversation.

Both workflows reuse supplied checkouts at the pinned commits or prepare detached worktrees as needed, and propose improvements as diffs. Both preserve or pin the PR comparison and revalidate head, base, and merge-base changes before further review writes. Actors return findings without writing to GitHub. The Independent Inventor returns its test plan before receiving proposed tests or GitHub discussion.

The Claude skill was adapted from the original `review-multiactor.md`. It retains its Opus, Fable, and Sonnet model requests with high effort. Codex uses its separately maintained native adaptation.

## Requirements

- Claude Code or Codex with native subagent tools enabled and enough capacity for three reviewers. Claude follows the imported model requests above. Codex actors inherit the active model; high reasoning is requested only when supported and permitted.
- Git and a matching local repository clone.
- GitHub access through connected tools or authenticated `gh`, including permission to prepare pending reviews when requested.
- Access to the linked issue, Jira work item, or design document when available. Inaccessible context is reported as a limitation.
- The repository's build and test tools when execution is needed. Both workflows use a local emulator or an explicitly authorized test target and the configured AWS credential chain for DynamoDB probes.

## Layout

- `.codex-plugin/plugin.json`: Codex plugin metadata.
- `.agents/plugins/marketplace.json`: Codex plugin catalog.
- `.claude-plugin/plugin.json`: Claude Code plugin metadata.
- `.claude-plugin/marketplace.json`: Claude Code plugin catalog.
- `codex/skills/review-multiactor/SKILL.md`: Codex review workflow.
- `claude/skills/review-multiactor/SKILL.md`: Claude Code review workflow.

The plugin contains its own skill instructions and has no build step or external runtime helper dependency.

## Validation

GitHub Actions validates both hosts' skill frontmatter, host skill paths, plugin/catalog metadata, release version consistency, and whitespace on pull requests and pushes to `main`.

Run the metadata and skill checks locally with:

```sh
python -m pip install PyYAML==6.0.3
python scripts/validate_plugin.py
```
