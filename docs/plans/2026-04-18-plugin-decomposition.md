# Plugin Decomposition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split `karak-claude-plugin` into four domain-focused sub-plugins (karak-design, karak-architecture, karak-engineering, karak-product) within a monorepo, while the root remains a meta-package for backward compatibility.

**Architecture:** Each sub-plugin lives in a top-level directory (e.g. `karak-design/`) containing its own `.claude-plugin/plugin.json`, `skills/`, and `agents/`. Skills and agents are copied (not symlinked) from the canonical root `skills/` and `agents/` directories. The root `marketplace.json` lists all five plugins.

**Tech Stack:** Claude Plugin JSON format, bash (sync check script), `claude plugin validate`

---

## File Map

| Action | Path | Purpose |
|--------|------|---------|
| Create | `karak-design/.claude-plugin/plugin.json` | Sub-plugin manifest for design tools |
| Create | `karak-design/skills/<8 dirs>` | Copies of canonical design skills |
| Create | `karak-design/agents/ui-designer.md` | Copy of canonical agent |
| Create | `karak-architecture/.claude-plugin/plugin.json` | Sub-plugin manifest for architecture tools |
| Create | `karak-architecture/skills/write-c4-diagram/` | Copy of canonical skill |
| Create | `karak-architecture/agents/system-designer.md` | Copy |
| Create | `karak-architecture/agents/gcp-infrastructure-engineer.md` | Copy |
| Create | `karak-engineering/.claude-plugin/plugin.json` | Sub-plugin manifest for engineering tools |
| Create | `karak-engineering/skills/codex-review/` | Copy of canonical skill |
| Create | `karak-engineering/agents/code-refactorer.md` | Copy |
| Create | `karak-engineering/agents/quality-assurance-manager.md` | Copy |
| Create | `karak-product/.claude-plugin/plugin.json` | Sub-plugin manifest for product tools |
| Create | `karak-product/agents/requirements-analyst.md` | Copy |
| Create | `karak-product/agents/agile-project-manager.md` | Copy |
| Modify | `.claude-plugin/marketplace.json` | Add 4 new plugin entries, bump meta to 1.7.0 |
| Create | `scripts/check-sync.sh` | CI script: fail if sub-plugin copies drift from root |

---

### Task 1: Create karak-design sub-plugin

**Files:**
- Create: `karak-design/.claude-plugin/plugin.json`
- Create: `karak-design/skills/` (8 skill directories, copied)
- Create: `karak-design/agents/ui-designer.md` (copied)

- [ ] **Step 1: Create directory structure and copy assets**

```bash
mkdir -p karak-design/.claude-plugin karak-design/skills karak-design/agents

# Copy skills
for skill in google-design-docs apple-design icon-design frontend-aesthetics \
             ux-psychologist material-design hifi-design-quality mobile-auth-screen-design; do
  cp -r "skills/$skill" "karak-design/skills/$skill"
done

# Copy agent
cp agents/ui-designer.md karak-design/agents/ui-designer.md
```

- [ ] **Step 2: Write `karak-design/.claude-plugin/plugin.json`**

```json
{
  "name": "karak-design",
  "description": "UI/UX and visual design skills: Apple HIG, Material Design 3, Google design docs, icon design, frontend aesthetics, UX psychology, Hi-Fi design quality, mobile auth screen design",
  "author": {
    "name": "karak"
  },
  "homepage": "https://github.com/karak-developer/karak-claude-plugin",
  "repository": "https://github.com/karak-developer/karak-claude-plugin",
  "license": "MIT",
  "keywords": [
    "design",
    "apple-hig",
    "material-design",
    "icon-design",
    "frontend",
    "ux-psychology",
    "hifi-design",
    "accessibility",
    "android"
  ],
  "skills": [
    "./skills/google-design-docs",
    "./skills/apple-design",
    "./skills/icon-design",
    "./skills/frontend-aesthetics",
    "./skills/ux-psychologist",
    "./skills/material-design",
    "./skills/hifi-design-quality",
    "./skills/mobile-auth-screen-design"
  ],
  "agents": [
    "./agents/ui-designer.md"
  ]
}
```

- [ ] **Step 3: Validate**

```bash
claude plugin validate ./karak-design
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add karak-design/
git commit -m "feat: add karak-design sub-plugin"
```

---

### Task 2: Create karak-architecture sub-plugin

**Files:**
- Create: `karak-architecture/.claude-plugin/plugin.json`
- Create: `karak-architecture/skills/write-c4-diagram/` (copied)
- Create: `karak-architecture/agents/system-designer.md` (copied)
- Create: `karak-architecture/agents/gcp-infrastructure-engineer.md` (copied)

