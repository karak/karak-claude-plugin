# karak-claude-plugin

Claude Code plugin marketplace (`.claude-plugin/marketplace.json`) with sub-plugins in `karak-*/`.

## Branching and releases

`main` is the release branch. Users install the marketplace from `main` (the default branch), so every merge into `main` is a release. `develop` is the integration branch.

### Required rules

1. **All work merges into `develop`.** Branch from `origin/develop` and open the PR with `--base develop`. The default branch is still `main`, so `gh pr create` without `--base` targets `main` by mistake.
2. **`main` only takes merges from `develop`, and each one bumps versions.** The develop→main merge must raise `metadata.version` and the version of every plugin that changed since `main`. CI job `release-gate` (`scripts/check-release.sh`) enforces both.

### Work branches

- Start every task with `git fetch origin && git switch -c <type>/<topic> origin/develop`. `<type>` is `feat`, `fix`, `docs`, `chore`, `ci`, or `test`.
- Don't check out, pull into, or push to local `main` or `develop`. Change them only through PRs.
- Don't change versions in work PRs. Bumping per PR makes parallel PRs collide on the same number, and the version would no longer match what a release contains. Versions change only in the release-prep PR (below).
- Issue keywords (`Closes #N`) only close issues on merges into the default branch (`main`). In work PRs, write `Refs #N`. List `Closes #N` for the included issues in the develop→main PR body.

### Releasing (merge `develop` into `main`)

Release only when the user asks. A merge into `main` publishes to every user.

1. **Prepare on a branch.** Branch `chore/release-v<X.Y.Z>` from `origin/develop`, where `X.Y.Z` is the new `metadata.version`.
2. **Find what changed.** Run `git diff --stat origin/main origin/develop -- 'karak-*' .claude-plugin/marketplace.json`. A plugin counts as changed when files under its `source` directory changed or its marketplace entry changed apart from `version`.
3. **Bump in `.claude-plugin/marketplace.json` only.** `plugin.json` files carry no `version`; keep it that way.
   - Each changed plugin: major for a removed or renamed skill/agent or another breaking change, minor for a new skill/agent or feature, patch for fixes and wording.
   - `metadata.version`: always bump it on a release, by the largest bump among the plugins (patch when only non-plugin files changed).
   - Bump plugin versions and `metadata.version` in the same commit. `check-sync.sh` fails when a plugin version changes without the top-level one.
4. **Check locally.** Run `HEAD_BRANCH=develop BASE_REF=origin/main bash scripts/check-release.sh`. Then open the PR to `develop` and merge it.
5. **Open the release PR.** Run `gh pr create --base main --head develop`, with the version list and `Closes #N` lines in the body.
6. **Merge with a merge commit.** Never squash or rebase develop→main. Squashing gives `main` commits that `develop` lacks, and every later release PR then shows old changes and conflicts.

There is no hotfix branch. Urgent fixes also go through `develop` and a release.

### Why versions must change

Claude Code decides whether an installed plugin needs updating from its version. Here that is the `version` in the marketplace entry, because `plugin.json` would take precedence if it had one. If the content changes but the version stays the same, users keep the cached old copy. If the same version holds different content on different days, the version means nothing. See https://code.claude.com/docs/en/plugins/loading.md (versions and updates) and https://code.claude.com/docs/en/plugins/host-marketplace.md (release a new version).

## Checks

Run these before opening a PR (CI runs them too):

- `bash scripts/check-sync.sh`: sub-plugin copies match the canonical `skills/` and `agents/`, and a plugin version bump comes with a top-level bump.
- `bash scripts/tests/test-check-release.sh`: scenario tests for the release gate.

## Plugin structure

When adding a skill or editing `plugin.json` / `marketplace.json`, follow the project skill `.claude/skills/plugin-structure-guide`. Write skill files in English.
