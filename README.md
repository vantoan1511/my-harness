# my-harness

> **Reusable Agent Engineering Harness for Autonomous AI Pair-Programmers**
>
> Shift-Left Quality • Contract-First Design • Test-Driven Development (TDD) • Pluggable Architecture

`my-harness` is an extracted, refined, and reusable framework for orchestrating AI coding agents across any software engineering project. It packages battle-tested skills, rules, lifecycle hooks, and automated verification tools so you can empower AI agents in new repositories without reinventing the setup from scratch.

---

## Key Highlights

- ⚡ **Zero-Friction Scaffolding**: Initialize complete `.agents/` workflows in any repository with a single command.
- 🛡️ **Shift-Left Quality Engine**: Fast, zero-dependency static pre-flight scanner (`< 0.5s`) that enforces git branch safety, banned imports, design tokens, and error handling rules before committing.
- 📐 **Contract-First Specification (`/specify`)**: Autonomous reconnaissance before questioning; interactive ambiguity resolution using `ask_question`; outputs actionable specifications and plans.
- 🧪 **Test-Driven Development (`/tdd-workflow`)**: Red-Green-Refactor testing loops across TypeScript/Node, Python, Rust, and Go.
- 🔁 **Continuous Execution Loop (`/implement`)**: Atomic task execution with per-file micro-validation, implementation reports, and automatic plan archiving.
- 🧠 **Agent Memory & Knowledge Curation**: Captures user instructions/corrections in markdown logs (`.agents/logs/`) and self-improves repository recipes.
- 📦 **Pluggable Domain Packs**: Core SDLC workflows are universal; domain-specific rules (like Vue 3, PrimeVue, Rust, Kubernetes, Neutralino) are organized into modular, installable packs.

---

## Architecture Overview

```
my-harness/
├── harness.py                    # Central CLI tool (init, add-pack, doctor, verify, sync)
├── install.ps1 / install.sh      # One-line installer scripts
├── pyproject.toml / setup.py     # Python package setup
│
├── template/                     # Universal starter template for projects
│   ├── .agents/
│   │   ├── hooks.json            # PreInvocation lifecycle hooks
│   │   ├── harness.config.json   # Configurable rules & validation commands
│   │   ├── rules/                # Constitution rules (shift-left-quality, review-rules)
│   │   ├── scripts/              # Static scanners, hooks & loggers
│   │   ├── skills/               # Universal SDLC agent skills
│   │   ├── references/           # Knowledge base catalog, ADRs & recipes
│   │   ├── PRPs/                 # Plans, PRDs, and implementation reports
│   │   ├── reviews/              # Code review artifacts
│   │   ├── handoffs/             # Session handoff summaries
│   │   └── logs/                 # Interaction memory logs
│   └── AGENTS.md.template        # Starter agent rules file
│
└── packs/                        # Optional domain & technology packs
    ├── desktop-vue-rust/         # Generalized desktop skeleton (Rust + Vue 3 + PrimeVue Nora)
    ├── orbit-desktop/            # Full Orbit Kubernetes desktop pack
    └── vue-primevue/             # Reusable Vue 3 + PrimeVue 4 styling & component pack
```

---

## Quick Start

### 1. Run the Installer (Choose Project vs Global Scope)

Run the installer interactively or specify the scope directly:

```bash
# PowerShell (Windows)
# Interactive menu: prompts to choose Project or Global scope
powershell -ExecutionPolicy Bypass -File d:/Projects/my-harness/install.ps1

# Or specify project scope directly:
powershell -ExecutionPolicy Bypass -File d:/Projects/my-harness/install.ps1 -Scope project -Target C:/path/to/my-project

# Or install globally (~/.agents + registers 'harness' CLI via pip):
powershell -ExecutionPolicy Bypass -File d:/Projects/my-harness/install.ps1 -Scope global

# Bash (Linux/macOS)
# Interactive menu: prompts to choose Project or Global scope
bash d:/Projects/my-harness/install.sh

# Or specify project scope directly:
bash d:/Projects/my-harness/install.sh --scope project --target /path/to/my-project

# Or install globally (~/.agents + registers 'harness' CLI via pip):
bash d:/Projects/my-harness/install.sh --scope global
```

