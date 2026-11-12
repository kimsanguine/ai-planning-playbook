---
name: ai-project-planning
description: Turn an approved work memo into five linked project documents, then review scope, evidence, human decisions, and the next small validation step. Use for AI product or workflow planning before implementation or when a project decision changes.
---

# AI Project Planning

Use this skill to turn one work memo into a project context that a person and an AI coding agent can read together. It does not approve a product decision, create customer evidence, or authorize external actions.

## Read first

1. Read any existing `docs/customer.md`, `docs/prd.md`, `docs/architecture.md`, `docs/design.md`, and `docs/progress.md` before proposing changes. If a legacy project keeps these at its root, preserve that layout rather than moving files as part of a planning task.
2. Treat the supplied memo, interview notes, and observed results as the only evidence. Mark missing evidence as `미확인` and write the next confirmation action instead of inventing customer claims, outcomes, or metrics.
3. Keep personal data, private links, secrets, and unapproved customer material out of the documents.
4. A person, not the agent, confirms scope, quality thresholds, external delivery, spending, deletion, and production release.

## Create or update the five documents

For a new project, copy all files in [assets/templates](assets/templates) into `docs/`. For an existing project, preserve prior records and change only relevant sections.

| File | Responsibility | Read or update when |
| --- | --- | --- |
| `docs/customer.md` | user evidence, current alternatives, hypotheses | an observed need or source changes |
| `docs/prd.md` | goal, scope, exclusions, quality thresholds | a person changes what the project should do |
| `docs/architecture.md` | input, processing responsibility, human review, recovery | a tool, data boundary, or failure path changes |
| `docs/design.md` | user action, visible result, states, and prototype behavior | a user flow or result presentation changes |
| `docs/progress.md` | the decision, reason, actual result, and next review | a decision or observed result is recorded |

Keep the links between documents explicit. `customer.md` evidence should support `prd.md` quality conditions; `architecture.md` and `design.md` should reference the applicable PRD conditions; `progress.md` should record why the human accepted, rejected, narrowed, or paused the change.

## Workflow

1. **Choose one decision.** State the user outcome, business or operational goal, limits of time, cost, access, and the decision owner.
2. **Separate evidence from assumptions.** Record a recent event, current alternative, source location, and the weakest assumption in `customer.md`.
3. **Set a bounded scope.** In `prd.md`, write included work, excluded work, measurable quality conditions, and what requires human approval.
4. **Design the smallest safe flow.** In `architecture.md`, define inputs, deterministic rules, model work if any, human review, stop conditions, and recovery. In `design.md`, describe the normal and boundary user actions and the visible result.
5. **Plan one validation.** Write a representative input, expected result, owner, date, stop condition, and next review in `progress.md`. Do not record an expected result as an actual result.
6. **Review before implementation.** Check that one decision, its evidence, PRD conditions, implementation boundary, user-facing state, and next validation all point to each other. If they conflict, ask the human to decide before editing code.

## Required final output

When using this skill, report:

1. the single decision and its owner;
2. evidence, assumptions, and what remains unconfirmed;
3. which sections in the five documents were created or changed;
4. the smallest next validation, including input, expected result, stop condition, owner, and date;
5. any action that still needs human approval.

## Reference material

The templates bundled with this skill are runnable project context, not completed product code. The repository's [cases](https://github.com/kimsanguine/ai-planning-playbook/tree/main/cases) and [examples](https://github.com/kimsanguine/ai-planning-playbook/tree/main/examples) are read-only comparison material. Do not copy their fictional or training inputs into a real customer's record.
