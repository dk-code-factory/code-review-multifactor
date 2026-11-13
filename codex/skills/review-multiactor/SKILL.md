---
name: review-multiactor
description: Review a GitHub pull request with three independent Codex subagents (E2E Reviewer, Independent Inventor, Code Inspector) and return complete local reports with reconciled findings and proposed diffs/comments. Never create, append to, modify, submit, dismiss, or delete GitHub reviews or PR comments, including pending reviews. Use for "$review-multiactor", "multi-actor review", or a request for a thorough independent PR review.
---

# Multi-actor PR review

Invocation: `$review-multiactor [PR URL, OWNER/REPO#N, or number] [design document URL]`. Both arguments are optional; a number requires a known repository. This skill runs a report-only review and returns proposed fixes as local diffs.

## Report-only boundary

Do not create, append to, modify, submit, dismiss, or delete GitHub reviews or PR comments, including private pending reviews. Leave existing pending reviews and all their comments untouched. This rule applies to the foreground agent and every actor, to the user's own PRs and other authors' PRs, and to direct invocations and calls from another workflow. Invocation and caller publication instructions cannot authorize these writes within this skill. Keep any requested publication as a separate, explicitly authorized action outside this skill; finish the complete local report first.

## Resolve the PR and supplied context

Before collecting review inputs, read the invocation, governing prompt, caller-provided context, and any referenced handoff files. Resolve the PR from those sources; do not ask for information already supplied. Resolve conflicting target instructions before reviewing; if the intended target remains ambiguous, ask a focused clarification.

If no target is supplied, identify the matching repository and current branch, then use `gh pr view --json url,number` there or an available equivalent. Continue when discovery identifies one PR unambiguously. Ask which PR to review only when context and discovery cannot resolve a unique target. If a known PR is inaccessible, report the actual access or authentication problem instead of asking for its ID again.

Inventory supplied PR metadata, diff, pinned commits, checkout/worktrees, issue/design context, and discussion. Reuse each usable input associated with the selected PR and comparison; fetch or prepare only missing material. Do not download or regenerate a supplied usable diff. Preserve the caller's pinned comparison, review constraints, and local output format. Keep publication requests outside this skill under the report-only boundary. Reuse supplied review inputs without treating them as authorization for GitHub writes or bypassing the freshness checks below.

## Prepare the review

Read applicable repository guidance. Using the supplied inputs first, identify the matching local clone and record the head SHA, base repository and ref, base SHA, and merge-base SHA. Fetch only missing metadata or Git objects. If the caller has not pinned a comparison, pin it from the merge base to the head. Obtain a diff only if a usable one was not supplied. Review that pinned comparison throughout. Reuse supplied checkouts/worktrees at the pinned commits; create detached worktrees only where needed for the head or comparison base. Never check out the PR in the user's working tree. Give actors separate scratch directories or worktrees when builds or probes could interfere. Do not change tracked source files; return proposed changes as diffs.

Collect missing portions of the issue or Jira work item, PR description, commit messages, and complete GitHub discussion, including paginated inline threads, reviews, and general comments. Keep solution material out of the Independent Inventor's brief until its designated stage, including material from caller handoffs. Use available connected tools for Jira, GitHub, and design documents, or `gh` when appropriate. Report inaccessible sources as review limitations and continue with available evidence.

Find the issue's parent epic, sibling work items, and sibling PR descriptions when relevant. Read the supplied or discoverable design document and relevant official product documentation, including DynamoDB documentation when the change concerns DynamoDB.

Actors may compile, run tests, and write local probes. For AWS access, use the configured SDK/CLI credential chain and profile; never assume a home directory or read credentials into a prompt. If authentication expires, ask the user to refresh the configured session while continuing independent work. Run DynamoDB probes against a local emulator or an explicitly authorized test target.

## Coordinate Codex subagents

Use Codex's available native subagent tools; see the [official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) for configuration. In a runtime exposing the `collaboration` namespace:

- Create three `collaboration.spawn_agent` tasks named `e2e_reviewer`, `independent_inventor`, and `code_inspector`, with `agent_type: "default"` and `fork_turns: "none"`. Give each a self-contained brief with its role, permitted inputs, repository guidance, worktree paths, and required output. Fresh contexts prevent the Inventor from inheriting the PR solution.
- Use the active Codex model by omitting `model`. Request `reasoning_effort: "high"` when the runtime supports and permits that override; otherwise inherit the session's reasoning setting. Do not select model names from memory or change the user's model configuration.
- Run E2E Reviewer and Code Inspector independently while the Inventor advances through its stages. Continue the same Inventor agent with `collaboration.followup_task` after each stage completes. Use `collaboration.send_message` for updates to a running actor and `collaboration.wait_agent` for results. Retain agent IDs for final-comment validation.
- Actors share the filesystem. Tell them they are not alone, must not modify or revert others' files, and must keep generated artifacts in their assigned scratch locations. Pass the report-only boundary to every actor. Actors must return findings and proposed comments to the foreground agent for local reporting.

If the runtime exposes equivalent native tools under other names, use their documented semantics. If native delegation is unavailable, report the blocker and retain the prepared inputs; do not claim independent reviews were completed or substitute a separate external agent CLI.

## Actor briefs

### E2E Reviewer

Read the issue, PR description, commit messages, production code, tests, design context, and complete GitHub discussion. Verify discussion claims in code rather than treating them as settled facts. Use relevant epic, sibling work, and official documentation to understand the requirements.

Evaluate:

