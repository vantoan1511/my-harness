---
name: github-project-setup
description: Set up a GitHub Project (v2) with 2-week sprints, Roadmap dates, Priority field, Board/Table/Roadmap views, Epic issues, issue templates, and small business-oriented sub-tickets with Acceptance Criteria using `gh` CLI and GraphQL.
---

# GitHub Project Setup & Sprint Organization

Use this skill when setting up a GitHub Project for a repository, creating an Epic and breaking it down into small, business-oriented sub-tickets with Acceptance Criteria, and organizing them into 2-week sprints, a Board, and a Roadmap.

## 1. Verify `gh` Auth & Scopes

Check that `gh` is authenticated and has `project` + `read:project` scopes:

```powershell
gh project list --owner <owner>
```

If it fails with missing `read:project` or `project` scope, ask the user to run:

```bash
gh auth refresh -s project,read:project
```

## 2. Create & Link Project

```powershell
$proj = gh project create --owner <owner> --title "<Project Title>" --format json | ConvertFrom-Json
gh project link $proj.number --owner <owner> --repo <owner>/<repo>
```

## 3. Add Issue Template (`.github/ISSUE_TEMPLATE/task.yml`)

Ensure the repository has a structured Task/Feature issue form so all new backlog items follow a consistent format (`Parent Epic`, `Summary`, `Acceptance Criteria`, `Technical Notes / Dependencies`):

```yaml
name: Task / Feature
description: A small, business-oriented unit of work for a sprint
title: ""
labels: []
body:
  - type: input
    id: epic
    attributes:
      label: Parent Epic
      description: Link the parent epic (if applicable)
      placeholder: "Part of #<epic-number>"
  - type: textarea
    id: summary
    attributes:
      label: Summary
      description: What is this ticket delivering and why does it matter?
    validations:
      required: true
  - type: textarea
    id: acceptance_criteria
    attributes:
      label: Acceptance Criteria
      description: Clear, testable conditions for "Done"
      value: |
        - [ ] 
        - [ ] 
    validations:
      required: true
  - type: textarea
    id: notes
    attributes:
      label: Technical Notes / Dependencies
      description: Optional implementation hints, links, or blockers
```

## 4. Create Epic & Business-Oriented Sub-Tickets

1. Ensure the `epic` label exists:
   ```powershell
   gh label create epic --description "High-level epic tracking a major initiative" --color "5319E7"
   ```
2. Create the **Epic** issue (`--label epic`) with overview, motivation, key workstreams, and success criteria.
3. Break the Epic into **small, easy-to-achieve sub-tickets**:
   - Use **business-oriented titles** (no technical prefixes like `feat(gpui):` or `chore:`).
   - Follow the issue template structure in `--body`:
     - `### Parent Epic` (`Part of #<epic-number>`)
     - `### Summary`
     - `### Acceptance Criteria` (2–3 clear, testable `- [ ]` checkboxes)
     - `### Technical Notes / Dependencies` (optional file hints or `Depends on #<number>`)
   - Add every created issue to the project:
     ```powershell
     gh project item-add $proj.number --owner <owner> --url <issue-url>
     ```

## 5. Configure Project Fields

1. **Date fields** (for Roadmap):
   ```powershell
   gh project field-create $proj.number --owner <owner> --name "Start date" --data-type DATE
   gh project field-create $proj.number --owner <owner> --name "Target date" --data-type DATE
   ```
2. **Priority field**:
   ```powershell
   gh project field-create $proj.number --owner <owner> --name "Priority" --data-type SINGLE_SELECT --single-select-options "P0 - Critical,P1 - High,P2 - Medium,P3 - Low"
   ```
3. **Sprint (Iteration) field** (2-week sprints formatted `YYYY.MM.A`, `YYYY.MM.B`, etc.):
   Use `gh api graphql --input -` with `ConvertTo-Json` (avoids PowerShell quoting issues):
   ```powershell
   @{
     query = 'mutation { createProjectV2Field(input: { projectId: "<PROJECT_ID>", dataType: ITERATION, name: "Sprint", iterationConfiguration: { duration: 14, startDate: "YYYY-MM-DD", iterations: [ { title: "YYYY.MM.A", startDate: "YYYY-MM-DD", duration: 14 }, { title: "YYYY.MM.B", startDate: "YYYY-MM-DD", duration: 14 } ] } }) { projectV2Field { ... on ProjectV2IterationField { id name configuration { iterations { id title startDate duration } } } } } }'
   } | ConvertTo-Json | gh api graphql --input -
   ```
   To shift sprint dates later, use `updateProjectV2Field` with `fieldId` and the updated `iterationConfiguration` (including each iteration's `id`).

## 6. Assign Items to Sprints, Board, and Roadmap

- Set `Status` = `Todo` and `Priority` on all new items.
- Assign each sub-ticket to its 2-week `Sprint` (`YYYY.MM.A`, `YYYY.MM.B`, ...) and sync its `Start date` and `Target date` via `gh_project.py assign-sprint <issue#> <sprint_title>`.
- Run `gh_project.py rollup-epic <epic#>` so the **Epic** `Start date` and `Target date` span the full initiative on the **Roadmap**.

## 7. Configure Project Views

1. Rename the default `View 1` to **Roadmap** (`ROADMAP_LAYOUT`) via `updateProjectV2View`.
   - Note: `updateProjectV2View` accepts `viewId`, `name`, `layout`, and `filter` — it does **not** accept `projectId` or `visibleFields` (toggle visible fields like **Priority** in the GitHub web UI under **Fields**).
2. Create views with `createProjectV2View` (note: `filter` cannot be passed on creation, so set it immediately afterward with `updateProjectV2View`):
   - **Current Sprint** (`BOARD_LAYOUT`) → filter: `sprint:@current`
   - **Sprint Planning** (`TABLE_LAYOUT`) → group by `Sprint` in UI
   - **Epics** (`TABLE_LAYOUT`) → filter: `label:epic`
   - **Backlog** (`TABLE_LAYOUT`) → filter: `no:sprint -label:epic`

## 8. Cache Project Metadata in Harness Config (`gh_project.py sync`)

Cache the Project ID, Status/Priority option IDs, and Sprint iteration IDs + dates inside `.agents/harness.config.json` so `/specify`, `/prp-plan`, `/implement`, `/pr`, and `github-backlog-management` can transition tickets without raw GraphQL queries:

```powershell
python .agents/scripts/gh_project.py sync --owner <owner> --project-number $proj.number --repo <owner>/<repo>
```

*(If running from global plugin scope without local scripts, invoke `~/.gemini/config/plugins/my-harness/scripts/gh_project.py`.)*
