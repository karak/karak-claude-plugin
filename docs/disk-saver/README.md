# disk-saver development notes

Design and TDD records kept from the development of `karak-windows-ops/skills/disk-saver`. These files are not part of the distributed plugin.

| File | Contents |
|---|---|
| `design.md` | Design doc: architecture, scan strategy, target catalog, scoring, safety invariants, test list |
| `survey.md` | Read-only disk survey of the development PC that the catalog was based on (redacted) |
| `backlog.md` | Open items and user requests for the next iteration (Japanese) |
| `bench_scandir.py` | Benchmark used to choose `os.scandir` with threads for sizing |
| `evidence/` | Raw pytest output for each TDD slice: `red-*` before implementation, `green-*` after |

Redaction: user name, organization, project names, OEM and the provisioning package name were generalized before these files were added. App and tool versions are removed, and device figures such as RAM and the installed-app list are rounded or summarized. Sizes and dates of the cleanup targets are kept as measured. Paths under the user profile are written as `<user>` or `%USERPROFILE%`.
