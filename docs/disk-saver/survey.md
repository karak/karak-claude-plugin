# Disk survey (read-only), 2026-11-09, NON-ELEVATED shell
Method: robocopy NUL trick fails here; used a .NET directory walk (skips reparse points). Sizes in GB (1024^3). Not admin, so several system paths are unreadable (shown as 0).

> Redaction note: this survey was taken on one work PC. User name, organization, project names, OEM and the provisioning package name have been generalized; app and tool versions removed and the installed-app list summarized. Sizes, dates and the technical findings are unchanged.

## 1. Drives
| Drive | Free | Total |
|---|---|---|
| C: (only fixed drive) | 17.0 GB | ~240 GB class (7% free) |

NTFS last-access: DisableLastAccess = 2 (system managed, updates ENABLED). LastAccessTime is usable but approximate (Defender/indexers/backup also touch it).

## 2. System locations
| Item | Size | Newest write | Note |
|---|---|---|---|
| C:\$Recycle.Bin | 0.0 (only own SID visible) | 2026-11-06 | effectively empty |
| %TEMP% | 3.2 GB | 2026-11-09 | Diagnostics 0.36, vscode-stable-user 0.24, claude 0.19, 5+ pip-unpack-* ~0.16 each (Nov 6-7) |
| C:\Windows\Temp | unreadable (no admin) | - | |
| C:\Windows.old | not present | | |
| SoftwareDistribution\Download | 0.0 / unreadable | | SoftwareDistribution total 0.06 |
| DeliveryOptimization | not found/inaccessible | | |
| C:\Windows\Installer | 2.7 GB | 2026-11-06 | $PatchCache$ 0.0 (newest 2023-10-24) |
| C:\Windows\WinSxS | 9.1 GB naive (hardlinks inflate it) | 2026-07-26 | |
| System32\DriverStore\FileRepository | 12.2 GB (>1GB) | 2026-10-26 | three Intel iigd_dch graphics driver packages: 2.30 + 2.10 + 1.94 GB; old versions removable via pnputil (admin) |
| C:\Windows\assembly | 1.0 | 2026-10-30 | |
| C:\Windows total | 34.4 GB | | System32 17.4 |
| hiberfil.sys | absent (hibernation off) | | |
| pagefile.sys | 15.5 GB (>1GB) | 2026-11-09 | |
| swapfile.sys | 0.02 | | |
| LiveKernelReports / Minidump / MEMORY.DMP / CrashDumps | 0 / absent / absent / absent | | |
| WER (ProgramData\Microsoft\Windows\WER) | 0.0 | 2026-11-09 | |

### WSL / VMs / vhdx (user profile)
| File | Size | LastWrite | LastAccess |
|---|---|---|---|
| Roaming\Claude\vm_bundles\claudevm.bundle\rootfs.vhdx | 8.46 GB (>1GB) | 2026-11-06 | 2026-11-06 |
| ...\claudevm.bundle\sessiondata.vhdx | 0.57 | 2026-11-05 | 2026-11-09 |
| ...\claudevm.bundle\smol-bin.vhdx | 0.04 | 2026-11-04 | 2026-11-09 |
| Local\Docker\wsl\disk\docker_data.vhdx | 1.48 GB (>1GB) | 2026-10-26 | 2026-11-09 |
| Local\Docker\wsl\main\ext4.vhdx | 0.15 | 2026-11-09 | 2026-11-09 |

No Ubuntu/other WSL distro packages; `wsl -l -v` lists only docker-desktop. Docker Desktop installed.

### Browsers
Chrome (registry; Application folder is under Program Files, not LocalAppData). Edge. Chrome User Data total 2.0 GB across several profiles; Edge User Data ~4.1 GB.
| Profile | Total | Cache | Code Cache | Service Worker |
|---|---|---|---|---|
| Chrome profiles (largest one) | 0.58 | 0.34 | 0.18 | 0.03 |
| Chrome profiles (all, combined) | ~1.6 | ~0.7 | ~0.7 | ~0.1 |
| Edge Default | 3.39 (>1GB) | 0.25 | 0.35 | 2.0 (>1GB) |

Chrome other: PlaywrightAttach 0.16, Snapshots 0.05. On-device AI model folders: Chrome optimization_guide_model_store 0.04, OnDeviceHeadSuggestModel 0.01, no OptGuideOnDeviceModel folder. Edge model folders ~0; component_crx_cache 0.19, ProvenanceData 0.16, Snapshots 0.13.

