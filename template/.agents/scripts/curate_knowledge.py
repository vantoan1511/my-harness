#!/usr/bin/env python3
"""
curate_knowledge.py — Self-Improving Knowledge Curation Tool

Scans agent logs (.agents/logs/*.md) and PRP implementation reports (.agents/PRPs/reports/*-report.md)
to extract user corrections, recurring gotchas, and implementation deviations,
verifying and updating the curated knowledge base in .agents/references/.
"""

import sys
import os
import re
import argparse
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def get_repo_root() -> Path:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(res.stdout.strip())
    except Exception:
        return Path(__file__).resolve().parent.parent.parent

def extract_user_corrections(base_dir: Path) -> list[dict]:
    logs_dir = base_dir / "logs"
    if not logs_dir.exists():
        return []

    corrections = []
    for log_file in sorted(logs_dir.glob("*.md")):
        try:
            content = log_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for m in re.finditer(r"## Time:\s*([^\n]+)\n\*\*User Request:\*\*\s*([^\n]+)", content):
            time_str = m.group(1).strip()
            req_str = m.group(2).strip()

            keywords = ["remember", "wrong", "fix that", "instead of", "don't do", "rule", "should have", "deviation"]
            if any(k in req_str.lower() for k in keywords):
                corrections.append({
                    "file": log_file.name,
                    "time": time_str,
                    "text": req_str
                })

    return corrections

