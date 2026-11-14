---
name: github-backlog-management
description: Manage GitHub Project (v2) tickets and backlog — create structured issues with Acceptance Criteria, refine existing issues with codebase reconnaissance, groom sprint backlogs, sync Roadmap dates, and update ticket statuses using `gh` CLI and `gh_project.py`.
---

# GitHub Backlog & Ticket Management

Use this skill for day-to-day backlog management on a repository linked to a GitHub Project (v2): creating new issues, refining existing issues, planning sprints, syncing Roadmap dates, and updating ticket statuses.

> **Helper Script (`gh_project.py`)**:
> Resolve `.agents/scripts/gh_project.py` (or `~/.gemini/config/plugins/my-harness/scripts/gh_project.py` if installed globally). If `.agents/harness.config.json` does not yet have a `github_project` cache, run:
> ```bash
> python .agents/scripts/gh_project.py sync --owner <owner> --project-number <number> --repo <owner>/<repo>
> ```

---

## 1. Create a New Issue

1. Use a **business-oriented title** (avoid technical prefixes like `feat:` or `chore:`).
2. Format `--body` to match `.github/ISSUE_TEMPLATE/task.yml`:
   ```markdown
   ### Parent Epic
   Part of #<epic-number>

   ### Summary
   <What this ticket delivers and why it matters>

   ### Acceptance Criteria
   - [ ] <Testable condition 1>
   - [ ] <Testable condition 2>

   ### Technical Notes / Dependencies
   <Optional file hints, reusable modules, or `Depends on #<number>`>
   ```
3. Create the issue, add it to the Project, set `Status` (`Todo`) and `Priority`, and assign its `Sprint` + Roadmap dates:
   ```powershell
   $url = gh issue create --repo <owner>/<repo> --title "<Title>" --body $body
   gh project item-add <project-number> --owner <owner> --url $url
   python .agents/scripts/gh_project.py set-status <issue-number> "Todo"
   python .agents/scripts/gh_project.py assign-sprint <issue-number> "<YYYY.MM.A>"
   ```
4. If linked to a Parent Epic, refresh the Epic's Roadmap dates:
   ```bash
   python .agents/scripts/gh_project.py rollup-epic <epic-number>
   ```

---

## 2. Refine an Existing Issue (Codebase-Grounded Refinement & Readiness Gate)

When refining an issue:

1. **Check Structure & Readiness (`check-ready`)**:
   ```bash
   gh issue view <number> --json number,title,body,labels,comments
   python .agents/scripts/gh_project.py check-ready <number>
   ```
   Ensure the ticket has `### Parent Epic` (if part of an epic), `### Summary` (no `TBD`/`TODO`), and `### Acceptance Criteria` with clear, testable `- [ ]` checkboxes.
2. **Codebase Reconnaissance**:
   - Inspect the codebase to locate affected files, existing modules/abstractions to reuse, and potential blockers (`Depends on #<N>`).
   - Populate `### Technical Notes / Dependencies` with concrete file paths and architectural hints so `/specify` and `/prp-plan` can execute cleanly.
3. **Vertical Slicing & Scope Check**:
   - If the ticket spans $>5$ files across unrelated domains or has $>4$ independent deliverables, prompt the user via `ask_question` to split it into smaller, sprint-sized sub-tickets linked to the same `Parent Epic`.
4. **Definition of Ready (DoR) Check**:
   - Verify `Priority` (`P0 - Critical` to `P3 - Low`) is set and Acceptance Criteria are concrete.
   - Apply the refined body back to GitHub:
     ```powershell
     gh issue edit <number> --repo <owner>/<repo> --body $updatedBody
     ```

---

## 3. Organize Sprint Backlog, Plan Sprints & Sync Roadmap

1. **Query Backlog & Sprint Items**:
   ```powershell
   @{
     query = 'query { node(id: "<PROJECT_ID>") { ... on ProjectV2 { items(first: 100) { nodes { id content { ... on Issue { number title body state labels(first: 5) { nodes { name } } } } fieldValues(first: 10) { nodes { ... on ProjectV2ItemFieldSingleSelectValue { name field { ... on ProjectV2SingleSelectField { name } } } ... on ProjectV2ItemFieldIterationValue { title startDate duration } ... on ProjectV2ItemFieldDateValue { date field { ... on ProjectV2Field { name } } } } } } } } } }'
   } | ConvertTo-Json | gh api graphql --input -
   ```
2. **Sprint Carryover Audit**:
   - Inspect unfinished (`Todo` / `In Progress`) items in `sprint:@current` or earlier sprints.
   - Prompt the user via `ask_question` (`is_multi_select: true`) to decide which carryover items roll forward into the target sprint vs. return to the backlog.
3. **Dependency & Priority Ordering**:
   - Check `### Technical Notes / Dependencies` for `Depends on #<N>` references; schedule blockers in the same or an earlier sprint than dependent items.
   - Ensure every scheduled item passes `check-ready` (`is_clear: true`) and has a `Priority`.
   - Balance sprint capacity by moving lower-priority (`P2`/`P3`) items out of overloaded sprints.
4. **Assign Sprint & Auto-Sync Roadmap Dates**:
   - Run `assign-sprint` for each scheduled ticket (this sets `Sprint` and automatically syncs `Start date` and `Target date` to `startDate` and `startDate + duration - 1` days):
     ```bash
     python .agents/scripts/gh_project.py assign-sprint <issue-number> "<YYYY.MM.A>"
     ```
5. **Automatic Epic Roadmap Rollup**:
   - After updating sub-tickets, recalculate each touched Parent Epic's Roadmap dates ($\min$ child start dates, $\max$ child target dates):
     ```bash
     python .agents/scripts/gh_project.py rollup-epic <epic-number>
     ```

---

## 4. Update Ticket Status

Use `gh_project.py set-status` to transition tickets between `Todo`, `In Progress`, and `Done`:

```bash
python .agents/scripts/gh_project.py set-status <issue-number> "In Progress"
```

### Raw GraphQL Fallback (if `github_project` cache is unavailable)

```powershell
@{
  query = 'mutation { updateProjectV2ItemFieldValue(input: { projectId: "<PROJECT_ID>", itemId: "<ITEM_ID>", fieldId: "<STATUS_FIELD_ID>", value: { singleSelectOptionId: "<OPTION_ID>" } }) { projectV2Item { id } } }'
} | ConvertTo-Json | gh api graphql --input -
```
