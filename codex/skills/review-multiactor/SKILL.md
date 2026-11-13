---
name: review-multiactor
description: Review a GitHub pull request with three independent Codex subagents (E2E Reviewer, Independent Inventor, Code Inspector), reconcile their findings, and prepare diff-backed comments in a pending GitHub review. Use for "$review-multiactor", "multi-actor review", or a request for a thorough independent PR review.
---

# Multi-actor PR review

Invocation: `$review-multiactor <PR URL or OWNER/REPO#N> [design document URL]`. Ask for the PR if it is missing. The design document is optional. This skill runs a review; it does not implement fixes or submit the review.

## Prepare the review

Read applicable repository guidance. Identify the matching local clone, fetch the PR, and record its head SHA, base repository and ref, base SHA, and merge-base SHA. Pin the review diff from that merge base to the head. Review that pinned comparison throughout. Create detached worktrees for the head and merge base; never check out the PR in the user's working tree. Give actors separate scratch directories or worktrees when builds or probes could interfere. Do not change tracked source files; return proposed changes as diffs.

Collect the issue or Jira work item, PR description, commit messages, diff, and complete GitHub discussion, including paginated inline threads, reviews, and general comments. Keep solution material out of the Independent Inventor's brief until its designated stage. Use available connected tools for Jira, GitHub, and design documents, or `gh` when appropriate. Report inaccessible sources as review limitations and continue with available evidence.

Find the issue's parent epic, sibling work items, and sibling PR descriptions when relevant. Read the supplied or discoverable design document and relevant official product documentation, including DynamoDB documentation when the change concerns DynamoDB.

Actors may compile, run tests, and write local probes. For AWS access, use the configured SDK/CLI credential chain and profile; never assume a home directory or read credentials into a prompt. If authentication expires, ask the user to refresh the configured session while continuing independent work. Run DynamoDB probes against a local emulator or an explicitly authorized test target.

## Coordinate Codex subagents

Use Codex's available native subagent tools; see the [official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) for configuration. In a runtime exposing the `collaboration` namespace:

- Create three `collaboration.spawn_agent` tasks named `e2e_reviewer`, `independent_inventor`, and `code_inspector`, with `agent_type: "default"` and `fork_turns: "none"`. Give each a self-contained brief with its role, permitted inputs, repository guidance, worktree paths, and required output. Fresh contexts prevent the Inventor from inheriting the PR solution.
- Use the active Codex model by omitting `model`. Request `reasoning_effort: "high"` when the runtime supports and permits that override; otherwise inherit the session's reasoning setting. Do not select model names from memory or change the user's model configuration.
- Run E2E Reviewer and Code Inspector independently while the Inventor advances through its stages. Continue the same Inventor agent with `collaboration.followup_task` after each stage completes. Use `collaboration.send_message` for updates to a running actor and `collaboration.wait_agent` for results. Retain agent IDs for final-comment validation.
- Actors share the filesystem. Tell them they are not alone, must not modify or revert others' files, and must keep generated artifacts in their assigned scratch locations. Actors must return findings to the foreground agent and must not write to GitHub. Only the foreground agent may prepare pending review comments.

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

Send each complete final comment, including rewritten code comments and diffs, back to its originating actor or actors. Ask only whether it remains correct, accurate, and faithful to the finding. Continue completed agents with a follow-up task. Resolve corrections before adding comments to GitHub.

## Prepare a pending GitHub review

Invoking this review workflow authorizes preparing private pending review comments. Honor any narrower user instruction such as a local-only review. Keep summary, verdict, and findings about commit messages, the PR description, or missing tests in the Codex conversation when they lack a valid inline anchor.

Before each write, including a retry, recheck the remote head SHA, base repository and ref, and base SHA. Fetch the current base and recompute the merge base. Compare these inputs with the pinned comparison. If any differ, stop adding comments and report the mismatch; refresh the comparison, review affected changes, and revalidate findings and inline anchors before continuing. Identify the authenticated GitHub account and its existing pending review for this PR. Reuse that review and preserve existing comments.

Use only a tool operation whose documented behavior leaves comments in a **PENDING** review. If no pending review exists, create one at the pinned head. With the [GitHub REST API](https://docs.github.com/en/rest/pulls/reviews#create-a-review-for-a-pull-request), creating a review with `commit_id` and inline `comments` while omitting `event` creates a pending review.

To extend an existing pending review, use a documented operation targeting either its review ID or the authenticated user's pending review for the specified PR. For example, `mcp__github__add_comment_to_pending_review` targets the requester's latest pending review using `owner`, `repo`, and `pullNumber`; it requires no review-ID argument. Before appending, verify that this selection identifies the intended existing review and record its ID and pending state. Verify the same review ID, state, and added comment after each append. If selection is ambiguous or available tools cannot safely append, keep the remaining drafts in the Codex conversation and report the limitation. Do not fall back to a standalone PR comment.

Never call review submission, `gh pr review`, standalone comment publication, or an operation that publishes an approval or change-request verdict. Never submit, dismiss, delete, or replace the user's pending review. Check each inline anchor against the pinned diff, including its side and range. If no valid anchor exists, retain the finding in the conversation.

After a write, verify the review ID, pending state, and intended comments. If a request times out or has an ambiguous result, inspect the pending review and its comments before retrying; avoid duplicates. If the result cannot be verified, stop writes and report the uncertainty.

## Report in Codex

Show each actor's complete output in the Codex conversation under a clearly labeled heading. For long output, save each complete report to a local Markdown file and link it under the actor's heading. Do not disclose another actor's report to the Inventor before staged disclosure is complete.

Separately provide the proposed review summary and verdict, findings without inline anchors, review limitations, and the pending review's ID or link. Do not repeat the inline comments in this synthesis. State that the review remains pending for the user to submit. If no review was created, state that instead.