### 2. Using Python Directly

```bash
# Initialize in current project:
python d:/Projects/my-harness/harness.py init

# Initialize in a specific project:
python d:/Projects/my-harness/harness.py init /path/to/my-project

# Initialize globally (~/.agents + register CLI):
python d:/Projects/my-harness/harness.py init --scope global
```

`harness init` automatically:
1. Detects project languages and runners (Node, Rust, Python, Go).
2. Scaffolds the `.agents/` directory structure (in project root or `~/.agents` if global).
3. Generates a tailored `harness.config.json` with appropriate test, lint, and type-check commands.
4. Creates a starter `AGENTS.md` rules file (when in project scope).
5. Registers the `harness` CLI globally in Python environment (when in global scope).

---

## CLI Commands

| Command | Description |
|---|---|
| `harness init [path] [--scope project\|global] [--pack <name>]` | Scaffolds `.agents/` in target project or globally (`~/.agents` + CLI) |
| `harness add-pack <pack> [path]` | Installs an extension pack into target project |
| `harness list-packs` | Lists all available extension packs |
| `harness doctor [path]` | Health check: verifies directory structure, JSON, scripts, and git |
| `harness verify [--changed\|--all] [path]` | Runs shift-left pre-flight verification scanner |
| `harness sync [path]` | Updates core harness scripts and universal skills in target project |

---

## Universal SDLC Skills

Every project initialized with `my-harness` receives the complete suite of autonomous software engineering skills:

### 1. Specification & Planning
- `/specify <intent>`: Discovers codebase context, asks interactive clarification questions via `ask_question`, defines interface contracts, writes a PRD spec (`.agents/PRPs/prds/`), generates an implementation plan (`.agents/PRPs/plans/`), and strictly ends with a clean plan handoff without preemptively implementing.
- `/prd <topic>`: Interactive, hypothesis-driven Product Requirements Document generator.
- `/prp-plan <feature>`: Deep 8-category codebase reconnaissance, UX delta mapping, step-by-step TDD task generation, and clean handoff to `/implement`.

### 2. Execution & Quality
- `/implement <plan.md>`: Seamless execution loop: executes plan tasks sequentially with per-task RED/GREEN/VALIDATE micro-validation, creates implementation report (`reports/{name}-report.md`), archives plan (`plans/completed/`), and seamlessly commits changes and creates a GitHub pull request via `gh pr create`.
- `/tdd-workflow`: Enforces test-first development. Provides testing patterns for TypeScript/Node, Python, Rust, and Go.
- `/simplifier`: Cleans up and simplifies recently modified code without altering functionality.
- `/code-review [PR#]`: Dual-mode code reviewer (local uncommitted diff or GitHub PR) checking security, architecture, extensibility, and quality.

### 3. Git & Delivery
- `/commit [intent]`: Intelligent conventional commit with natural-language file staging.
- `/pr [--draft]`: Validates preconditions, analyzes commits and diffs, matches PR templates, pushes branch, and opens GitHub PR via `gh pr create`.
- `/pr-changelog [PR#]`: Generates a high-signal, categorized changelog from Git history, diffs, and PR metadata; automatically updates `CHANGELOG.md`.
- `/release`: Semantic versioning release workflow, lockfile update, and release branch creation.

### 4. Telemetry & Continuous Improvement
- `/session-handoff`: Records session goals, outcomes, next steps, and open issues into markdown handoffs.
- `/agent-log-analyzer`: Scans agent interaction logs (`.agents/logs/*.md`) to extract user corrections and propose automated scripts or rules.

