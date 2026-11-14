#!/usr/bin/env python3
"""
gh_project.py — Deterministic GitHub Projects (v2) CLI Helper for my-harness.

Caches Project/Field/Option/Iteration IDs in `.agents/harness.config.json`,
evaluates Issue readiness ("Clear?" gate), syncs Sprint dates to Roadmap dates,
updates ticket statuses, and computes Epic Roadmap date rollups.
"""

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

CHECKBOX_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s+(.+?)\s*$", re.MULTILINE)
EPIC_REF_RE = re.compile(r"Part\s+of\s+(#\d+)", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"\b(TBD|TODO)\b", re.IGNORECASE)


def find_repo_root(start: Optional[Path] = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / ".agents").exists() or (candidate / ".git").exists():
            return candidate
    return cur


def load_project_config(repo_root: Path) -> dict:
    cfg_path = repo_root / ".agents" / "harness.config.json"
    if not cfg_path.exists():
        return {}
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
        return data.get("github_project", {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_project_config(repo_root: Path, gh_cfg: dict) -> Path:
    agents_dir = repo_root / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = agents_dir / "harness.config.json"
    data = {}
    if cfg_path.exists():
        try:
            loaded = json.loads(cfg_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            data = {}
    data["github_project"] = gh_cfg
    cfg_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return cfg_path


def calculate_iteration_end_date(start_date: str, duration_days: int) -> str:
    start_dt = datetime.date.fromisoformat(start_date)
    end_dt = start_dt + datetime.timedelta(days=max(duration_days - 1, 0))
    return end_dt.isoformat()


def compute_epic_date_rollup(child_dates: list) -> Optional[dict]:
    starts = [s for s, _ in child_dates if s]
    targets = [t for _, t in child_dates if t]
    if not starts or not targets:
        return None
    return {"start_date": min(starts), "target_date": max(targets)}


def format_issue_body(
    summary: str,
    acceptance_criteria: list,
    epic: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    parts = []
    if epic:
        normalized_epic = epic if str(epic).startswith("#") else f"#{epic}"
        parts.append(f"### Parent Epic\nPart of {normalized_epic}")
    parts.append(f"### Summary\n{summary.strip()}")
    ac_lines = [f"- [ ] {item.strip()}" for item in acceptance_criteria if str(item).strip()]
    ac_block = "\n".join(ac_lines) if ac_lines else "- [ ] "
    parts.append(f"### Acceptance Criteria\n{ac_block}")
    if notes and notes.strip():
        parts.append(f"### Technical Notes / Dependencies\n{notes.strip()}")
    return "\n\n".join(parts) + "\n"


def _extract_section(body: str, heading_pattern: str) -> str:
    pattern = re.compile(rf"(?im)^{heading_pattern}\s*\r?\n(.*?)(?=^###\s|\Z)", re.DOTALL)
    match = pattern.search(body)
    return match.group(1).strip() if match else ""


def check_issue_readiness(issue_data: dict) -> dict:
    body = issue_data.get("body") or ""
    epic_match = EPIC_REF_RE.search(body)
    epic_ref = epic_match.group(1) if epic_match else None

    summary_text = _extract_section(body, r"###\s*Summary")
    ac_text = _extract_section(body, r"###\s*Acceptance Criteria")
    notes_text = _extract_section(body, r"###\s*Technical Notes(?:\s*/\s*Dependencies)?")
    ac_items = [m.group(1).strip() for m in CHECKBOX_RE.finditer(ac_text) if m.group(1).strip()]

    missing = []
    if not summary_text or PLACEHOLDER_RE.search(summary_text):
        missing.append("Missing or placeholder Summary section")
    if not ac_items:
        missing.append("Missing testable Acceptance Criteria checkboxes (- [ ])")
    elif PLACEHOLDER_RE.search(ac_text):
        missing.append("Acceptance Criteria contains TBD/TODO placeholders")

    return {
        "number": issue_data.get("number"),
        "title": issue_data.get("title", ""),
        "is_clear": len(missing) == 0,
        "ac_count": len(ac_items),
        "epic_ref": epic_ref,
        "missing": missing,
        "has_technical_notes": bool(notes_text),
    }


def _extract_field_entry(field_node: dict) -> Optional[dict]:
    name = field_node.get("name")
    field_id = field_node.get("id")
    if not name or not field_id:
        return None
    entry = {"id": field_id, "dataType": field_node.get("dataType", "")}
    options = field_node.get("options")
    if isinstance(options, list):
        entry["options"] = {opt["name"]: opt["id"] for opt in options if "name" in opt and "id" in opt}
    iterations = (field_node.get("configuration") or {}).get("iterations")
    if isinstance(iterations, list):
        parsed_iters = {}
        for it in iterations:
            title = it.get("title")
            start_date = it.get("startDate")
            duration = int(it.get("duration") or 14)
            if title and start_date and it.get("id"):
                parsed_iters[title] = {
                    "id": it["id"],
                    "startDate": start_date,
                    "duration": duration,
                    "endDate": calculate_iteration_end_date(start_date, duration),
                }
        entry["iterations"] = parsed_iters
    return entry


def parse_project_metadata(project_node: dict) -> dict:
    fields = {}
    for node in (project_node.get("fields") or {}).get("nodes") or []:
        name = node.get("name")
        entry = _extract_field_entry(node)
        if name and entry:
            fields[name] = entry
    return {
        "project_id": project_node.get("id", ""),
        "project_number": project_node.get("number"),
        "title": project_node.get("title", ""),
        "fields": fields,
    }


def run_gh_cli(args: list, stdin_text: Optional[str] = None) -> str:
    res = subprocess.run(
        ["gh", *args],
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return res.stdout


def run_gh_graphql(query: str, variables: Optional[dict] = None) -> dict:
    payload = json.dumps({"query": query, "variables": variables or {}})
    out = run_gh_cli(["api", "graphql", "--input", "-"], stdin_text=payload)
    parsed = json.loads(out)
    if parsed.get("errors"):
        raise RuntimeError(json.dumps(parsed["errors"]))
    return parsed.get("data", {})


def _query_project_items(project_id: str) -> list:
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              id
              content { ... on Issue { number title body state } }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldDateValue { date field { ... on ProjectV2Field { name } } }
                  ... on ProjectV2ItemFieldSingleSelectValue { name field { ... on ProjectV2SingleSelectField { name } } }
                  ... on ProjectV2ItemFieldIterationValue { title startDate duration field { ... on ProjectV2IterationField { name } } }
                }
              }
            }
          }
        }
      }
    }
    """
    data = run_gh_graphql(query, {"projectId": project_id})
    return ((data.get("node") or {}).get("items") or {}).get("nodes") or []


def _find_project_item_id(items: list, issue_number: int) -> Optional[str]:
    for item in items:
        content = item.get("content") or {}
        if content.get("number") == issue_number:
            return item.get("id")
    return None


def _update_field_value(project_id: str, item_id: str, field_id: str, value: dict) -> None:
    mutation = """
    mutation($input: UpdateProjectV2ItemFieldValueInput!) {
      updateProjectV2ItemFieldValue(input: $input) { projectV2Item { id } }
    }
    """
    variables = {
        "input": {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "value": value,
        }
    }
    run_gh_graphql(mutation, variables)


def _require_project_config(repo_root: Path) -> dict:
    cfg = load_project_config(repo_root)
    if not cfg.get("project_id") or not cfg.get("fields"):
        raise RuntimeError("Missing cached github_project config. Run `gh_project.py sync` first.")
    return cfg


def cmd_sync(args) -> int:
    repo_root = find_repo_root()
    proj_raw = run_gh_cli(["project", "view", str(args.project_number), "--owner", args.owner, "--format", "json"])
    proj_info = json.loads(proj_raw)
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          id title number
          fields(first: 50) {
            nodes {
              ... on ProjectV2Field { id name dataType }
              ... on ProjectV2SingleSelectField { id name dataType options { id name } }
              ... on ProjectV2IterationField {
                id name dataType
                configuration { iterations { id title startDate duration } }
              }
            }
          }
        }
      }
    }
    """
    data = run_gh_graphql(query, {"projectId": proj_info["id"]})
    metadata = parse_project_metadata(data["node"])
    metadata["owner"] = args.owner
    if args.repo:
        metadata["repo"] = args.repo
    cfg_path = save_project_config(repo_root, metadata)
    print(json.dumps({"synced": True, "config_path": str(cfg_path), "project_id": metadata["project_id"]}))
    return 0