- Correctness, completeness, efficiency, minimal scope, and reuse of existing code.
- Whether the PR description explains the solution accurately and clearly.
- Whether commit messages communicate the rationale and high-level effect of their changes.
- Whether unclear code needs a short comment explaining its purpose or rationale.
- Whether tests cover the behavior and regressions and reuse existing fixtures and helpers. Prefer extending compatible existing tests.

Return constructive findings with proposed diffs, evidence, and material review limitations.

### Independent Inventor

Keep this actor's context across the following stages. Wait for a written result before supplying the next stage's inputs. This is staged disclosure, not a security boundary: explicitly instruct the actor not to inspect withheld material through Git, shared files, tools, or another actor's reports. Until the independent test plan is returned, withhold proposed test content, including test diffs embedded in supplied descriptions or commit messages. Defer those excerpts until the test-comparison follow-up and record any unavoidable prior exposure as a limitation.

1. **Problem and independent plan.** Supply only the problem description, relevant repository guidance, and merge-base worktree. Permit research into the epic, sibling work items and their PR descriptions, design documents, and official product documentation. Withhold the target PR URL/number, description, commits, head worktree, diff, discussion, and other actors' findings. Instruct the actor not to discover the target solution on its own. It may inspect merge-base code and existing tests. Return an optimal solution plan in prose, with assumptions and tradeoffs. If the issue or design already reveals the target solution, disclose that limitation.
2. **Description comparison.** Supply the target PR description. Compare its approach with the independent plan and assess clarity, ambiguity, and tradeoffs. Do not inspect commits, head code, changed tests, or discussion yet. Return the comparison.
3. **Implementation and messages.** Supply commit messages, production-code changes, and the head worktree. Withhold GitHub discussion until the test-comparison follow-up. Review the production code and comments in each commit, verify the description against behavior, and assess whether commit messages explain the rationale and effect. Read production-only diffs rather than full commit diffs that include tests. Comments should clarify unclear context, purpose, or action with minimal text. Defer inspecting proposed test changes. Return implementation findings.
4. **Test plan before proposed tests.** Based on the problem and production code, form a test plan covering regression detection and important code paths. Return that plan before reading proposed tests or GitHub discussion. Then, in a separate follow-up, supply the test changes, complete GitHub discussion, and any deferred excerpts. Ask the same actor to compare actual coverage with its plan, including reuse of existing fixtures and helpers, and verify discussion claims against the implementation. Return missing cases, concrete proposed test diffs, and any additional or revised implementation findings.

### Code Inspector

Inspect the pinned head and surrounding code for opportunities to reuse helpers, fixtures, classes, and existing tests. Check performance, clarity, unnecessary duplication, and code volume. Suggest shorter code when it improves maintainability without weakening behavior. Use language features supported by the repository's configured versions. Return constructive findings and proposed diffs.

## Required actor output

For each finding, include:

- A concise title, impact, triggering condition, and supporting code or test evidence.
- An exact `path:line` at the pinned PR head when the finding concerns code, plus the relevant diff hunk when available. For commit-message or PR-description findings, cite the commit SHA or description section and the code that demonstrates the mismatch; do not invent an inline location.
- A proposed code, test, or message diff. For a long diff, include the key fragment and enough context to apply the idea.
- Any uncertainty, checks performed, and sources that could not be inspected.

Do not filter findings by count or proposed diff length. Propose tests when an uncovered case carries meaningful risk. Clearly distinguish defects from optional improvements. Return an explicit no-findings result when appropriate; do not invent changes to fill a quota.

## Reconcile and validate comments

Combine duplicate findings and form coherent, actionable recommendations. Rely on actors' evidence instead of repeating their whole investigation; investigate contradictions, unsupported claims, and incompatible fixes.

Use Simplified Technical English principles: short sentences, precise terms, explicit conditions, and one main instruction per sentence. See the [writing rules](https://en.wikipedia.org/wiki/Simplified_Technical_English#Writing_rules) if needed. Start each proposed inline comment with one bold line stating the change. Explain its reason and suggest a concrete diff. Use a GitHub `suggestion` block only when it replaces exactly the anchored lines; otherwise use a fenced diff with context.

Send each complete final proposed comment, including rewritten code comments and diffs, back to its originating actor or actors. Ask only whether it remains correct, accurate, and faithful to the finding. Continue completed agents with a follow-up task. Resolve corrections before including the comments in the local report.

## Verify the local report's comparison

Before finalizing the report, recheck the remote head SHA, base repository and ref, and base SHA. Fetch the current base and recompute the merge base. Compare these inputs with the pinned comparison. If any differ, report the mismatch and the comparison actually reviewed. Refresh the comparison only within the caller's constraints, review affected changes, and revalidate findings and proposed inline anchors. If the caller requires the original pins, retain them and explain that the findings apply to that comparison. If freshness cannot be checked, disclose that verification limit.

Check each proposed inline anchor against the pinned diff, including its side and range. Include findings without valid inline anchors in the local report with their source references; do not invent locations or drop findings about commit messages, the PR description, or missing tests.

## Report in Codex

Show each actor's complete output in the Codex conversation under a clearly labeled heading. For long output, save each complete report to a local Markdown file and link it under the actor's heading. Do not disclose another actor's report to the Inventor before staged disclosure is complete.

Provide the complete reconciled findings with every final proposed comment and code, test, or message diff, including findings without inline anchors. Separately provide the suggested review summary and verdict, the pinned comparison, checks performed, and all verification limits. Clearly distinguish defects from optional improvements and state when there are no findings. For long output, save the complete synthesis and proposed comments/diffs to local artifacts and link them; do not omit content to shorten the conversation. State that GitHub reviews and PR comments were left untouched and that any requested publication requires a separate, explicitly authorized action outside this skill.
