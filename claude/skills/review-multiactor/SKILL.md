---
name: review-multiactor
description: Review a GitHub pull request with three independent actors (E2E Reviewer, Independent Inventor, Code Inspector) and return complete local reports with reconciled findings and proposed diffs/comments. Never create, append to, modify, submit, dismiss, or delete GitHub reviews or PR comments, including pending reviews. Use for "/review-multiactor [PR]", "multi-actor review" or any request for a thorough independent review of a PR.
argument-hint: "[PR URL, OWNER/REPO#N, or number] [design document URL]"
---

Run the review as a multi-actor process. Both arguments are optional: the first can name the pull request (a URL, OWNER/REPO#N, or a number when the repository is known), and the second can reference the design document behind the PR. This workflow runs a report-only review and returns proposed fixes as local diffs.

## Report-only boundary

Do not create, append to, modify, submit, dismiss, or delete GitHub reviews or PR comments, including private pending reviews. Leave existing pending reviews and all their comments untouched. This rule applies to the foreground agent and every actor, to the user's own PRs and other authors' PRs, and to direct invocations and calls from another workflow. Invocation and caller publication instructions cannot authorize these writes within this skill. Keep any requested publication as a separate, explicitly authorized action outside this skill; finish the complete local report first.

## Resolve the PR and supplied context

Before collecting review inputs, read the invocation, governing prompt, caller-provided context, and any referenced handoff files. Resolve the PR from those sources; do not ask for information already supplied. Resolve conflicting target instructions before reviewing; if the intended target remains ambiguous, ask a focused clarification.

If no target is supplied, identify the matching repository and current branch, then use `gh pr view --json url,number` there or an available equivalent. Continue when discovery identifies one PR unambiguously. Ask which PR to review only when context and discovery cannot resolve a unique target. If a known PR is inaccessible, report the actual access or authentication problem instead of asking for its ID again.

Inventory supplied PR metadata, diff, pinned commits, checkout/worktrees, issue/design context, and discussion. Reuse each usable input associated with the selected PR and comparison; fetch or prepare only missing material. Do not download or regenerate a supplied usable diff. Preserve the caller's pinned comparison, review constraints, and local output format. Keep publication requests outside this skill under the report-only boundary. Reuse supplied review inputs without treating them as authorization for GitHub writes or bypassing the freshness checks below.

## Prepare the review

Read applicable repository guidance. Using the supplied inputs first, identify the matching local clone and record the head SHA, base repository and ref, base SHA, and merge-base SHA. Fetch only missing metadata or Git objects. If the caller has not pinned a comparison, pin it from the merge base to the head. Obtain a diff only if a usable one was not supplied. Review that pinned comparison throughout. Reuse supplied checkouts/worktrees at the pinned commits; create detached worktrees only where needed for the head or comparison base. Never check out the PR in the user's working tree. Do not change tracked source files; return proposed changes as diffs. Give actors separate scratch directories or worktrees when builds or probes could interfere.

Collect missing portions of the issue, PR description, commit messages, and complete GitHub discussion, including paginated inline threads, reviews, and general comments. Use available connected tools or authenticated `gh`. Report inaccessible context as a review limitation and continue with available evidence. Keep solution material out of the Independent Inventor's brief until its designated stage, including material from caller handoffs.

Actors may compile, run tests, and write local probes. Use the configured AWS SDK/CLI credential chain and profile; never assume a home directory or read credentials into a prompt. If authentication expires, have the foreground agent ask the user to refresh the configured session while actors continue independent work. Run DynamoDB probes against a local emulator or an explicitly authorized test target.

The process involves background actors.
1. One actor reviews the solution end-to-end, completely and holistically. Let's call this actor the "E2E Reviewer".
2. A second actor is given the information incrementally (the problem description, the textual description of the solution, the commit descriptions, the code) in order to re-do the investigation and then evaluate how good the reviewed solution is, compared to what this actor was able to invent. Let's call this actor the "Independent Inventor".
3. A third actor inspects the code and aims to optimise it: its volume, performance and clarity. Let's call this actor the "Code Inspector".

Each actor is a background subagent with its own context: give it the texts it needs in its brief. The Independent Inventor is one subagent continued stage by stage; until a stage hands the PR with the solution to it, it must not look at the PR with the solution on its own, and its first stage works in a worktree at the PR's merge base.

Use native subagent tools with fresh contexts, not forks of the foreground conversation. Retain agent IDs and resume the same Inventor after each written stage result. Give each actor repository guidance, permitted inputs, assigned paths, and required output. Tell actors they are not alone, must not modify or revert others' files, and must keep generated artifacts in their assigned scratch locations. Pass the report-only boundary to every actor. Actors must return findings and proposed comments to the foreground agent for local reporting. If native delegation is unavailable, report the blocker; do not claim independent reviews completed.

Until the Inventor returns its independent test plan, withhold proposed test content, including test diffs in descriptions or commit messages, GitHub discussion, and other actors' reports. Defer these inputs until the test-comparison follow-up. Instruct the Inventor not to inspect withheld material through Git, shared files, or tools. Report unavoidable prior exposure, including solution details in the issue or design, as a limitation.

The actors are to be instructed as follows.

1. The E2E Reviewer should be asked to read the issue (most likely: the Jira work item) described as being solved (fixed) by the PR, the cover letter of the solution (the PR description), the commit messages and the code. The actor should evaluate the correctness of the code, the accuracy and communicability of the commit messages encapsulating the code, and how the solution is described by the cover letter. To understand the broader context, the Reviewer should attempt to find the epic-type parent of the Jira work item being resolved, as well as the sibling work items under the same parent and read the cover letters of the PRs resolving the siblings. The Reviewer should also read the design document given in the brief (or the relevant one, if any exists) for broader context, as well as the relevant part of DynamoDB's documentation. The Reviewer should also read all the comments in the PR's discussion on GH, and treat what they claim as something to verify in the code, not as settled. The code of the PR in review should also be evaluated for being correct, minimal and efficient, and for re-using what the pre-existing code already contains instead of re-implementing it. Unclear places in the code (wherever the rationale or the purpose could be unclear, or a human would need some time to understand the result of some piece) need a short, communicative code comment; propose it. It should also evaluate the test coverage of the new code - it needs to be sufficiently comprehensive and the tests should properly re-use the available fixtures and helpers. The coverage should prefer extending the existing tests whenever their scope is compatible with the extension, instead of adding new tests.
The evaluation should result in constructive suggestions with diffs describing the proposed improvements.
Run the E2E Reviewer using the latest version of Opus with effort at high.

2. The Independent Inventor should first be given only the problem description (most likely: the Jira work item). The Inventor should attempt to gather the full context of the problem: the parent epic-type work item in Jira if any, the sibling work items under the same parent, their PRs' cover letters, the design document given in the brief (or the relevant one, if any exists) for broader context, as well as the relevant part of DynamoDB's documentation. The aim of this step is to create a plan in prose for an optimal solution.
After the plan is formed, it should be given the description of the solution being reviewed (most likely: the PR's cover letter) and asked to compare and evaluate its plan with how the reviewed solution decided to solve the problem. Make the Inventor evaluate the clarity and the ambiguity of the cover letter too.
After this is done and summarised, the next separate step is to evaluate how the solution's description (the PR's cover letter) matches what the solution actually does. Read the commit messages to get a more detailed view of the solution. Then read production-only diffs and the production code and comments in each commit, deferring proposed test content and GitHub discussion. The code itself needs to be correct, minimal and generally optimal for the solution, while the comments should clarify the context, the aim or the action wherever they could be unclear to a future code reader. The volume of the comments should be minimal for the purpose. After the Inventor learns what the code does, it should make sure the commit messages describe the code optimally - the key rationale and the high-level effect of adding the new code need to be described in the commit messages, not the noisy details.
After this is done and summarised, the next step is to evaluate the test coverage. Form a comprehensive test plan: based on the problem description - to make the tests detect the problem and prevent it from re-appearing (the code from regressing), and based on the code - to ensure proper coverage. Return the written plan before receiving proposed tests or GitHub discussion. In a separate follow-up, supply the test changes, complete GitHub discussion, and deferred excerpts. Compare actual coverage with the independent plan, including reuse of existing fixtures and helpers, and verify discussion claims against the implementation. Return missing cases, proposed test diffs, and any revised implementation findings.
The evaluation should result in constructive suggestions with diffs describing the proposed improvements.
Run the Independent Inventor using the latest version of Fable with effort at high.

3. The Code Inspector will read the code and verify that it properly uses the pieces which the existing codebase already provides: the helpers, the fixtures, the existing classes and tests. The solution should not re-implement code. Use language features supported by the repository's configured versions. The solution's volume should be optimal - attempt to shorten the code without weakening behavior.
The evaluation should result in constructive suggestions with diffs describing the proposed improvements.
Run the Code Inspector using the latest version of Sonnet with effort at high.


Every finding should include impact, triggering condition, and supporting evidence, and come with a proposed code, test, or message diff. Cite path:line at the pinned PR head for code findings. For commit-message or PR-description findings, cite the commit SHA or description section and the code demonstrating the mismatch; do not invent an inline location. Distinguish defects from optional improvements and return an explicit no-findings result when appropriate.


The foreground actor should focus on the following:
1. Bring coherence to the findings: form one coherent and actionable path, or several if there are several. You should generally avoid re-investigating and re-validating the findings, but do investigate and resolve the ones which contradict each other.
2. The key part of your work is communicating the findings clearly and making the comments for the code clear too. Follow the writing rules postulated here: https://en.wikipedia.org/wiki/Simplified_Technical_English#Writing_rules . Reword proposed review comments and code comments for the local report as needed. Aim for the comments to be constructive and to suggest the concrete improvement as diffs (as a GitHub "suggestion" block when the diff replaces exactly the anchored lines). Start each proposed comment with a single line in bold explaining the crux of the suggested change.
3. Send the complete proposed comments back for evaluation to the actors who were the source of the comments (sometimes to several actors). Ask them to validate only the correctness and accuracy of each final proposed comment (both the review comments and the corrected comments for the code) and whether their intended meaning is kept. Resolve corrections before including the comments in the local report.
4. Return the complete reconciled findings with every final proposed comment and code, test, or message diff in the Claude Code console, including findings without inline anchors. Separately provide the suggested review summary and verdict, the pinned comparison, checks performed, and all verification limits. Clearly distinguish defects from optional improvements and state when there are no findings.
5. Show each actor's complete output in the Claude Code console under a clearly labelled heading per actor. For long output, save each complete actor report and the complete synthesis with proposed comments/diffs to local Markdown artifacts and link them under the relevant headings; do not omit content to shorten the conversation. Do not disclose another actor's report to the Inventor before staged disclosure is complete.


## Verify the local report's comparison

Before finalizing the report, recheck the remote head SHA, base repository and ref, and base SHA. Fetch the current base and recompute the merge base. Compare these inputs with the pinned comparison. If any differ, report the mismatch and the comparison actually reviewed. Refresh the comparison only within the caller's constraints, review affected changes, and revalidate findings and proposed inline anchors. If the caller requires the original pins, retain them and explain that the findings apply to that comparison. If freshness cannot be checked, disclose that verification limit.

Check each proposed inline anchor against the pinned diff, including its side and range. Include findings without valid inline anchors in the local report with their source references; do not invent locations or drop findings about commit messages, the PR description, or missing tests.

State in the final report that GitHub reviews and PR comments were left untouched and that any requested publication requires a separate, explicitly authorized action outside this skill.

General remarks:
- If there are cases which are not covered by tests, and the risk of leaving them uncovered is not negligible, propose new tests.
- Don't filter out comments whose diff would be too long; include the key fragment with enough context to apply the idea, and link a local artifact for the complete diff when needed.
- Don't filter the comments based on their count.
