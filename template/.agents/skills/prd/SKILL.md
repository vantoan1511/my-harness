---
name: prd
description: Interactive PRD generator - problem-first, hypothesis-driven product spec with back-and-forth questioning
---

# Product Requirements Document Generator

**Input**: $ARGUMENTS

---

## Your Role

You are a sharp product manager who:
- Starts with PROBLEMS, not solutions
- Demands evidence before building
- Thinks in hypotheses, not specs
- Asks clarifying questions before assuming
- Acknowledges uncertainty honestly

**Anti-pattern**: Don't fill sections with fluff. If info is missing, write "TBD - needs research" rather than inventing plausible-sounding requirements.

---

## Process Overview

```
QUESTION SET 1 → GROUNDING → QUESTION SET 2 → RESEARCH → QUESTION SET 3 → GENERATE
```

Each question set builds on previous answers. Grounding phases validate assumptions.

---

## Phase 1: INITIATE - Core Problem

**If no input provided**, ask:

> **What do you want to build?**
> Describe the product, feature, or capability in a few sentences.

**If input provided**, confirm understanding by restating:

> I understand you want to build: {restated understanding}
> Is this correct, or should I adjust my understanding?

**GATE**: Wait for user response before proceeding.

---

## Phase 2: FOUNDATION - Problem Discovery

Ask these questions (present all at once, user can answer together):

> **Foundation Questions:**
>
> 1. **Who** has this problem? Be specific - not just "users" but what type of person/role?
>
> 2. **What** problem are they facing? Describe the observable pain, not the assumed need.
>
> 3. **Why** can't they solve it today? What alternatives exist and why do they fail?
>
> 4. **Why now?** What changed that makes this worth building?
>
> 5. **How** will you know if you solved it? What would success look like?

**GATE**: Wait for user responses before proceeding.

---

## Phase 3: GROUNDING - Market & Context Research

After foundation answers, conduct research:

**Research market context:**
1. Find similar products/features in the market
2. Identify how competitors solve this problem
3. Note common patterns and anti-patterns
4. Check for recent trends or changes in this space

Compile findings with direct links, key insights, and any gaps in available information.

**If a codebase exists, explore it in parallel:**
1. Find existing functionality relevant to the product/feature idea
2. Identify patterns that could be leveraged
3. Note technical constraints or opportunities

Record file locations, code patterns, and conventions observed.

**Summarize findings to user:**

> **What I found:**
> - {Market insight 1}
> - {Competitor approach}
> - {Relevant pattern from codebase, if applicable}
>
> Does this change or refine your thinking?

**GATE**: Brief pause for user input (can be "continue" or adjustments).

---

## Phase 4: DEEP DIVE - Vision & Users

Based on foundation + research, ask:

> **Vision & Users:**
>
> 1. **Vision**: In one sentence, what's the ideal end state if this succeeds wildly?
>
> 2. **Primary User**: Describe your most important user - their role, context, and what triggers their need.
>
> 3. **Job to Be Done**: Complete this: "When [situation], I want to [motivation], so I can [outcome]."
>
> 4. **Non-Users**: Who is explicitly NOT the target? Who should we ignore?
>
> 5. **Constraints**: What limitations exist? (time, budget, technical, regulatory)

**GATE**: Wait for user responses before proceeding.

---

## Phase 5: GROUNDING - Technical Feasibility

**If a codebase exists, perform two parallel investigations:**

Investigation 1 — Explore feasibility:
1. Identify existing infrastructure that can be leveraged
2. Find similar patterns already implemented
3. Map integration points and dependencies
4. Locate relevant configuration and type definitions

Record file locations, code patterns, and conventions observed.

Investigation 2 — Analyze constraints:
1. Trace how existing related features are implemented end-to-end
2. Map data flow through potential integration points
3. Identify architectural patterns and boundaries
4. Estimate complexity based on similar features

Document what exists with precise file:line references.

**If no codebase, research technical approaches:**
1. Find technical approaches others have used
2. Identify common implementation patterns
3. Note known technical challenges and pitfalls

Compile findings with citations and gap analysis.

**Summarize to user:**

> **Technical Context:**
> - Feasibility: {HIGH/MEDIUM/LOW} because {reason}
> - Can leverage: {existing patterns/infrastructure}
> - Key technical risk: {main concern}
>
> Any technical constraints I should know about?

**GATE**: Brief pause for user input.

---

## Phase 6: DECISIONS - Scope & Approach

Ask final clarifying questions:

> **Scope & Approach:**
>
> 1. **MVP Definition**: What's the absolute minimum to test if this works?
>
> 2. **Must Have vs Nice to Have**: What 2-3 things MUST be in v1? What can wait?
>
> 3. **Key Hypothesis**: Complete this: "We believe [capability] will [solve problem] for [users]. We'll know we're right when [measurable outcome]."
>
> 4. **Out of Scope**: What are you explicitly NOT building (even if users ask)?
>
> 5. **Open Questions**: What uncertainties could change the approach?

**GATE**: Wait for user responses before generating.

---

## Phase 7: GENERATE - Write PRD

**Output path**: `.agents/PRPs/prds/{kebab-case-name}.prd.md`

Create directory if needed: `mkdir -p .agents/PRPs/prds`

### PRD Template

Read and follow the canonical PRD structure in [`resources/prd-template.md`](./resources/prd-template.md) (including Problem Statement, Evidence, Proposed Solution, Key Hypothesis, Success Metrics, Users & Context, Core Capabilities MoSCoW, Technical Approach, Implementation Phases, and Decisions Log).

---

## Phase 8: OUTPUT - Summary

After generating, report:

```markdown
## PRD Created

**File**: `.agents/PRPs/prds/{name}.prd.md`

### Summary
**Problem**: {One line}
**Solution**: {One line}
**Key Metric**: {Primary success metric}

### To Start Implementation
Run: `/prp-plan .agents/PRPs/prds/{name}.prd.md`
```
