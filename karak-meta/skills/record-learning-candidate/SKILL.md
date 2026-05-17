---
name: record-learning-candidate
description: Use when the Stop hook injects a "learning candidate" instruction containing a transcript path and date — records a one-line pointer to today's conversation log into auto-memory so future sessions can grep back into past learnings. Fires on phrases like "record learning candidate", "log today's learnings", "stop hook learning pointer", or when a hook message names a transcript_path and asks for keyword extraction. Always invoke when the hook prompt arrives; do not skip even if the session feels routine — the value comes from accumulating pointers, not from filtering them.
metadata:
  type: meta
---

# Record Learning Candidate

## When this fires

The `karak-meta` plugin installs a Stop hook that runs after every Claude turn finishes. The hook checks whether ≥24h have elapsed since the most recent `learning-candidate-*.md` in the auto-memory directory. If yes, it injects a short instruction into the next turn telling you to use this skill. The hook also passes:

- `transcript_path` — absolute path to the current session's `.jsonl` transcript
- `date` — today's date in `YYYY-MM-DD` (local time)
- `since` — UTC timestamp of the previous record (or `null` if none)

If the hook did **not** fire (no instruction in context, no transcript_path mentioned), do not run this skill spontaneously — the user did not ask for it.

## What to produce

A single Markdown memory file plus a one-line entry in `MEMORY.md`. The point is to leave a **breadcrumb you can grep back to later**, not a full summary.

### File location

`~/.claude/projects/<encoded-cwd>/memory/learning-candidate-<YYYY-MM-DD>.md`

The encoded directory is the same one that already holds `MEMORY.md` and other auto-memory files in this session. Resolve it by stripping the filename off the path of an existing entry like `MEMORY.md`. Do not hardcode the project name.

If a file for today's date already exists, **append to it** (multiple Stop events on the same day — the hook will only call you once per 24h but boundary days can collide). Append a new bullet under a fresh `## <HH:MM>` header rather than overwriting.

### File contents

```markdown
---
name: learning-candidate-2026-05-18
description: Learning-candidate pointer for 2026-05-18 — keywords: <≤31char grep string>
metadata:
  type: reference
---

## 14:23

- **Transcript:** `/Users/.../<session-uuid>.jsonl`
- **Keywords:** `<≤31char grep string>`
- **Hook range:** since `<since-iso>` until `<now-iso>`
- **Why this might matter:** <one-sentence reason a future session might want to grep this back>
```

The `Keywords` field is the load-bearing part. It is the string a future you will `grep -l` for across `learning-candidate-*.md` files when trying to remember "did I work on X recently?". Pick it so that:

- it is ≤31 characters (hard cap — count bytes if mixing scripts; truncate if needed)
- it names the **concrete artifact + action**, not generic verbs ("auth JWT cookie refresh fix" beats "bug fix today")
- it uses tokens that will actually appear in the future grep query — file names, library names, error symbols, project nouns
- multi-token: separate with spaces or `+`; a single keyword wastes the budget

If the session genuinely had no learning worth a pointer (e.g., a chat that was all clarification questions), still write the entry but say so explicitly — `Keywords: <no learning — clarify only>` — so you don't re-scan the same dead turn next time the hook fires.

### MEMORY.md index entry

Append exactly one line to `MEMORY.md` under any existing header (or at the end):

```
- [Learning 2026-05-18](learning-candidate-2026-05-18.md) — <same ≤31char keyword string>
```

Do **not** add a fresh section header for every entry; that pollutes the index. If today's entry is already indexed (appending to an existing file), skip this step.

## How to extract keywords

You have the full conversation context loaded already — that is by design. The hook does not ship the transcript bytes; it relies on you using your own context window as the source of truth for "what happened since the last hook fire".

1. Skim back through the user/assistant turns in the current session.
2. Identify the **one or two concrete things** that were learned, decided, built, or fixed. Surface decisions and surprises; deprioritize routine progress.
3. Compress to a noun-phrase under 31 chars. Examples (each ≤31 chars):
   - `karak-meta Stop hook 24h gate`
   - `Cloud Run 404 rewrite fix`
   - `SwiftData V2 migration rollback`
   - `MSW resetHandlers afterEach`
4. If multiple sessions intersected, pick the keyword that disambiguates the work from the other sessions — that is what makes the pointer useful.

## Steps to execute

1. **Read the hook instruction** from the latest user-style message in context. Extract `transcript_path`, `date`, and `since` (or note `since=null`).
2. **Resolve the memory directory** by reading one existing memory file's path (e.g. `MEMORY.md`). Construct the new filename from `date`.
3. **Check whether today's file exists.** If yes, plan to append; if no, plan to create.
4. **Extract keywords** following the guidance above. Verify length ≤31 chars.
5. **Write the file** (Write tool for new file, Edit tool for append).
6. **Update MEMORY.md** with the index line, unless appending to an existing day's entry.
7. **Report back** to the user in one sentence: file path written + keyword string. Do not paste the full file contents into the chat.

## Examples

### Example 1 — fresh day, real learning

Hook injects: `transcript_path=/Users/x/.claude/projects/-Users-x-foo/abc.jsonl date=2026-05-18 since=2026-05-16T11:02:00Z`

Output file `learning-candidate-2026-05-18.md`:

```markdown
---
name: learning-candidate-2026-05-18
description: Learning-candidate pointer for 2026-05-18 — keywords: karak-meta Stop hook 24h gate
metadata:
  type: reference
---

## 14:23

- **Transcript:** `/Users/x/.claude/projects/-Users-x-foo/abc.jsonl`
- **Keywords:** `karak-meta Stop hook 24h gate`
- **Hook range:** since `2026-05-16T11:02:00Z` until `2026-05-18T05:23:00Z`
- **Why this might matter:** First implementation of the Stop-hook-based learning-pointer flow; details around 24h-boundary handling and stop_hook_active loop guard live in this transcript.
```

MEMORY.md gets: `- [Learning 2026-05-18](learning-candidate-2026-05-18.md) — karak-meta Stop hook 24h gate`

### Example 2 — second Stop on the same day (appending)

Today's file already exists from this morning. Append a new `## HH:MM` section to the same file. Do **not** touch MEMORY.md.

### Example 3 — chat had no real learning

```markdown
## 22:11

- **Transcript:** `...`
- **Keywords:** `<no learning — clarify only>`
- **Hook range:** since `...` until `...`
- **Why this might matter:** Logged so the 24h window advances; nothing to recover here.
```

The pointer is still useful: it tells future-you "you already looked, there is nothing there".

## Anti-patterns

- **Writing a long summary in the memory body.** This is a pointer, not a journal. Keep the body to the four bullets shown above. Anything more goes in the transcript itself.
- **Putting the keyword in past-tense verb form** (`fixed the Cloud Run rewrite`). Future-you will grep for nouns (`Cloud Run rewrite`), not verbs.
- **Using all 31 chars on one giant word.** Hyphenated mega-tokens defeat the grep; prefer 2–4 short tokens.
- **Skipping MEMORY.md updates** on first-of-the-day entries. Without the index line, the file exists but is not surfaced at session start.
- **Running this skill without a hook instruction in context.** The hook is the trigger; running ad-hoc creates duplicates and confusion. If the user explicitly asks you to record a learning out of band, that is fine, but say so and pick the date manually.