### 5. Natural Writing & Social Conversation (Built-in by Default)
Installed by default in all initialized projects — no optional pack required:
- `/natural-human-writing` (or `/fb-comment-style`): Produces believable, naturally human-written text across chats, comments, debates, emails, explanations, and documentation. Adapts tone, contractions, rhythm, and imperfections to the context instead of sounding robotic or AI-generated.
- `/social-conversation`: Natural conversational behavior for casual chat, banter, teasing, flirting, dating apps, and everyday social messaging. Calibrates energy, avoids neediness, and matches the user's conversational register.
- `rules/natural-human-writing.md`: Built-in rule ensuring agents preserve natural human voice and conversational calibration across prompts.

---

## Configuration (`harness.config.json`)

Each target project configures its specific rules and commands in `.agents/harness.config.json`:

```json
{
  "project_name": "my-app",
  "preset": "universal",
  "git": {
    "protected_branches": ["main", "master"],
    "enforce_branch_safety": true
  },
  "guardrails": {
    "reminders": [
      "1. Contract-First: Define interfaces & schemas before writing logic.",
      "2. TDD: Write failing tests before writing production code.",
      "3. Micro-Validation: Run `python .agents/scripts/verify_shift_left.py --changed` after every file edit.",
      "4. Branch Safety: Never commit directly to main/master."
    ]
  },
  "rules": {
    "banned_imports": [
      {
        "id": "no-low-level-in-ui",
        "description": "Direct low-level runtime import in presentation layer",
        "pattern": "['\"]@my-org/low-level-runtime['\"]",
        "path_match": ["src/components/", "src/views/"],
        "suggestion": "Route interactions through domain services instead."
      }
    ],
    "banned_patterns": [
      {
        "id": "no-hardcoded-hex-colors",
        "description": "Hardcoded hex color in stylesheet",
        "pattern": "#[0-9a-fA-F]{3,8}\\b",
        "file_extensions": [".css", ".scss", ".vue"],
        "css_blocks_only": true,
        "path_exclude": ["src/assets/tokens.css"],
        "suggestion": "Use design tokens (CSS variables) instead."
      }
    ]
  },
  "commands": {
    "type_check": "npm run type-check",
    "lint": "npm run lint",
    "test": "npm test",
    "build": "npm run build"
  }
}
```

---

## Extension Packs

Extension packs allow adding technology-specific rules and skills without polluting core universal workflows.

### Available Packs:

1. **`desktop-vue-rust` (Recommended for Desktop Apps)**
   - Complete project skeleton for lightweight desktop applications (Rust backend + Neutralino/desktop runtime + Vue 3 + PrimeVue 4 Nora + Tailwind CSS v4).
   - Includes:
     - Rules: `desktop-configuration-system.md`, `desktop-design-system.md`, `desktop-frontend-engineering.md`, `primevue-nora-standards.md`
     - Skills: `desktop-ui-implementation`, `desktop-ui-review`, `primevue-customization`, `data-view-page`
     - ADRs: Application lifecycle (sync mount before IPC), backend configuration system, storage tiers
     - Recipes: Canonical data view (DataTable + drawer), PrimeVue controls, Node 24 native tests, Rust `cargo test`
     - Gotchas: Desktop runtime, PrimeVue quirks, Tailwind v4
     - Guardrails: Pre-configured static verification scanner rules
   - Install with:
     ```bash
     harness add-pack desktop-vue-rust
     ```

2. **`orbit-desktop`**
   - Specialized Orbit Kubernetes desktop client bundle (Kubernetes resource pages, Kubernetes status colors, winget fork sync).
   - Install with:
     ```bash
     harness add-pack orbit-desktop
     ```

3. **`vue-primevue`**
   - Comprehensive UI patterns for Vue 3 + PrimeVue 4 + Tailwind CSS applications.
   - Includes:
     - Skill: `ui` (DataTables, Forms, Animations, Layouts, Theming, Setup)
     - Rules: `vue-primevue-standards.md`
   - Install with:
     ```bash
     harness add-pack vue-primevue
     ```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