### AI model stores
~\.ollama, ~\.lmstudio, ~\.cache\huggingface, torch, whisper, nomic.ai, LM-Studio: all MISSING. ~\.cache = 1.8 GB (puppeteer 1.07, chrome-devtools-mcp 0.52, chrome-cdp-e2e 0.12). ~\.codex 5.1 GB (packages 4.02, sessions 0.43, .sandbox-bin 0.35).

### Dev caches
| Item | Size | Newest write |
|---|---|---|
| Local\npm-cache | 8.0 GB (>1GB): _cacache 6.09, _npx 1.93 | 2026-11-09 |
| Local\pnpm (store 1.84) | 1.85 | 2026-11-06 |
| Local\pnpm-cache | 0.44 | 2026-11-07 |
| Local\uv\cache | 0.98 | 2026-11-05 |
| pip cache (Local\pip) | 0.0 | |
| yarn, Roaming\npm-cache, ~\.npm, ~\.gradle, ~\.m2, ~\.android, Android SDK, JetBrains, Cursor, go mod | missing | |
| ~\.nuget\packages | 0.92 | 2026-11-06 |
| ~\.rustup | 1.27 (>1GB, toolchains) | 2026-07-15 |
| ~\.cargo / ~\.bun | 0.21 / 0.19 | |
| Local\nvm | 1.53 (two Node 24.x versions: 0.73, 0.61) | 2026-11-04 |
| Local\ms-playwright | 2.07 (chromium-1254/1234/1223 + headless shells; 1223 from 2026-06-19) | 2026-11-07 |
| Local\ms-playwright-mcp | 0.40 | |
| ~\.cache\puppeteer | 1.07 | 2026-05-19 |
| ~\.vscode\extensions | 5.5 (>1GB) | 2026-11-09 |
| Roaming\Code | 4.7 (CachedExtensionVSIXs 1.73, User 1.29, WebStorage 1.04, CachedData 0.34, Cache 0.12) | 2026-11-09 |
| Local\Programs (VS Code 2.1, Python 0.78, antigravity 0.49, Zed 0.43, draw.io 0.42, Git 0.42) | 5.1 | |
| Local\Figma 1.2, GitHubDesktop 1.08, slack 0.87, superpowers 0.68, PowerToys 0.94, Roaming\Zoom 1.31 | | |

### Office / Teams / OneDrive
| Item | Size |
|---|---|
| New Teams (Packages\MSTeams_8wekyb3d8bbwe) | 1.58 GB |
| Local\Microsoft: Office 1.79, Olk (new Outlook) 1.04, OneNote 0.66, OneDrive client 3.06 (ListSync db 0.90) | |
| Packages\Microsoft.MicrosoftOfficeHub | 1.02 |
| OST/PST files | none found |
| OneDrive - &lt;organization&gt; | 35.5 GB logical. Files On-Demand IS in use: about 70% of ~100k files are cloud-only placeholders (almost all of the logical size); well under 1 GB is actually local. The largest folder is meeting recordings (cloud-only). Not a real disk cost. |

~\.claude: 1.26 GB (plugins 0.73, projects 0.31, backups 0.16).

## 3. node_modules (61 found outside AppData, 5.3 GB total; top 20; "src newest" = newest file excluding node_modules/.git/dist/build/etc.)
Project names are replaced with labels; the same label means the same project.
| node_modules (under %USERPROFILE%) | GB | project src newest |
|---|---|---|
| project-A\develop | 1.04 | 2026-11-06 |
| side-projects\project-B | 0.38 | 2026-11-09 |
| project-C\backend\app-1 | 0.37 | 2026-03-09 (stale) |
| code-samples\project-D\vue | 0.33 | 2026-04-09 (stale) |
| .claude\plugins\cache\...\chrome-devtools-mcp\<old ver> | 0.23 | 2026-08-13 (old plugin version) |
| .vscode\extensions\ms-azuretools.vscode-azurestorage-<ver>\dist | 0.22 | extension |
| project-E\main\nuxt-app | 0.22 | 2026-04-15 (stale) |
| project-F\app | 0.22 | 2026-10-23 |
| project-A\worktree-1\app | 0.20 | 2026-07-31 |
| code-samples\project-G\app | 0.19 | 2025-08-15 (stale) |
| project-E\main\...\.worktrees\design-system | 0.18 | 2026-04-13 (stale) |
| project-C\backend\app-2 | 0.17 | 2026-03-09 (stale) |
| worktrees\project-H\client | 0.15 | 2026-11-07 |
| .vscode\extensions\ms-dotnettools.csdevkit-<ver>\vs-green-server (2 copies) | 0.13 each | extension |
| ...\.worktrees\worktree-2 | 0.11 | 2026-07-01 |
| .vscode\extensions\.<hash>\dist | 0.11 | extension |
| ...\.worktrees\worktree-3 | 0.10 | 2026-06-04 |
| code-samples\project-I\code | 0.09 | 2025-08-19 (stale) |
| .claude\plugins\cache\...\chrome-devtools-mcp\<newer ver> | 0.07 | 2026-09-14 |