def cmd_check_ready(args) -> int:
    gh_args = ["issue", "view", str(args.issue_number), "--json", "number,title,body,labels,state"]
    if args.repo:
        gh_args.extend(["--repo", args.repo])
    issue_data = json.loads(run_gh_cli(gh_args))
    result = check_issue_readiness(issue_data)
    print(json.dumps(result, indent=2))
    return 0 if result["is_clear"] else 2


def _resolve_project_item(issue_number: int) -> tuple:
    repo_root = find_repo_root()
    cfg = _require_project_config(repo_root)
    items = _query_project_items(cfg["project_id"])
    item_id = _find_project_item_id(items, issue_number)
    if not item_id:
        raise RuntimeError(f"Issue #{issue_number} not found in Project")
    return cfg, item_id


def cmd_set_status(args) -> int:
    cfg, item_id = _resolve_project_item(args.issue_number)
    status_field = cfg["fields"].get("Status", {})
    option_id = (status_field.get("options") or {}).get(args.status_name)
    if not status_field.get("id") or not option_id:
        raise RuntimeError(f"Unknown Status option '{args.status_name}'")
    _update_field_value(cfg["project_id"], item_id, status_field["id"], {"singleSelectOptionId": option_id})
    print(json.dumps({"issue": args.issue_number, "status": args.status_name, "updated": True}))
    return 0