def extract_report_issues(base_dir: Path) -> list[dict]:
    reports_dir = base_dir / "PRPs" / "reports"
    if not reports_dir.exists():
        return []

    issues = []
    for report_file in sorted(reports_dir.glob("*-report.md")):
        try:
            content = report_file.read_text(encoding="utf-8")
        except Exception:
            continue

        m_dev = re.search(r"## Deviations from Plan\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
        if m_dev:
            dev_text = m_dev.group(1).strip()
            if dev_text and dev_text.lower() != "none":
                issues.append({
                    "file": report_file.name,
                    "section": "Deviations",
                    "text": dev_text
                })

        m_issues = re.search(r"## Issues Encountered\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
        if m_issues:
            iss_text = m_issues.group(1).strip()
            if iss_text and iss_text.lower() != "none":
                issues.append({
                    "file": report_file.name,
                    "section": "Issues",
                    "text": iss_text
                })

    return issues

def extract_self_review_findings(base_dir: Path) -> list[dict]:
    reports_dir = base_dir / "PRPs" / "reports"
    if not reports_dir.exists():
        return []

    findings = []
    for report_file in sorted(reports_dir.glob("*-report.md")):
        try:
            content = report_file.read_text(encoding="utf-8")
        except Exception:
            continue

        m_log = re.search(r"## Self-Review & Adaptation Log\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
        if not m_log:
            continue

        for line in m_log.group(1).splitlines():
            line_str = line.strip()
            if not line_str.startswith("|") or "---" in line_str or "Severity" in line_str:
                continue
            cols = [c.strip() for c in line_str.strip("|").split("|")]
            if len(cols) < 5:
                continue
            sev = cols[1].upper()
            if sev in ("[HIGH/MEDIUM/LOW]", "NONE", "") or sev not in ("CRITICAL", "HIGH", "MEDIUM"):
                continue

            findings.append({
                "report": report_file.name,
                "severity": sev,
                "file_target": cols[2],
                "issue": cols[3],
                "adaptation": cols[4]
            })
    return findings

def _ensure_readme_link(base_dir: Path):
    readme_path = base_dir / "references" / "README.md"
    if not readme_path.exists():
        return
    try:
        content = readme_path.read_text(encoding="utf-8")
        link_str = "[auto-curated-gotchas.md](file://gotchas/auto-curated-gotchas.md)"
        if "auto-curated-gotchas.md" not in content:
            updated = content.replace(
                "## Catalog Index",
                f"## Catalog Index\n\n- {link_str} — Auto-curated gotchas from self-reviews & reports."
            )
            readme_path.write_text(updated, encoding="utf-8")
    except Exception:
        pass

def persist_curated_gotchas(base_dir: Path, findings: list[dict], issues: list[dict]) -> Path | None:
    gotchas_dir = base_dir / "references" / "gotchas"
    gotchas_dir.mkdir(parents=True, exist_ok=True)
    out_file = gotchas_dir / "auto-curated-gotchas.md"

    existing_content = out_file.read_text(encoding="utf-8") if out_file.exists() else ""
    header = (
        "# Auto-Curated Gotchas & Operational Traps\n\n"
        "> Synthesized automatically by `curate_knowledge.py` from Phase 4.5 Self-Review logs and PRP reports.\n"
    )
    if not existing_content:
        existing_content = header

    new_entries = []
    for f in findings:
        title = f"### [{f['severity']}] {f['issue']} (Source: {f['report']})"
        if title in existing_content:
            continue
        body = f"{title}\n- **Target**: {f['file_target']}\n- **Adaptation / Fix**: {f['adaptation']}\n"
        new_entries.append(body)

    for iss in issues:
        title = f"### [DEVIATION] {iss['section']} in {iss['file']}"
        if title in existing_content:
            continue
        body = f"{title}\n- **Insight**: {iss['text']}\n"
        new_entries.append(body)

    if new_entries:
        existing_content = existing_content.rstrip() + "\n\n" + "\n".join(new_entries) + "\n"
        out_file.write_text(existing_content, encoding="utf-8")

    _ensure_readme_link(base_dir)
    return out_file

def verify_reference_links(base_dir: Path) -> list[str]:
    repo_root = base_dir.parent
    ref_dir = base_dir / "references"
    if not ref_dir.exists():
        return []

    broken_links = []
    for ref_file in ref_dir.rglob("*.md"):
        try:
            content = ref_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for m in re.finditer(r"\[.*?\]\((file:///[^)]+)\)", content):
            raw_uri = m.group(1)
            path_part = raw_uri.replace("file:///", "")
            target_path = Path(path_part)
            if not target_path.exists():
                broken_links.append(f"{ref_file.name}: broken link -> {raw_uri}")

    return broken_links

def main():
    parser = argparse.ArgumentParser(description="Self-Improving Knowledge Curation Tool")
    parser.add_argument("--persist", action="store_true", help="Persist findings and deviations into gotchas")
    args = parser.parse_args()

    repo_root = get_repo_root()
    base_dir = repo_root / ".agents"
    print("==> Knowledge Base Curation Report")
    print(f"Base Directory: {base_dir}\n")

    # 1. Verify existing reference links
    broken = verify_reference_links(base_dir)
    if broken:
        print("[WARN] Broken reference links detected:")
        for b in broken:
            print(f"  - {b}")
    else:
        print("[PASS] All reference links verified against codebase.")

    # 2. Extract corrections
    corrections = extract_user_corrections(base_dir)
    print(f"\nExtracted {len(corrections)} user correction(s) from agent logs:")
    for c in corrections[-5:]:
        print(f"  [{c['file']} {c['time']}] {c['text']}")

    # 3. Extract report insights
    report_issues = extract_report_issues(base_dir)
    print(f"\nExtracted {len(report_issues)} deviation/issue insights from PRP reports:")
    for ri in report_issues[-5:]:
        print(f"  [{ri['file']} - {ri['section']}] {ri['text'][:120]}...")

    # 4. Extract self-review findings
    self_review_findings = extract_self_review_findings(base_dir)
    print(f"\nExtracted {len(self_review_findings)} Phase 4.5 self-review finding(s):")
    for f in self_review_findings[-5:]:
        print(f"  [{f['severity']}] {f['file_target']} - {f['issue']}")

    if args.persist:
        out_file = persist_curated_gotchas(base_dir, self_review_findings, report_issues)
        if out_file:
            print(f"\n[PASS] Persisted curated gotchas to: {out_file}")

    print("\n==> Knowledge Base Status: Operational & Curated.")

if __name__ == "__main__":
    main()
