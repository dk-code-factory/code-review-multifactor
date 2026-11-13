# code-review-multifactor

A standalone Claude Code and Codex plugin for report-only multi-actor GitHub pull-request reviews. Version 1.1.3. MIT licensed.

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

The repository, plugin, and included skill are all named `code-review-multifactor`.

Update saved skill invocations to `code-review-multifactor:code-review-multifactor`.

## Use

In Claude Code, invoke the namespaced skill:

```text
/code-review-multifactor:code-review-multifactor OWNER/REPO#123
```

In Codex, select `code-review-multifactor`, or invoke it with an optional pull-request URL, `OWNER/REPO#N`, or PR number when the repository is known, plus an optional design document URL:

```text
$code-review-multifactor https://github.com/OWNER/REPO/pull/123
$code-review-multifactor OWNER/REPO#123 https://example.com/design
$code-review-multifactor 123
```

Both hosts resolve the PR from the invocation, governing prompt, or caller context, including referenced handoff files. Without a supplied target, they discover the PR for the current branch in the matching repository. For example, run either command from a branch with an open PR:

```text
/code-review-multifactor:code-review-multifactor
$code-review-multifactor
```

They ask only when the target cannot be resolved unambiguously or conflicting target instructions need clarification. A known PR's access failure is reported as an access problem.

When called by dk-workflows or another workflow, both hosts reuse supplied metadata, diffs, pinned commits, checkouts/worktrees, and discussion for the selected PR and comparison. They collect only missing inputs, preserve the caller's pinned comparison, review constraints, and local output format, and check comparison freshness before finalizing the local report. A handoff can be referenced in the governing prompt without repeating the PR as a positional argument:

```text
Use $code-review-multifactor with the dk-workflows handoff at /tmp/pr-review/handoff.md.
It identifies the PR and pinned comparison and supplies the diff and worktrees.
Return the complete review and proposed comments/diffs in the conversation or linked local artifacts.
```

The same handoff instructions apply to Claude's `/code-review-multifactor:code-review-multifactor`. No workflow configuration changes or runtime helper are required.

Each host's skill coordinates three native subagents:

- **E2E Reviewer:** checks requirements, implementation, commit messages, PR description, discussion, and tests.
- **Independent Inventor:** develops an independent solution plan, then evaluates the description, production code, and tests through staged disclosure.
- **Code Inspector:** checks reuse, clarity, performance, and unnecessary code.

The foreground agent reconciles findings and returns final proposed comments to their source actors for validation. Every review returns the complete reconciled findings, proposed comments and code/test/message diffs, each actor's complete report, a suggested summary and verdict, and verification limits. Long reports are saved to linked local artifacts. Findings without valid inline anchors remain in the local report with source references.

Neither host creates, appends to, modifies, submits, dismisses, or deletes GitHub reviews or PR comments, including private pending reviews. Existing pending reviews and their comments are left untouched. This applies to your own PRs, other authors' PRs, and workflow callers. Invocation and caller publication instructions cannot enable these writes within the skill. Any requested publication is a separate, explicitly authorized action outside this review skill, after the complete local report is returned.

Both workflows reuse supplied checkouts at the pinned commits or prepare detached worktrees as needed, and propose improvements as diffs. Both preserve or pin the PR comparison and report head, base, or merge-base changes and any freshness verification limits. The foreground agent and actors all follow the report-only boundary. The Independent Inventor returns its test plan before receiving proposed tests or GitHub discussion.

The Claude skill was adapted from the original Claude Code review skill. It retains its Opus, Fable, and Sonnet model requests with high effort. Codex uses its separately maintained native adaptation.

## Requirements

- Claude Code or Codex with native subagent tools enabled and enough capacity for three reviewers. Claude follows the imported model requests above. Codex actors inherit the active model; high reasoning is requested only when supported and permitted.
- Git and a matching local repository clone.
- Read access to GitHub PR metadata, diffs, and discussion through connected tools or authenticated `gh`. The skill needs no review or comment write permissions.
- Access to the linked issue, Jira work item, or design document when available. Inaccessible context is reported as a limitation.
- The repository's build and test tools when execution is needed. Both workflows use a local emulator or an explicitly authorized test target and the configured AWS credential chain for DynamoDB probes.

## Layout

- `.codex-plugin/plugin.json`: Codex plugin metadata.
- `.agents/plugins/marketplace.json`: Codex plugin catalog.
- `.claude-plugin/plugin.json`: Claude Code plugin metadata.
- `.claude-plugin/marketplace.json`: Claude Code plugin catalog.
- `codex/skills/code-review-multifactor/SKILL.md`: Codex review workflow.
- `claude/skills/code-review-multifactor/SKILL.md`: Claude Code review workflow.

The plugin contains its own skill instructions and has no build step or external runtime helper dependency.

## Validation

GitHub Actions validates both hosts' skill frontmatter, host skill paths, plugin/catalog metadata, release version consistency, and whitespace on pull requests and pushes to `main`.

Run the metadata and skill checks locally with:

```sh
python -m pip install PyYAML==6.0.3
python scripts/validate_plugin.py
```