node_modules total is small; not the main space consumer.

## 4. Files >500MB (user profile + ProgramData; only 8; OneDrive placeholders excluded)
| File | GB | LastWrite | LastAccess |
|---|---|---|---|
| Roaming\Claude\vm_bundles\claudevm.bundle\rootfs.vhdx | 8.46 | 2026-11-06 | 2026-11-06 |
| ProgramData\P-Pointer4\scanner.db | 3.79 | 2026-11-09 | 2026-11-09 (actively written) |
| Local\Docker\wsl\disk\docker_data.vhdx | 1.48 | 2026-10-26 | 2026-11-09 |
| Local\Microsoft\OneDrive\ListSync\...\Microsoft.ListSync.db | 0.90 | 2026-11-09 | 2026-11-09 |
| ProgramData\Microsoft\Provisioning\&lt;provisioning package&gt;.ppkg | ~0.7 | (old) | (recent) |
| ProgramData\P-Pointer4\scanner.log.backup.zip | 0.67 | 2026-11-09 | 2026-11-09 |
| Roaming\Claude\...\sessiondata.vhdx | 0.57 | 2026-11-05 | 2026-11-09 |
| Roaming\Code\CachedExtensionVSIXs\openai.chatgpt-...-win32-x64 | 0.57 | 2026-10-24 | 2026-11-09 |
(Windows dir: only pagefile.sys 15.5 GB.)

## 5. Top folders
%USERPROFILE% (99.0 GB, OneDrive reparse point excluded): AppData 67.1; .vscode 5.5; .codex 5.1; side-projects 3.3; project-A 2.75; .cache 1.8; project-E 1.65; .local 1.34; .rustup 1.27; .claude 1.26; code-samples 0.94; .nuget 0.92; other work projects 0.90 / 0.59 / 0.37 / 0.36 / 0.28 / 0.28; .config 0.80; .azure 0.29.
%LOCALAPPDATA% (49.4): Microsoft 11.7 (Edge 4.06, OneDrive 3.06, Office 1.79, Olk 1.04, OneNote 0.66); npm-cache 8.0; Programs 5.1; Temp 3.2; Packages 3.1; ms-playwright 2.07; Google 2.0; pnpm 1.85; Docker 1.68; nvm 1.53; Figma 1.2; GitHubDesktop 1.08; uv 0.98; PowerToys 0.94; slack 0.87; superpowers 0.68; pnpm-cache 0.44; ms-playwright-mcp 0.40; SquirrelTemp 0.36; agy 0.36.
%APPDATA% (17.6): Claude 10.75 (vm_bundles 9.1, claude-code 0.59, claude-code-vm 0.31, Cache 0.27); Code 4.69; Zoom 1.31; Figma 0.42; Slack 0.30; Microsoft 0.08.
C:\ProgramData (8.0): P-Pointer4 4.61 (third-party scanner app: scanner.db 3.79 + log zip 0.67); Microsoft 1.53 (Provisioning ~0.7, Defender 0.34, WDF 0.29); &lt;OEM&gt; 1.41; Package Cache 0.38; USOShared 0.08.
Accounting: C: used ~220 GB vs Windows 34.4 + profile 99 + ProgramData 8 + pagefile 15.5 = ~157 GB; remaining ~60 GB is Program Files, other users, System Volume Information (shadow copies/restore points), and unreadable system areas (not measured without admin).

## 6. Installed apps by registry EstimatedSize (top 20, summarized)
Summarized by category (rounded): browsers and WebView runtimes ~11 GB (Copilot, Edge, Edge WebView2, Chrome); container and VM tooling ~4 GB (Docker Desktop, WSL); SDKs and runtimes ~2.5 GB (.NET, JDKs); editors and dev tools ~5 GB (VS Code and other editors, Git, database and cloud CLIs); utilities, sync and endpoint security ~1.5 GB. No single app other than the browsers exceeds ~3.5 GB, so uninstalling apps is not a meaningful lever on this machine.

## Could not measure
Not elevated: C:\Windows\Temp, SoftwareDistribution\Download, DeliveryOptimization, other users' Recycle Bin, System Volume Information, C:\Windows\CSC. Program Files not surveyed. Main scan did not follow reparse points (OneDrive measured separately). Directory listings in the main scan go to depth 4; browser caches measured separately.
