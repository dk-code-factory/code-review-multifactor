# code-review-multifactor

A standalone Codex plugin for multi-actor GitHub pull-request reviews. Version 1.0.0. MIT licensed.

## Install

```sh
codex plugin marketplace add dk-code-factory/code-review-multifactor
codex plugin add code-review-multifactor@code-review-multifactor
```

Start a new Codex session after installation. This repository catalogs only its own plugin and requires no other review plugin.

The repository and plugin are named `code-review-multifactor`. The included skill keeps its existing name, `review-multiactor`.

## Use

Select `review-multiactor` in Codex, or invoke it with a pull-request URL or `OWNER/REPO#N` and an optional design document URL:

```text
$review-multiactor https://github.com/OWNER/REPO/pull/123
$review-multiactor OWNER/REPO#123 https://example.com/design
```

The skill coordinates three native Codex subagents:

- **E2E Reviewer:** checks requirements, implementation, commit messages, PR description, discussion, and tests.
- **Independent Inventor:** develops an independent solution plan, then evaluates the description, production code, and tests through staged disclosure.
- **Code Inspector:** checks reuse, clarity, performance, and unnecessary code.

Codex reconciles their findings and returns final comments to their source actors for validation. It prepares inline findings in the authenticated user's pending GitHub review and leaves submission to the user. Existing pending comments are preserved. A local-only request keeps all findings in the conversation.

The review uses detached worktrees and a pinned PR comparison. Head, base, and merge-base changes trigger revalidation before further review writes. Proposed fixes are returned as diffs; the skill does not edit the reviewed source.

## Requirements

- Codex with native subagent tools enabled and enough capacity for three reviewers. Actors inherit the active model; high reasoning is requested only when supported and permitted.
- Git and a matching local repository clone.
- GitHub access through connected tools or authenticated `gh`, including permission to prepare pending reviews when requested.
- Access to the linked issue, Jira work item, or design document when available. Inaccessible context is reported as a limitation.
- The repository's build and test tools when execution is needed. DynamoDB probes use a local emulator or an explicitly authorized test target and the configured AWS credential chain.

## Layout

- `.codex-plugin/plugin.json`: Codex plugin metadata.
- `.agents/plugins/marketplace.json`: repository-local plugin catalog.
- `codex/skills/review-multiactor/SKILL.md`: complete review workflow.

The plugin contains its own skill instructions and has no build step or external runtime helper dependency.
