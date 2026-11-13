# code-review-multifactor

A standalone Claude Code and Codex plugin for multi-actor GitHub pull-request reviews. Version 1.1.0. MIT licensed.

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

In Codex, select `review-multiactor`, or invoke it with a pull-request URL or `OWNER/REPO#N` and an optional design document URL:

```text
$review-multiactor https://github.com/OWNER/REPO/pull/123
$review-multiactor OWNER/REPO#123 https://example.com/design
```

Each host's skill coordinates three native subagents:

- **E2E Reviewer:** checks requirements, implementation, commit messages, PR description, discussion, and tests.
- **Independent Inventor:** develops an independent solution plan, then evaluates the description, production code, and tests through staged disclosure.
- **Code Inspector:** checks reuse, clarity, performance, and unnecessary code.

The foreground agent reconciles findings and returns final comments to their source actors for validation. It prepares inline findings in the authenticated user's pending GitHub review and leaves submission to the user. Existing pending comments are preserved. A local-only request keeps all findings in the host conversation.

Both workflows review in detached worktrees and propose improvements as diffs. Both pin the PR comparison and revalidate head, base, and merge-base changes before further review writes. Actors return findings without writing to GitHub. The Independent Inventor returns its test plan before receiving proposed tests or GitHub discussion.

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
