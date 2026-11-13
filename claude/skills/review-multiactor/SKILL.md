---
name: review-multiactor
description: Review a GitHub pull request as a multi-actor process - three background actors (E2E Reviewer, Independent Inventor, Code Inspector) each evaluate the Jira work item, the cover letter, the commit messages, the code and the test coverage, and the foreground agent merges their findings into a pending GitHub review with STE-worded, diff-backed comments. Use for "/review-multiactor <PR>", "multi-actor review" or any request for a thorough independent review of a PR.
argument-hint: "<PR URL or OWNER/REPO#N> [design document URL]"
---

Run the review as a multi-actor process. The first argument names the pull request (a URL or OWNER/REPO#N); without it, ask which one. The second, optional argument is a reference to the design document behind the PR. Fetch the PR head into a detached worktree of the matching local clone, never into the user's working tree; the actors read the code there, and they may compile and run it, run the tests, and write and run probes against DynamoDB when they need to - if the AWS token in '/home/hollow/.aws/credentials' is stale, they should ask for a fresh one.

The process involves background actors.
1. One actor reviews the solution end-to-end, completely and holistically. Let's call this actor the "E2E Reviewer".
2. A second actor is given the information incrementally (the problem description, the textual description of the solution, the commit descriptions, the code) in order to re-do the investigation and then evaluate how good the reviewed solution is, compared to what this actor was able to invent. Let's call this actor the "Independent Inventor".
3. A third actor inspects the code and aims to optimise it: its volume, performance and clarity. Let's call this actor the "Code Inspector".

Each actor is a background subagent with its own context: give it the texts it needs in its brief. The Independent Inventor is one subagent continued stage by stage; until a stage hands the PR with the solution to it, it must not look at the PR with the solution on its own, and its first stage works in a worktree at the PR's merge base.

The actors are to be instructed as follows.

1. The E2E Reviewer should be asked to read the issue (most likely: the Jira work item) described as being solved (fixed) by the PR, the cover letter of the solution (the PR description), the commit messages and the code. The actor should evaluate the correctness of the code, the accuracy and communicability of the commit messages encapsulating the code, and how the solution is described by the cover letter. To understand the broader context, the Reviewer should attempt to find the epic-type parent of the Jira work item being resolved, as well as the sibling work items under the same parent and read the cover letters of the PRs resolving the siblings. The Reviewer should also read the design document given in the brief (or the relevant one, if any exists) for broader context, as well as the relevant part of DynamoDB's documentation. The Reviewer should also read all the comments in the PR's discussion on GH, and treat what they claim as something to verify in the code, not as settled. The code of the PR in review should also be evaluated for being correct, minimal and efficient, and for re-using what the pre-existing code already contains instead of re-implementing it. Unclear places in the code (wherever the rationale or the purpose could be unclear, or a human would need some time to understand the result of some piece) need a short, communicative code comment; propose it. It should also evaluate the test coverage of the new code - it needs to be sufficiently comprehensive and the tests should properly re-use the available fixtures and helpers. The coverage should prefer extending the existing tests whenever their scope is compatible with the extension, instead of adding new tests.
The evaluation should result in constructive suggestions with diffs describing the proposed improvements.
Run the E2E Reviewer using the latest version of Opus with effort at high.

2. The Independent Inventor should first be given only the problem description (most likely: the Jira work item). The Inventor should attempt to gather the full context of the problem: the parent epic-type work item in Jira if any, the sibling work items under the same parent, their PRs' cover letters, the design document given in the brief (or the relevant one, if any exists) for broader context, as well as the relevant part of DynamoDB's documentation. The aim of this step is to create a plan in prose for an optimal solution.
After the plan is formed, it should be given the description of the solution being reviewed (most likely: the PR's cover letter) and asked to compare and evaluate its plan with how the reviewed solution decided to solve the problem. Make the Inventor evaluate the clarity and the ambiguity of the cover letter too.
After this is done and summarised, the next separate step is to evaluate how the solution's description (the PR's cover letter) matches what the solution actually does. Read the commit messages to get a more detailed view of the solution. Then read the code and the comments in each commit. The code itself needs to be correct, minimal and generally optimal for the solution, while the comments should clarify the context, the aim or the action wherever they could be unclear to a future code reader. The volume of the comments should be minimal for the purpose. After the Inventor learns what the code does, it should make sure the commit messages describe the code optimally - the key rationale and the high-level effect of adding the new code need to be described in the commit messages, not the noisy details. Only at this stage should the Inventor also read all the comments in the PR's discussion on GH.
After this is done and summarised, the next step is to evaluate the test coverage. Form a comprehensive test plan: based on the problem description - to make the tests detect the problem and prevent it from re-appearing (the code from regressing), and based on the code - to ensure proper coverage. Only then look at the tests proposed by the solution, and document the differences.
The evaluation should result in constructive suggestions with diffs describing the proposed improvements.
Run the Independent Inventor using the latest version of Fable with effort at high.

3. The Code Inspector will read the code and verify that it properly uses the pieces which the existing codebase already provides: the helpers, the fixtures, the existing classes and tests. The solution should not re-implement code. The solution should use what modern versions of the programming languages enable. The solution's volume should be optimal - attempt to shorten the code.
The evaluation should result in constructive suggestions with diffs describing the proposed improvements.
Run the Code Inspector using the latest version of Sonnet with effort at high.


Every finding should cite its place as path:line at the PR head, verified in the code, and come with a diff of the code or diff of the message.


The foreground actor should focus on the following:
1. Bring coherence to the findings: form one coherent and actionable path, or several if there are several. You should generally avoid re-investigating and re-validating the findings, but do investigate and resolve the ones which contradict each other.
2. The key part of your work is communicating the findings clearly and making the comments for the code clear too. Follow the writing rules postulated here: https://en.wikipedia.org/wiki/Simplified_Technical_English#Writing_rules . You will likely choose to reword all of the GH comments and comments for the code proposed by the actors before publishing them. Aim for the comments to be constructive and to suggest the concrete improvement as diffs (as a GitHub "suggestion" block when the diff replaces exactly the commented lines). Start each posted comment with a single line in bold explaining the crux of the suggested change.
3. Post the complete comments back for evaluation to the actors who were the source of the comments (sometimes to several actors). Ask them to validate only the correctness and accuracy of each final comment (both the GH comments and the corrected comments for the code) and whether their intended meaning is kept.
4. Create a pending review on GH and put the comments there as pending. A pending review is private until submitted. Use only a call that leaves the review in the pending state; anything that publishes a comment or a verdict at once is forbidden. Add to the user's existing pending review when there is one, never submit it. Line comments go there. Propose separately, in the Claude Code console, the review summary and the verdict, along with the findings on commit messages, on the cover letter or on missing tests, but don't repeat the inline comments. The review is submitted on GH by the user.
5. Print the output of each actor in the Claude Code console too, under a clearly labelled heading per actor.


General remarks:
- If there are cases which are not covered by tests, and the risk of leaving them uncovered is not negligible, propose new tests.
- Don't filter out comments whose diff would be too long; post the key fragment of the diff instead.
- Don't filter the comments based on their count.
