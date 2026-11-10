# disk-saver — design doc (Windows 11, Claude Code skill)

Target machine evidence used below: survey.md plus probes run 2026-11-09 (non-elevated). Numbers in the catalog are from this machine; the catalog itself is generic.

## 1. Architecture and layout

**Language: Python 3.13 + pytest 9** (both installed; `uv` available). Rejected alternatives: PowerShell 7.x is installed but the only Pester is 3.x (2016, Windows PowerShell module dir; pwsh sees the same copy) — unusable for spec-style TDD without installing modules. Python also won on evidence: `os.scandir` + `DirEntry.stat(follow_symlinks=False)` sized 12 catalog targets (~600k files, 38 GB) in **48 s with 8 threads** (bench_scandir.py), versus 10–25 min for the earlier full walk. PowerShell survives only as (a) read-only probe one-liners invoked via `subprocess` (`pnputil`, `Get-CimInstance`, `nvm list`) and (b) generated `.ps1` files the user runs elevated.

```
%USERPROFILE%\.claude\skills\disk-saver\   (development copy; now karak-windows-ops/skills/disk-saver)
  SKILL.md                 phases: scan → classify/report → stop → approve → execute → verify
  NOTICE                   MIT attributions (CL, daymade)
  catalog\windows.json     target catalog (schema below) — the ONLY source of paths/commands
  scripts\scan.py          read-only: catalog-driven sizing + evidence probes → scan.json
  scripts\classify.py      pure: protect → classify → score → rank → plan.json + report.md
  scripts\probes\*.py      one module per evidence source (pnputil, vscode, nvm, playwright, browsers, git, procs, registry)
  apply\execute.py         the only file allowed to delete; consumes plan.json + approved ids
  apply\admin_pack.py      renders admin-probe-pack.ps1 / admin-actions.ps1 (never runs them)
  tests\fixtures\          fake home trees, canned pnputil/nvm/docker outputs
  tests\test_*.py
```