def cmd_assign_sprint(args) -> int:
    cfg, item_id = _resolve_project_item(args.issue_number)
    sprint_field = cfg["fields"].get("Sprint", {})
    iteration = (sprint_field.get("iterations") or {}).get(args.sprint_title)
    if not sprint_field.get("id") or not iteration:
        raise RuntimeError(f"Unknown Sprint iteration '{args.sprint_title}'")
    _update_field_value(cfg["project_id"], item_id, sprint_field["id"], {"iterationId": iteration["id"]})
    _sync_item_dates(cfg, item_id, iteration["startDate"], iteration["endDate"])
    print(json.dumps({"issue": args.issue_number, "sprint": args.sprint_title, "start_date": iteration["startDate"], "target_date": iteration["endDate"]}))
    return 0


def _sync_item_dates(cfg: dict, item_id: str, start_date: str, target_date: str) -> None:
    start_field = cfg["fields"].get("Start date", {})
    target_field = cfg["fields"].get("Target date", {})
    if start_field.get("id"):
        _update_field_value(cfg["project_id"], item_id, start_field["id"], {"date": start_date})
    if target_field.get("id"):
        _update_field_value(cfg["project_id"], item_id, target_field["id"], {"date": target_date})


def _extract_item_dates(item: dict) -> tuple:
    start_date, target_date = None, None
    for fv in (item.get("fieldValues") or {}).get("nodes") or []:
        fname = (fv.get("field") or {}).get("name")
        if fname == "Start date":
            start_date = fv.get("date")
        elif fname == "Target date":
            target_date = fv.get("date")
    return (start_date, target_date)


def cmd_rollup_epic(args) -> int:
    repo_root = find_repo_root()
    cfg = _require_project_config(repo_root)
    items = _query_project_items(cfg["project_id"])
    epic_item_id = _find_project_item_id(items, args.epic_number)
    if not epic_item_id:
        raise RuntimeError(f"Epic #{args.epic_number} not found in Project")
    epic_pattern = re.compile(rf"Part\s+of\s+#{args.epic_number}\b", re.IGNORECASE)
    child_dates = [
        _extract_item_dates(it)
        for it in items
        if epic_pattern.search(((it.get("content") or {}).get("body")) or "")
    ]
    rollup = compute_epic_date_rollup(child_dates)
    if not rollup:
        print(json.dumps({"epic": args.epic_number, "updated": False, "reason": "No child dates found"}))
        return 0
    _sync_item_dates(cfg, epic_item_id, rollup["start_date"], rollup["target_date"])
    print(json.dumps({"epic": args.epic_number, "updated": True, **rollup}))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GitHub Projects (v2) helper for my-harness")
    sub = parser.add_subparsers(dest="command")

    p_sync = sub.add_parser("sync", help="Fetch and cache GitHub Project field & iteration IDs")
    p_sync.add_argument("--owner", required=True, help="Project owner login")
    p_sync.add_argument("--project-number", type=int, required=True, help="GitHub Project number")
    p_sync.add_argument("--repo", default="", help="Optional owner/repo slug")

    p_ready = sub.add_parser("check-ready", help="Check whether an issue passes the Clear? readiness gate")
    p_ready.add_argument("issue_number", type=int, help="GitHub issue number")
    p_ready.add_argument("--repo", default="", help="Optional owner/repo slug")

    p_status = sub.add_parser("set-status", help="Update Status field for a Project issue")
    p_status.add_argument("issue_number", type=int, help="GitHub issue number")
    p_status.add_argument("status_name", help="Target status (e.g. Todo, In Progress, Done)")

    p_sprint = sub.add_parser("assign-sprint", help="Assign Sprint and sync Start/Target Roadmap dates")
    p_sprint.add_argument("issue_number", type=int, help="GitHub issue number")
    p_sprint.add_argument("sprint_title", help="Sprint title (e.g. 2026.11.A)")

    p_rollup = sub.add_parser("rollup-epic", help="Recalculate Epic Start/Target dates from child tickets")
    p_rollup.add_argument("epic_number", type=int, help="Parent Epic issue number")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    handlers = {
        "sync": cmd_sync,
        "check-ready": cmd_check_ready,
        "set-status": cmd_set_status,
        "assign-sprint": cmd_assign_sprint,
        "rollup-epic": cmd_rollup_epic,
    }
    handler = handlers.get(args.command)
    if not handler:
        parser.print_help()
        return 1
    try:
        return handler(args)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