- [ ] **Step 1: Create directory structure and copy assets**

```bash
mkdir -p karak-architecture/.claude-plugin karak-architecture/skills karak-architecture/agents

cp -r skills/write-c4-diagram karak-architecture/skills/write-c4-diagram
cp agents/system-designer.md karak-architecture/agents/system-designer.md
cp agents/gcp-infrastructure-engineer.md karak-architecture/agents/gcp-infrastructure-engineer.md
```

- [ ] **Step 2: Write `karak-architecture/.claude-plugin/plugin.json`**

```json
{
  "name": "karak-architecture",
  "description": "System architecture skills: C4 model diagrams, system design, GCP infrastructure",
  "author": {
    "name": "karak"
  },
  "homepage": "https://github.com/karak-developer/karak-claude-plugin",
  "repository": "https://github.com/karak-developer/karak-claude-plugin",
  "license": "MIT",
  "keywords": [
    "architecture",
    "c4-model",
    "cloud-architecture",
    "gcp"
  ],
  "skills": [
    "./skills/write-c4-diagram"
  ],
  "agents": [
    "./agents/system-designer.md",
    "./agents/gcp-infrastructure-engineer.md"
  ]
}
```

- [ ] **Step 3: Validate**

```bash
claude plugin validate ./karak-architecture
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add karak-architecture/
git commit -m "feat: add karak-architecture sub-plugin"
```

---

### Task 3: Create karak-engineering sub-plugin

**Files:**
- Create: `karak-engineering/.claude-plugin/plugin.json`
- Create: `karak-engineering/skills/codex-review/` (copied)
- Create: `karak-engineering/agents/code-refactorer.md` (copied)
- Create: `karak-engineering/agents/quality-assurance-manager.md` (copied)

- [ ] **Step 1: Create directory structure and copy assets**

```bash
mkdir -p karak-engineering/.claude-plugin karak-engineering/skills karak-engineering/agents

cp -r skills/codex-review karak-engineering/skills/codex-review
cp agents/code-refactorer.md karak-engineering/agents/code-refactorer.md
cp agents/quality-assurance-manager.md karak-engineering/agents/quality-assurance-manager.md
```

- [ ] **Step 2: Write `karak-engineering/.claude-plugin/plugin.json`**

```json
{
  "name": "karak-engineering",
  "description": "Code quality and review skills: Codex-based code review with session resume, code refactoring, QA management",
  "author": {
    "name": "karak"
  },
  "homepage": "https://github.com/karak-developer/karak-claude-plugin",
  "repository": "https://github.com/karak-developer/karak-claude-plugin",
  "license": "MIT",
  "keywords": [
    "code-review",
    "code-quality"
  ],
  "skills": [
    "./skills/codex-review"
  ],
  "agents": [
    "./agents/code-refactorer.md",
    "./agents/quality-assurance-manager.md"
  ]
}
```

- [ ] **Step 3: Validate**

```bash
claude plugin validate ./karak-engineering
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add karak-engineering/
git commit -m "feat: add karak-engineering sub-plugin"
```

---

### Task 4: Create karak-product sub-plugin

**Files:**
- Create: `karak-product/.claude-plugin/plugin.json`
- Create: `karak-product/agents/requirements-analyst.md` (copied)
- Create: `karak-product/agents/agile-project-manager.md` (copied)

- [ ] **Step 1: Create directory structure and copy assets**

```bash
mkdir -p karak-product/.claude-plugin karak-product/agents

cp agents/requirements-analyst.md karak-product/agents/requirements-analyst.md
cp agents/agile-project-manager.md karak-product/agents/agile-project-manager.md
```

- [ ] **Step 2: Write `karak-product/.claude-plugin/plugin.json`**

```json
{
  "name": "karak-product",
  "description": "Product management agents: requirements analysis, agile project management",
  "author": {
    "name": "karak"
  },
  "homepage": "https://github.com/karak-developer/karak-claude-plugin",
  "repository": "https://github.com/karak-developer/karak-claude-plugin",
  "license": "MIT",
  "keywords": [
    "product-management",
    "requirements",
    "agile"
  ],
  "agents": [
    "./agents/requirements-analyst.md",
    "./agents/agile-project-manager.md"
  ]
}
```

- [ ] **Step 3: Validate**

```bash
claude plugin validate ./karak-product
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add karak-product/
git commit -m "feat: add karak-product sub-plugin"
```

---