Catalog entry schema (extends CL's `id/path/tier/why/regen/command`):
`id, title_ja, paths[] (env-expanded globs), class (PRESERVE|FREE|CHEAP|COSTLY|PROJECT|DECISION|ADVICE), detector (probe name, optional), gates[] (process_not_running:<exe>, admin, tool_present:<exe>), evidence[] (signal names), rebuild_cost (1 none|1.5 small dl|3 large dl|5 build|∞), method ({kind: delete|recycle|command|handoff_admin|advice, command?}), hardlinks (bool)`. METHOD in the report is rendered from `method` and is the single execution truth; `execute.py` never re-derives it.

## 2. Scan strategy (< 3 min target)

- **Catalog-driven only.** No home-directory walk. Each entry expands its globs and sizes them with a bounded iterative `os.scandir` walk; `ThreadPoolExecutor(8)` across entries (I/O-bound, scandir releases the GIL). Measured 48 s for the heavy dozen; whole catalog ≈ 60–90 s cold.
- **Attributes from the directory entry, no extra syscall:** `st_file_attributes`: skip `0x400` reparse (junctions, symlinks, OneDrive root); exclude `0x400000` RECALL_ON_DATA_ACCESS and `0x1000` OFFLINE (cloud placeholders) from bytes; flag `0x200` sparse / `0x800` compressed. For flagged files > 100 MB (vhdx, scanner.db) call `GetCompressedFileSizeW` via ctypes for **size-on-disk**; report both logical and allocated.
- **Hard links:** `DirEntry.stat` on Windows returns `st_nlink=0`; dedupe needs full `os.stat` per file, so it is opt-in per entry (`hardlinks: true` on pnpm store, nvm). Everywhere else bytes are labelled logical.
- **Project discovery** (node_modules etc.) is the one bounded walk: roots = `%USERPROFILE%` top-level dirs minus AppData/OneDrive/dot-dirs, depth ≤ 6, prune at the first `node_modules`/`.git`/`dist`.
- **Cache:** `%LOCALAPPDATA%\disk-saver\scan-<date>.json`, 24 h TTL, `--refresh`; stale header printed like CL. `--deep <path>` opt-in full walk for one subtree. Per-entry 60 s budget → `partial: true`, never silently truncated.
- **Admin-only areas** (Windows\Temp, SoftwareDistribution, shadow storage, DISM store, other users' bins) are *ingested*, not scanned: `admin-probe-pack.ps1` (generated, read-only commands only) writes JSON to the scratchpad and `scan.py --admin-json` merges it.

## 3. Target catalog (Windows)

Class legend (borrowed from daymade): PRESERVE never proposed; FREE/CHEAP grouped approval; COSTLY/PROJECT per-item; DECISION report-only with options; ADVICE report-only, no command.

| id | Path / detector | Class | Evidence signals | Rebuild cost | METHOD (exact) | Admin | Here |
|---|---|---|---|---|---|---|---|
| pagefile | `C:\pagefile.sys`; `Win32_PageFileUsage`, `AutomaticManagedPagefile`, `CrashControl\CrashDumpEnabled` | ADVICE | allocated 21 GB vs RAM ~16 GB, peak use 2.8 GB; CrashDumpEnabled=3 (small dump → no RAM-size requirement) | n/a | advice: custom size 4096–8192 MB via sysdm.cpl, reboot | yes | ~13 GB |
| driverstore-superseded | `pnputil /enum-drivers` grouped by (Original Name, Class GUID); in-use = `Driver Name`/`Extension Driver Names` from `/enum-devices /drivers` | COSTLY | in-use oem66+oem71 (8991); outranked pairs oem374+oem377 (8332), oem7+oem12 (8826); size via `C:\Windows\INF\oemNN.inf` DriverVer → FileRepository folder | 3 (re-download from Intel/OEM) | handoff_admin: `pnputil /delete-driver oem374.inf` (no `/force`; pnputil itself refuses in-use) ×4, pairs together | yes | ~4.3 GB |
| npm-npx | `%LOCALAPPDATA%\npm-cache\_npx` | CHEAP | no `npx`/`npm` process; LastWrite age | 1.5 | delete (permanent) | no | 1.9 GB |
| npm-verify | `%LOCALAPPDATA%\npm-cache\_cacache` | FREE | — | 1 | command `npm cache verify` (GC only) | no | ? |
| npm-cacache | same | COSTLY | n/a | 3 | command `npm cache clean --force` (user-directed option, below verify) | no | 6.1 GB |
| pnpm-store | `%LOCALAPPDATA%\pnpm\store` (`pnpm store path`) | CHEAP | `hardlinks: true` | 1.5 | command `pnpm store prune` | no | ≤1.8 GB |
| uv-cache | `uv cache dir` | CHEAP | — | 1.5 | command `uv cache prune` | no | ≤1 GB |
| nuget-http | `~\.nuget\...\v3-cache`, `plugins-cache`, temp | CHEAP | — | 1.5 | command `dotnet nuget locals http-cache --clear` | no | small |
| nvm-unused | `nvm list` vs `nvm current`; `.nvmrc`/`.node-version`/`engines.node` in discovered projects | COSTLY | current 24.x; three unreferenced 22.x/24.x versions; keep newest per major unless pinned | 1.5 | command `nvm uninstall <ver>` (one per item) | no | ~1.2 GB |
| playwright-stale | `%LOCALAPPDATA%\ms-playwright\*`; `.links\*` → `playwright-core` path → `browsers.json` revisions | COSTLY | link target missing (1 of 4 dead); revision not pinned by any live link; chromium-1223/headless-1223/ffmpeg-1011/winldd-1007 from June | 3 | recycle (no per-revision CLI; `npx playwright install` would GC) | no | ~0.7 GB |
| puppeteer-cache | `~\.cache\puppeteer` | COSTLY | no project in discovery has `node_modules\puppeteer`; LastWrite 2026-05 | 3 | recycle | no | 1.07 GB |
| vscode-vsix | `%APPDATA%\Code\CachedExtensionVSIXs` | FREE | gate process_not_running:Code (11 running now) | 1 | delete | no | 1.73 GB |
| vscode-cache | `%APPDATA%\Code\{Cache,CachedData,GPUCache}` | FREE | same gate | 1 | delete | no | 0.46 GB |
| vscode-stale-ws | `%APPDATA%\Code\User\workspaceStorage\*\workspace.json`: only a `folder` with `file:///` scheme whose path no longer exists qualifies; `workspace` (.code-workspace), `vscode-remote://`, `vscode-vfs://` and any non-file scheme = keep; a path under the OneDrive root qualifies only while the OneDrive root is reachable (sync running) | PROJECT | 7 of 25 here, all `file:///` under OneDrive Desktop; 1 `.code-workspace` entry correctly kept | 1 | recycle (per workspace dir) | no | part of 1.29 |
| vscode-ext-dupes | `~\.vscode\extensions`, same id multiple versions, not in `extensions.json`, not in `.obsolete` | CHEAP | 0 found here (detector still shipped) | 1.5 | recycle | no | 0 |
| vscode-webstorage | `%APPDATA%\Code\WebStorage` | DECISION | may hold chat/extension state | — | advice | no | 1.04 GB |
| edge-cache / chrome-cache | `<profile>\{Cache,Code Cache,GPUCache,GrShaderCache,ShaderCache}` per profile | FREE | process_not_running:msedge / chrome | 1 | delete | no | ~1.9 GB |
| edge-sw-cachestorage | `<profile>\Service Worker\{CacheStorage,ScriptCache}`; list top origins by size from `CacheStorage\<hash>\index` | COSTLY | browser closed; PWA offline data (Teams/Outlook web) is lost, not credentials | 1.5 | delete | no | 2.0 GB |
| browser-snapshots | `User Data\Snapshots` (old-version profile copies) | CHEAP | browser closed | 1 | delete | no | 0.18 |
| chrome-ondevice-model | `User Data\OptGuideOnDeviceModel\*`, `OptGuidePredictionModels`, `optimization_guide_model_store` | DECISION | model present (none here; 0.04 GB of smaller stores) | 3 | advice: `chrome://on-device-internals` / flag `#optimization-guide-on-device-model` = Disabled | no | 0 |
| teams-cache | `Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams\EBWebView\*\{Cache,Code Cache,Service Worker\CacheStorage}` + `tmp`, `Logs` | CHEAP | process_not_running:ms-teams (2 running) | 1 | delete (never the whole EBWebView) | no | ≤1.5 GB |
| user-temp | `%TEMP%\*` older than 7 days, excluding `claude\<current session>`; `pip-unpack-*`, `vscode-stable-user`, `Diagnostics` | FREE | mtime>7d; open-handle test (exclusive open) → skip | 1 | delete | no | ~2.5 GB |
| recycle-bin | `$Recycle.Bin` own SID | ADVICE | — | — | advice 「ごみ箱はご自身で空にしてください」 — never a skill command, because `recycle` rows in the same run depend on the bin (CL's `~/.Trash` rule) | no | 0 |
| project-node-modules | discovered `node_modules`/`.venv`/`target`/`.nuxt`/`.next`/`dist` | PROJECT | sibling manifest; src newest ≥30 d; `git diff-index --quiet HEAD` and no untracked (plumbing); unknown git = disqualified; `.worktrees` counted via `git worktree list` | 5 | recycle | no | ~1.5 GB (three stale work projects) |
| claude-plugin-old | `~\.claude\plugins\cache\<plugin>\<ver>` not in `installed_plugins.json` | CHEAP | version not referenced | 1.5 | recycle | no | ~0.3 |
| codex-packages | `~\.codex\packages\*` (versioned sub-dirs?) | DECISION | structure unknown; report versions, newest kept | 3 | advice | no | 4.0 GB |
| codex-sessions | `~\.codex\sessions` | PRESERVE (USER-DATA) | — | — | — | — | 0.43 |
| claude-vm-bundle | `%APPDATA%\Claude\vm_bundles\*.bundle` | DECISION | `.cowork-adopted` present; rootfs written 11-06 → active; Claude process running | ∞/3 | advice: disable Cowork in app or re-download 8.5 GB | no | 8.5 GB |
| docker-reclaim | `docker system df` (daemon absent now → “unavailable”) | COSTLY | daemon reachable; reclaimable column | 3 | command `docker builder prune -f` / `docker image prune -f` (dangling only; never `-a`, never `--volumes`, never `system prune`) | no | ? |
| wsl-vhdx-compact | `docker_data.vhdx`, `ext4.vhdx`: allocated vs logical | ADVICE | sparse delta | — | advice: `wsl --shutdown` then `wsl --manage docker-desktop --set-sparse true` / `Optimize-VHD` | yes | 1.5 GB |
| win-temp / wu-download | `C:\Windows\Temp`, `SoftwareDistribution\Download` from admin pack | FREE | age>7d | 1 | handoff_admin (Remove-Item lines in admin-actions.ps1) | yes | ? |
| dism-component | `Dism /Online /Cleanup-Image /AnalyzeComponentStore` | COSTLY | “Component Store Cleanup Recommended : Yes” | 5 | handoff_admin `Dism /Online /Cleanup-Image /StartComponentCleanup` (never `/ResetBase`) | yes | ? (WinSxS 9.1 naive) |
| shadow-storage | `vssadmin list shadowstorage` | DECISION | used vs max | — | advice: `vssadmin resize shadowstorage /for=C: /on=C: /maxsize=5%` | yes | ? |
| installer-orphans | `C:\Windows\Installer\*.msp` not referenced in `HKCR\Installer\Patches` | DECISION | cross-ref count | ∞ | advice only (v2) | yes | ≤2.7 |
| onedrive-local | files with neither RECALL nor OFFLINE attr but cloud-backed | ADVICE | 0.67 GB local | — | advice: right-click “Free up space” | no | 0.67 |

**Protected (denylist, checked before the catalog):** OneDrive root, Documents/Desktop/Pictures/Downloads, `.ssh`, `.gnupg`, `.azure`, `.aws`, `ProgramData\P-Pointer4`, Trend Micro, `ProgramData\Microsoft\Provisioning\*.ppkg`, any browser profile file outside the cache subdirs (History, Cookies, Login Data, IndexedDB, Local Storage, Sessions, Database), `*.vhdx` for delete (compact only), `node_modules` under `.vscode\extensions`, `.claude\plugins`, `AppData`, `pnpm` store, `codex\sessions`, `claude\projects`, pagefile/swapfile, `System Volume Information`.

## 4. Usage-evidence model and scoring

Signals (each probe returns `{signal, value, source}`; everything lands in the report's 根拠 column):

| Signal | Source | Caveat |
|---|---|---|
| `process_running` | `tasklist /FO CSV` (stdlib only, no psutil) by exe name (never kill) | gates; blocks delete when true. Edge and Teams keep background processes after the window closes — the report tells the user how to quit fully (Edge tray → 「Microsoft Edge を閉じる」 / startup boost off; Teams tray → 終了) |
| `last_write_age` | newest mtime in subtree (from scan) | reliable |
| `last_access_age` | LastAccessTime (enabled here, system-managed) | approximate: Defender/indexer touch it; used only as *supporting* |
| `referenced_by_config` | `extensions.json`, `.obsolete`, `installed_plugins.json`, `nvm current`, `.nvmrc`, Playwright `.links` + `browsers.json`, `.cowork-adopted` | strong; a positive reference → confidence 0 |
| `superseded_version` | same id, newer version present / `pnputil` Outranked vs Best Ranked | strong |
| `git_clean` | `git diff-index --quiet HEAD` + `git ls-files --others --exclude-standard` empty | unknown = not clean |
| `shell_last_run` | HKCU UserAssist (ROT13, readable) | shell launches only; Prefetch is admin-only here, so not used |
| `admin_required` | catalog | affects ranking, not confidence |

Scoring (`classify.score`): `confidence = base[class] × Π multipliers`, base FREE .95 / CHEAP .85 / COSTLY .70 / PROJECT .50; multipliers: process_running → 0 (blocked, still listed), referenced_by_config → 0, last_write < 7 d → .6, 7–30 d → .8, 30–90 d → .9, > 90 d → 1.0, superseded_version → ×1.2 (cap 1.0), git_clean false/unknown → 0 (PROJECT only).
`priority = reclaimable_GB × confidence ÷ rebuild_cost`. Tie-breaks: no-admin before admin, fewer files first (Recycle Bin on 185k files is slow), older last_write first. ADVICE/DECISION rows are ranked separately by bytes in their own section so the 21 GB pagefile and 8.5 GB VM stay visible without becoming a savings promise.

## 5. Report, approval, execution, verification

Report (`report.md`, Japanese): header 現在の空き容量/合計、スキャン時刻、未計測領域 (admin gap, bytes+count). Section A 「提案（承認待ち）」 table: `# | 対象 | 論理サイズ | 実回収見込み | 分類 | 根拠 | 再構築コスト | METHOD | 管理者`. Section B 「判断が必要」 (DECISION). Section C 「助言のみ」 (ADVICE: pagefile, vhdx compaction, shadow storage). Section D 「保護対象（提案しません）」 with reason. Footer: reclaimable total (proposed only), review-only total labelled overlapping, blocked rows and why (e.g. Code が起動中).

Approval: FREE+CHEAP offered as one grouped `AskUserQuestion` naming every row; COSTLY/PROJECT/handoff individually; DECISION rows ask “which option”; ADVICE never asked. Any row whose METHOD is `delete` says 「ごみ箱を経由せず完全削除」 in the question. Approval produces `approved.json` = plan hash + ids; never carries to another run.

Execution (`apply/execute.py approved.json`): refuses if plan hash mismatches; one invocation per item; `delete` = `shutil.rmtree`/`os.remove` for regenerable caches only; `recycle` = `SHFileOperationW` with `FOF_ALLOWUNDO` (PROJECT, Playwright, workspaceStorage) — such rows show 0 in 実回収見込み until the user empties the bin; `command` = argv (no shell) matching the **command allowlist** `^(npm|pnpm|uv|nvm|dotnet|docker)( [A-Za-z0-9_.:=/@-]+)*$`; `handoff_admin` entries must match the separate **handoff allowlist** of fixed shapes — `pnputil /delete-driver oem\d+\.inf`, `Dism /Online /Cleanup-Image /StartComponentCleanup`, `wsl --manage \S+ --set-sparse true`, and a path-only template for Windows\Temp / SoftwareDistribution\Download that `admin_pack.py` renders as `Remove-Item` lines — and are appended to `admin-actions.ps1`, path printed, nothing run. PowerShell cmdlets are not argv; any cmdlet the skill itself runs goes through `pwsh -NoProfile -NonInteractive -Command ...` and only for read-only probes. After each item: exit code + `os.path.exists` recheck (or tool output for commands); failures carry the raw error text; one failure never stops the run. Never self-elevate; never kill a process to unblock a gate — report 「Code を閉じてから再実行」.

Verification: `GetDiskFreeSpaceExW` before/after per item and in aggregate vs predicted; explain shortfall (Recycle Bin not emptied, sparse, hard links, admin items pending). Re-run the probe for command items (`nvm list`, `pnputil /enum-drivers` after the user ran the admin script) and observe %TEMP%/browser cache refill after 60 s like daymade.

## 6. Safety invariants and test list (spec-style; F = fixture, R = real FS/read-only)

Invariants: (1) scan/classify/probes contain no delete/move/rename primitives; (2) only catalog paths are ever proposed; (3) denylist beats catalog; (4) a gate failure blocks, never kills; (5) METHOD is the only execution source; (6) admin work is handed off, never run; (7) nothing executes without `approved.json` matching the plan hash.

- `test_safety`: scanner, classifier and probe sources contain no deletion primitives (F); every `command` entry matches the command allowlist and every `handoff_admin` entry matches the handoff allowlist, neither with destructive words outside those fixed shapes (F); `pnputil` never appears in a `command` entry (F); guard detects `shutil.rmtree`, `os.remove`, `SHFileOperation` in scanner source (F).
- `test_catalog`: every entry has a class, Japanese title, rebuild cost, and a METHOD consistent with its class (ADVICE has no command; PRESERVE has no method) (F); no entry path falls under the denylist (F).
- `test_protect`: a path inside OneDrive, Documents, .ssh, P-Pointer4, browser History is reported protected with a reason (F); a node_modules under .vscode\extensions or AppData is never a project candidate (F).
- `test_scan`: cloud placeholder files contribute 0 bytes (F via attribute stub); reparse points are not descended (F: junction in tmp_path); a 60 s budget overrun marks the entry partial, not complete (F); scanned bytes for a fixture tree equal the known total (F).
- `test_evidence`: a VS Code extension listed in extensions.json is never proposed even when an older copy exists (F); the newest version of a duplicated extension is kept (F); a workspaceStorage whose folder exists is kept, a missing `file:///` folder qualifies, a remote URI or a `.code-workspace` entry is never treated as stale, and a missing OneDrive path qualifies only while the OneDrive root is reachable (F); the nvm current version is never proposed; a version pinned by `.nvmrc` is never proposed (F); a Playwright revision pinned by a live link is kept, an unpinned one qualifies, a dead link alone is not enough (F); the in-use driver and its paired extension are never proposed; outranked pairs are (F: canned pnputil text); a running owning process blocks the row with reason (F).
- `test_project`: node_modules qualifies only with sibling manifest + ≥30 d + clean git; dirty or unknown git disqualifies (F: real `git init` in tmp_path).
- `test_scoring`: priority order is bytes×confidence÷cost; equal priority prefers non-admin then fewer files (F); ADVICE rows never appear in the proposal total (F).
- `test_report`: report is Japanese, carries the METHOD column, states permanent deletion in words for `delete` rows, and prints a stale warning when scan age > 24 h (F).
- `test_execute`: refuses on plan-hash mismatch; runs one invocation per item; reports a still-existing path as failure; continues after a failure; never emits `taskkill` (F in tmp_path).
- `test_smoke_real` (R, marked `slow`): catalog scan of this machine completes under 180 s and every proposed path exists.

TDD order per slice: create the module stub returning empty results → run pytest, capture the assertion failures to `evidence/red-<slice>.txt` → implement → `evidence/green-<slice>.txt`.

## 7. Implementation order (vertical slices)

1. Catalog + safety tests + `scan.py` sizing of 8 non-gated entries (npm-npx, user-temp, vscode-vsix, playwright, puppeteer, uv, pnpm, nuget) → first Japanese report in ~1 min. This alone exposes ~8 GB.
2. Gates and evidence probes: process_running, extensions.json/.obsolete, workspaceStorage, nvm, Playwright links — adds vscode-stale-ws and nvm rows.
3. `execute.py` with delete/recycle/command + verification; approval flow in SKILL.md. First real reclaim.
4. Admin pack: pnputil driver pairs, pagefile advice, DISM/vssadmin ingest, admin-actions.ps1 — the biggest wins (~17 GB pagefile + 4.3 GB drivers).
5. Browsers/Teams cache entries with origin listing; project-node-modules with git plumbing.
6. DECISION/ADVICE rows (Claude VM, codex packages, vhdx compaction, OneDrive) and the refill observation.

## 8. Licensing and attribution

Both references are MIT. Add `NOTICE` listing “disk-cleanup, Copyright (c) 2026 Charles Ladera, MIT” and “macos-cleaner (daymade-macos), Copyright (c) 2025 daymade, MIT”, with the full MIT text once. Copy with header attribution only what we actually port from CL: the manifest schema, `test_safety.py` guard idea (`source_violations`, `command_violations`) and the project-artifact qualification rule; put `# Derived from CharlesLadera/disk-cleanup (MIT)` at the top of those files. From daymade take only concepts (phase contract, class names, nominal vs physical, refill observation, report sections) — no files, their scripts are macOS-specific. tw93/Mole (GPL-3.0): ideas only, no code, no file. Do not copy CL's macOS manifest entries or daymade's reference prose verbatim.

## Open questions for the user

1. Pagefile: willing to set a custom size (admin + reboot)? It is the single largest item (~13 GB: 21 GB allocated → 8 GB max).
2. Claude desktop Cowork VM (8.5 GB): in use? If not, acceptable to disable/remove and re-download later?
3. Edge/Teams: OK to lose PWA offline caches (requires closing Edge and Teams during execution)?
4. Permanent delete (no Recycle Bin) acceptable for regenerable caches, as the design proposes?
5. `npm cache clean --force` (6.1 GB) as a user-directed option, or exclude entirely?