### Task 5: Update root marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Replace `.claude-plugin/marketplace.json` with the following**

```json
{
  "name": "karak-dev",
  "owner": {
    "name": "karak"
  },
  "metadata": {
    "description": "Design, code review, UX psychology, and specialized cloud architecture tools for Claude Code",
    "version": "1.7.0"
  },
  "plugins": [
    {
      "name": "karak-claude-plugin",
      "source": "./",
      "description": "Meta-package: design, architecture, engineering, and product management tools for Claude Code",
      "version": "1.7.0",
      "author": {
        "name": "karak"
      },
      "homepage": "https://github.com/karak-developer/karak-claude-plugin",
      "repository": "https://github.com/karak-developer/karak-claude-plugin",
      "license": "MIT",
      "keywords": [
        "design",
        "code-review",
        "ux-psychology",
        "cloud-architecture",
        "gcp",
        "apple-hig",
        "icon-design",
        "frontend",
        "accessibility",
        "material-design",
        "android",
        "hifi-design",
        "architecture",
        "c4-model"
      ],
      "category": "development",
      "tags": [
        "design-system",
        "code-quality",
        "ux",
        "cloud",
        "ios",
        "android",
        "material-design",
        "web",
        "hifi-design",
        "architecture",
        "c4-model",
        "plantuml"
      ]
    },
    {
      "name": "karak-design",
      "source": "./karak-design",
      "description": "UI/UX and visual design skills: Apple HIG, Material Design 3, Google design docs, icon design, frontend aesthetics, UX psychology, Hi-Fi design quality, mobile auth screen design",
      "version": "1.0.0",
      "author": {
        "name": "karak"
      },
      "homepage": "https://github.com/karak-developer/karak-claude-plugin",
      "repository": "https://github.com/karak-developer/karak-claude-plugin",
      "license": "MIT",
      "keywords": [
        "design",
        "apple-hig",
        "material-design",
        "icon-design",
        "frontend",
        "ux-psychology",
        "hifi-design",
        "accessibility",
        "android"
      ],
      "category": "development",
      "tags": [
        "design-system",
        "ux",
        "ios",
        "android",
        "material-design",
        "web",
        "hifi-design"
      ]
    },
    {
      "name": "karak-architecture",
      "source": "./karak-architecture",
      "description": "System architecture skills: C4 model diagrams, system design, GCP infrastructure",
      "version": "1.0.0",
      "author": {
        "name": "karak"
      },
      "homepage": "https://github.com/karak-developer/karak-claude-plugin",
      "repository": "https://github.com/karak-developer/karak-claude-plugin",
      "license": "MIT",
      "keywords": [
        "architecture",
        "c4-model",
        "cloud-architecture",
        "gcp"
      ],
      "category": "development",
      "tags": [
        "architecture",
        "c4-model",
        "plantuml",
        "cloud",
        "gcp"
      ]
    },
    {
      "name": "karak-engineering",
      "source": "./karak-engineering",
      "description": "Code quality and review skills: Codex-based code review with session resume, code refactoring, QA management",
      "version": "1.0.0",
      "author": {
        "name": "karak"
      },
      "homepage": "https://github.com/karak-developer/karak-claude-plugin",
      "repository": "https://github.com/karak-developer/karak-claude-plugin",
      "license": "MIT",
      "keywords": [
        "code-review",
        "code-quality"
      ],
      "category": "development",
      "tags": [
        "code-quality",
        "code-review"
      ]
    },
    {
      "name": "karak-product",
      "source": "./karak-product",
      "description": "Product management agents: requirements analysis, agile project management",
      "version": "1.0.0",
      "author": {
        "name": "karak"
      },
      "homepage": "https://github.com/karak-developer/karak-claude-plugin",
      "repository": "https://github.com/karak-developer/karak-claude-plugin",
      "license": "MIT",
      "keywords": [
        "product-management",
        "requirements",
        "agile"
      ],
      "category": "development",
      "tags": [
        "product-management",
        "agile",
        "requirements"
      ]
    }
  ]
}
```

- [ ] **Step 2: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('valid')"
```

Expected: `valid`

- [ ] **Step 3: Verify both version fields are 1.7.0**

```bash
python3 -c "
import json
m = json.load(open('.claude-plugin/marketplace.json'))
assert m['metadata']['version'] == '1.7.0'
assert m['plugins'][0]['version'] == '1.7.0'
print('versions consistent')
"
```

Expected: `versions consistent`

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat: add 4 sub-plugins to marketplace.json, bump meta to 1.7.0"
```

---

### Task 6: Add sync check script

**Files:**
- Create: `scripts/check-sync.sh`

- [ ] **Step 1: Create `scripts/check-sync.sh`**

```bash
#!/usr/bin/env bash
# Fail if any sub-plugin copy has drifted from its canonical source in root skills/ or agents/.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAILED=0

check_copy() {
    local canonical="$1"
    local copy="$2"
    if ! diff -rq "$canonical" "$copy" >/dev/null 2>&1; then
        echo "DRIFT: $copy differs from $canonical"
        FAILED=1
    fi
}

# karak-design
for skill in google-design-docs apple-design icon-design frontend-aesthetics \
             ux-psychologist material-design hifi-design-quality mobile-auth-screen-design; do
    check_copy "$REPO_ROOT/skills/$skill" "$REPO_ROOT/karak-design/skills/$skill"
done
check_copy "$REPO_ROOT/agents/ui-designer.md" "$REPO_ROOT/karak-design/agents/ui-designer.md"

# karak-architecture
check_copy "$REPO_ROOT/skills/write-c4-diagram" "$REPO_ROOT/karak-architecture/skills/write-c4-diagram"
check_copy "$REPO_ROOT/agents/system-designer.md" "$REPO_ROOT/karak-architecture/agents/system-designer.md"
check_copy "$REPO_ROOT/agents/gcp-infrastructure-engineer.md" "$REPO_ROOT/karak-architecture/agents/gcp-infrastructure-engineer.md"

# karak-engineering
check_copy "$REPO_ROOT/skills/codex-review" "$REPO_ROOT/karak-engineering/skills/codex-review"
check_copy "$REPO_ROOT/agents/code-refactorer.md" "$REPO_ROOT/karak-engineering/agents/code-refactorer.md"
check_copy "$REPO_ROOT/agents/quality-assurance-manager.md" "$REPO_ROOT/karak-engineering/agents/quality-assurance-manager.md"

# karak-product
check_copy "$REPO_ROOT/agents/requirements-analyst.md" "$REPO_ROOT/karak-product/agents/requirements-analyst.md"
check_copy "$REPO_ROOT/agents/agile-project-manager.md" "$REPO_ROOT/karak-product/agents/agile-project-manager.md"

if [ "$FAILED" -eq 1 ]; then
    echo "Sync check FAILED. Re-copy from canonical sources."
    exit 1
fi
echo "All sub-plugin copies are in sync."
```

- [ ] **Step 2: Make executable and run**

```bash
chmod +x scripts/check-sync.sh
bash scripts/check-sync.sh
```

Expected: `All sub-plugin copies are in sync.`

- [ ] **Step 3: Commit**

```bash
git add scripts/check-sync.sh
git commit -m "chore: add sync check script for sub-plugin copies"
```

---

### Task 7: Final validation

- [ ] **Step 1: Validate all plugins**

```bash
claude plugin validate .
claude plugin validate ./karak-design
claude plugin validate ./karak-architecture
claude plugin validate ./karak-engineering
claude plugin validate ./karak-product
```

Expected: no errors for any plugin.

- [ ] **Step 2: Validate all plugin.json files have no `version` field**

```bash
python3 -c "
import json
for path in [
    '.claude-plugin/plugin.json',
    'karak-design/.claude-plugin/plugin.json',
    'karak-architecture/.claude-plugin/plugin.json',
    'karak-engineering/.claude-plugin/plugin.json',
    'karak-product/.claude-plugin/plugin.json',
]:
    d = json.load(open(path))
    assert 'version' not in d, f'{path} must not have version field'
    print(f'{path}: OK')
"
```

Expected: 5 lines of `OK`.

- [ ] **Step 3: Validate all skills paths use `./skills/` prefix**

```bash
python3 -c "
import json
for path in [
    '.claude-plugin/plugin.json',
    'karak-design/.claude-plugin/plugin.json',
    'karak-architecture/.claude-plugin/plugin.json',
    'karak-engineering/.claude-plugin/plugin.json',
]:
    d = json.load(open(path))
    for s in d.get('skills', []):
        assert s.startswith('./skills/'), f'{path}: bad skill path: {s}'
    print(f'{path}: skills paths OK')
"
```

Expected: 4 lines of `skills paths OK`.

- [ ] **Step 4: Run sync check**

```bash
bash scripts/check-sync.sh
```

Expected: `All sub-plugin copies are in sync.`

- [ ] **Step 5: Commit docs and finalize**

```bash
git add docs/
git commit -m "docs: add plugin decomposition spec and implementation plan"
```
