# Issue #12 - Let a Short Link expire

One Claude Code session, start to finish.

| | |
|---|---|
| Ticket | [#12 Let a Short Link expire](https://github.com/kyokosawada/orban-labs-challenge/issues/12) |
| Model | `claude-opus-5` (160 replies) |
| Ran | 2026-07-30 18:26 UTC to 2026-07-30 18:46 UTC |
| Prompts | 1 |
| Tool calls | 113 |
| Session log | `0635671e-b32b-4e2e-b0cc-a92ed3bb3b25.jsonl` |

## What was trimmed

This file is generated from the session's own JSONL log. Every user prompt and every visible
assistant reply is reproduced in full and in order, including the wrong turns. Nothing was
reworded and no exchange was dropped.

Four things were left out, uniformly, to keep the file readable:

- **Tool results.** All 113 of them: command output, file contents, search results.
  The tool *calls* are kept, one line each, so the sequence of work is still visible.
- **Tool call bodies.** A call is shown as its name plus the file it touched, or the command it
  ran shortened to 300 characters. The text written by a `Write` or an `Edit` is not repeated
  here; it is the code, and the code is in this repository.
- **Internal reasoning blocks.** 32 of them. These are the model's private scratch
  space, not part of its reply.
- **Harness bookkeeping.** 28 records of skill definitions, system reminders, hook output
  and background-task notifications injected by Claude Code rather than written by either party.

Absolute paths were rewritten: the worktree the session ran in appears as `<repo>` and the home
directory as `~`. Nothing else in the text was changed.

---

## Prompt 1 - 2026-07-30 18:27 UTC

```
FIRSTMATE_OP: v1 launch-brief: You are a crewmate: an autonomous worker agent managed by firstmate. Work on your own; do not wait for a human.

# Task
Your instructions are at `~/firstmate/data/orban-b-expiry/task.md`.

Read it in full, then read everything it and the standing rules tell you to read, then
build the ticket. Work test-first at the seam it names, typecheck as you go, run the full
suite before you finish, run `/code-review`, and write its outcome to the report path.

Five other workers are building neighbouring tickets in this same repo right now. Stay
strictly inside your own ticket and your own project directory.


# Herdr lifecycle declaration - NOT ENABLED
**HARD SAFETY GATE:** this scaffold cannot inspect the task text that replaces `{TASK}` later.
If the task will start, stop, delete, restart, profile, or otherwise drive Herdr lifecycle behavior, stop and regenerate the brief with `--herdr-lab` before dispatch.
Do not add Herdr lifecycle commands to this unguarded brief by hand.

# Setup
You are in a disposable git worktree of orban-labs-challenge, at a detached HEAD on a clean default branch.

**Verify isolation before anything else.** Run `pwd -P` and `git rev-parse --show-toplevel`; both must resolve to the disposable task worktree you were launched in, such as a treehouse pool path or an Orca-managed worktree, not the primary checkout firstmate operates from.
The path check is authoritative: `git rev-parse --git-dir` and `git rev-parse --git-common-dir` can help inspect the repo, but they do not prove you are outside the primary checkout.
If the top-level path is the primary checkout or not the worktree you were launched in, STOP - do not branch or commit here - append `blocked: launched in primary checkout, not an isolated worktree` to the status file and stop.

1. First action: create your branch: `git checkout -b fm/orban-b-expiry`

# Rules
1. Never push to any remote and never open a PR. Work only on your `fm/orban-b-expiry` branch; firstmate handles the merge into local `main`.
2. Stay inside this worktree; modify nothing outside it.
3. Use gh-axi for GitHub operations and chrome-devtools-axi for browser operations.
4. Report status by appending one line:
   `echo "{state}: {one short line}" >> '~/firstmate/state/orban-b-expiry.status'`
   States: working, needs-decision, blocked, paused, done, failed.
   Each append wakes firstmate, so report sparingly: only phase changes a supervisor
   would act on (setup done, bug reproduced, fix implemented, validation passed) and the
   needs-decision/blocked/paused/done/failed states. No step-by-step FYI progress lines;
   firstmate reads your pane for that.
   A mid-task `working:` line (including setup complete) is nonterminal: do not end the
   turn after it; continue the same stage until a defined `done:` gate under Definition of done.
   Use `paused: {why}` - distinct from `blocked:` - ONLY when you are deliberately idling on a
   known external wait you expect to clear on its own (an upstream release, a rate-limit reset,
   a scheduled window): firstmate then leaves your idle pane alone and rechecks it on a long
   cadence instead of treating it as a possible wedge. Use `blocked:` when you are stuck and need help.
5. If you hit the same obstacle twice, append `blocked: {why}` and stop; firstmate will help.
6. If a decision belongs above the implementation worker (product choices, destructive actions, ask-user findings),
   append `needs-decision: {summary of options}` and stop. Firstmate will apply the configured authority and reply with the decision.
   When firstmate replies or a blocker clears and you resume, append `resolved: {how it was decided or unblocked}` (add the same `[key=<slug>]` if you opened it with one) so the decision or blocker is durably closed and does not keep resurfacing.
7. Never stop, restart, or update the shared `no-mistakes` daemon - it is one instance serving
   every lane/home, so restarting it kills other lanes' in-flight pipeline runs. On ANY no-mistakes
   daemon error, append `blocked: {the daemon error}` and stop; only firstmate manages the daemon.
8. Write no comments in committed project code: no explanatory comments, no docblocks,
   no section banners. Put the reasoning in the commit message, the ticket, or the project notes.
   A file header the repo documents as the authoritative owner of that file's behavior or
   contract is an interface, not an explanatory comment, and is out of scope.
9. Commit format in orban-labs-challenge, measured from its last 26 non-merge commits (all this repo has):
   - Body:    26/26 carry one             -> write a subject line and a body
   - Case:    0/26 lowercase              -> start with a capital
   - Prefix:  0/26 carry a type: prefix   -> no feat:/fix:/chore: prefix
   Where a measure above is decisive it is a rule, not a preference; where it says mixed, read the log and match it.
   Those numbers describe orban-labs-challenge only. If you commit in another repo, measure that one first: `~/firstmate/bin/fm-commit-style.sh <repo-path>`.

# Project memory
If `AGENTS.md` or `CLAUDE.md` already exists, or if this task produced durable project-intrinsic knowledge, run `~/firstmate/bin/fm-ensure-agents-md.sh .` in the worktree.
Record only project knowledge useful to almost every future session.
For anything the codebase already shows, prefer a pointer to the authoritative file, command, or doc over copying the detail.
If you touch a project `AGENTS.md` that lacks `## Maintaining this file`, add that short self-governance section from `~/firstmate/bin/fm-ensure-agents-md.sh` in the same pass.
Keep it proportionate: skip `AGENTS.md` edits for trivial tasks that produced no durable project knowledge.

# Definition of done
This project ships **local-only**: no remote, no PR, no pipeline.
The task is complete only when committed on your branch `fm/orban-b-expiry`. Do NOT push, do NOT open a PR, do NOT merge.
Keep your branch a clean fast-forward onto the current default branch - if `main` has advanced, rebase onto it so the eventual merge stays a fast-forward.
When it is implemented and committed, append `done: ready in branch fm/orban-b-expiry` to the status file and stop.
The configured merge authority approves the ready branch, then firstmate merges it into local `main` through the guarded fast-forward path.
```

**Assistant**

I'll start by verifying isolation and reading the task.

```text
Bash  pwd -P && git rev-parse --show-toplevel && git rev-parse --git-dir && git rev-parse --git-common-dir
Read  ~/firstmate/data/orban-b-expiry/task.md
```

**Assistant**

Isolation verified - I'm in the treehouse worktree, not the primary checkout.

```text
Bash  git checkout -b fm/orban-b-expiry
Read  ~/firstmate/data/orban-standing-rules.md
Bash  ls && echo "---" && ls project-b-ai-assisted && echo "--- docs" && find docs project-b-ai-assisted/docs -type f 2>/dev/null | head -50
Bash  GH_REPO=kyokosawada/orban-labs-challenge gh-axi issue view 12 --full
Read  AGENTS.md
Read  project-b-ai-assisted/docs/spec.md
Read  project-b-ai-assisted/CONTEXT.md
Read  project-b-ai-assisted/docs/adr/0003-expiry-is-optional-and-indistinguishable-from-absence.md
Bash  cd <repo>/project-b-ai-assisted && find backend tests frontend -type f -not -path '*/node_modules/*' -not -path '*/.next/*' | sort
Bash  for f in backend/db.py backend/repository.py backend/routes.py backend/schemas.py backend/errors.py backend/config.py backend/codes.py backend/main.py backend/auth.py; do echo "===== $f"; cat -n "$f"; done
Bash  for f in tests/conftest.py tests/test_short_links.py tests/test_redirect.py pytest.ini requirements-dev.txt; do echo "===== $f"; cat -n "$f"; done
Bash  cd project-b-ai-assisted && for f in requirements.txt frontend/package.json frontend/app/page.tsx frontend/app/shorten-view.tsx frontend/app/api/shortener-api.ts frontend/app/api/short-links/route.ts frontend/app/errors.ts; do echo "===== $f"; cat -n "$f"; done
Bash  for f in requirements.txt frontend/package.json frontend/app/page.tsx frontend/app/shorten-view.tsx frontend/app/api/shortener-api.ts frontend/app/api/short-links/route.ts frontend/app/errors.ts; do echo "===== $f"; cat -n "$f"; done
Bash  ls -a && python3 --version && (test -d .venv && echo "venv exists" || echo "no venv")
Bash  grep -n "field\|expiry\|label" frontend/app/globals.css | head -40
Bash  python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt && .venv/bin/python -m pytest 2>&1 | tail -5
Read  project-b-ai-assisted/frontend/app/globals.css
```

**Assistant**

Baseline is green (23 passed). Now the tests first.

```text
Write  project-b-ai-assisted/tests/test_expiry.py
Bash   .venv/bin/python -m pytest tests/test_expiry.py 2>&1 | tail -20
```

**Assistant**

Red as expected. Now the implementation.

```text
Write  project-b-ai-assisted/backend/clock.py
Edit   project-b-ai-assisted/backend/db.py
Edit   project-b-ai-assisted/backend/schemas.py
Edit   project-b-ai-assisted/backend/schemas.py
```

**Assistant**

Now the repository:

```text
Edit  project-b-ai-assisted/backend/repository.py
Edit  project-b-ai-assisted/backend/repository.py
Edit  project-b-ai-assisted/backend/routes.py
Edit  project-b-ai-assisted/backend/routes.py
Bash  .venv/bin/python -m pytest 2>&1 | tail -20
Bash  cat ../.gitignore 2>/dev/null | head -30; echo "--- status"; git status --short
Bash  .venv/bin/pip install -q mypy 2>&1 | tail -2; .venv/bin/python -m mypy backend --ignore-missing-imports 2>&1 | tail -20
Bash  git add backend/clock.py backend/db.py backend/repository.py backend/routes.py backend/schemas.py tests/test_expiry.py && git commit -q -F - <<'EOF' Accept an optional expiry when a Short Link is minted A Short Link may now carry a moment after which it stops resolving. Most are created without one, ...
```

**Assistant**

Now part two: expired links stop resolving.

```text
Edit  project-b-ai-assisted/tests/test_expiry.py
Edit  project-b-ai-assisted/tests/test_expiry.py
Bash  .venv/bin/python -m pytest tests/test_expiry.py 2>&1 | tail -15
```

**Assistant**

Red on exactly the four resolution behaviours. Now the lookup filter.

```text
Edit  project-b-ai-assisted/backend/repository.py
Edit  project-b-ai-assisted/backend/repository.py
Edit  project-b-ai-assisted/backend/routes.py
Bash  .venv/bin/python -m pytest 2>&1 | tail -8 && .venv/bin/python -m mypy backend --ignore-missing-imports 2>&1 | tail -5
Bash  git add backend/repository.py backend/routes.py tests/test_expiry.py && git commit -q -F - <<'EOF' Stop resolving a Short Link once its expiry has passed The expiry is part of the lookup rather than a check after it, so an expired Short Link is simply not found. A visitor meets the same plain 404 a ...
Bash  echo "working: expiry backend done and green, moving to the interface" >> '~/firstmate/state/orban-b-expiry.status'
Read  project-b-ai-assisted/frontend/app/globals.css
Edit  project-b-ai-assisted/frontend/app/shorten-view.tsx
Edit  project-b-ai-assisted/frontend/app/shorten-view.tsx
Edit  project-b-ai-assisted/frontend/app/shorten-view.tsx
Edit  project-b-ai-assisted/frontend/app/shorten-view.tsx
Edit  project-b-ai-assisted/frontend/app/shorten-view.tsx
Edit  project-b-ai-assisted/frontend/app/shorten-view.tsx
Edit  project-b-ai-assisted/frontend/app/shorten-view.tsx
Edit  project-b-ai-assisted/frontend/app/shorten-view.tsx
Edit  project-b-ai-assisted/frontend/app/globals.css
Edit  project-b-ai-assisted/frontend/app/globals.css
Edit  project-b-ai-assisted/frontend/app/globals.css
Bash  cd frontend && (test -d node_modules && echo "deps present" || npm install --no-audit --no-fund 2>&1 | tail -3) && npx tsc --noEmit 2>&1 | tail -20
Bash  cd frontend && npx tsc --noEmit; echo "tsc exit=$?"
Bash  npx tsc --noEmit; echo "tsc exit=$?"
Bash  cd .. && SHORTENER_API_KEY=local-dev-key SHORTENER_DATABASE_PATH=/tmp/expiry-demo-$$.db .venv/bin/python -m uvicorn backend.main:app --port 8112 --host 127.0.0.1
Bash  SHORTENER_API_KEY=local-dev-key SHORTENER_API_URL=http://127.0.0.1:8112 SHORTENER_PUBLIC_BASE_URL=http://127.0.0.1:8112 npx next dev --port 3112
Bash  curl -s -o /dev/null -w "api:%{http_code}\n" http://127.0.0.1:8112/docs; curl -s -o /dev/null -w "web:%{http_code}\n" http://127.0.0.1:3112/
Bash  chrome-devtools-axi open http://127.0.0.1:3112/ 2>&1 | tail -20
Bash  chrome-devtools-axi screenshot --out /tmp/expiry-form.png 2>&1 | tail -3
Read  /tmp/expiry-form.png
Bash  chrome-devtools-axi fill @g360:23_6 "https://example.com/a/genuinely/long/campaign?utm_source=newsletter" 2>&1 | tail -4
Bash  chrome-devtools-axi snapshot 2>&1 | grep -E "textbox|spinbutton \"Month|button \"Shorten" | head -6
Bash  chrome-devtools-axi --help 2>&1 | head -40
```

**Assistant**

Another worker is sharing the default browser session; switching to an isolated one.

```text
Bash  export CHROME_DEVTOOLS_AXI_SESSION=orban-b-expiry; chrome-devtools-axi open http://127.0.0.1:3112/ 2>&1 | grep -E "textbox|Expiry|button" | head -10
Bash  export CHROME_DEVTOOLS_AXI_SESSION=orban-b-expiry; chrome-devtools-axi fill @g1:1_6 "https://example.com/a/genuinely/long/campaign?utm_source=newsletter" 2>&1 | tail -2; chrome-devtools-axi fillform @g1:1_8=2027-03-01T09:30 2>&1 | tail -3
Bash  export CHROME_DEVTOOLS_AXI_SESSION=orban-b-expiry; U=$(chrome-devtools-axi snapshot 2>&1 | grep 'DateTime "Expiry"' | sed 's/.*uid=\([^ ]*\).*/\1/'); echo "uid=$U"; chrome-devtools-axi fillform @$U=2027-03-01T09:30 2>&1 | tail -4
Bash  export CHROME_DEVTOOLS_AXI_SESSION=orban-b-expiry; chrome-devtools-axi eval '() => ({ destination: document.getElementById("destination").value, expiry: document.getElementById("expires-at").value })' 2>&1 | tail -5
Bash  export CHROME_DEVTOOLS_AXI_SESSION=orban-b-expiry; B=$(chrome-devtools-axi snapshot 2>&1 | grep 'button "Shorten"' | sed 's/.*uid=\([^ ]*\).*/\1/'); chrome-devtools-axi click @$B 2>&1 | grep -iE "short|stops|alert|goes" | head -12
Bash  export CHROME_DEVTOOLS_AXI_SESSION=orban-b-expiry; chrome-devtools-axi screenshot --out /tmp/expiry-result.png 2>&1 | tail -2
Read  /tmp/expiry-result.png
```

**Assistant**

The result card shows no expiry line - the earlier `fillform` set the DOM value without notifying React. Re-running with a real React-visible change:

```text
Bash  export CHROME_DEVTOOLS_AXI_SESSION=orban-b-expiry; D=$(chrome-devtools-axi snapshot 2>&1 | grep 'textbox "Destination"' | sed 's/.*uid=\([^ ]*\).*/\1/'); chrome-devtools-axi fill @$D "https://example.com/limited-time-campaign" >/dev/null 2>&1; chrome-devtools-axi eval '() => { const el = document.ge ...
Bash  export CHROME_DEVTOOLS_AXI_SESSION=orban-b-expiry; B=$(chrome-devtools-axi snapshot 2>&1 | grep 'button "Shorten"' | sed 's/.*uid=\([^ ]*\).*/\1/'); chrome-devtools-axi click @$B >/dev/null 2>&1; chrome-devtools-axi wait 1200 >/dev/null 2>&1; chrome-devtools-axi eval '() => document.querySelector(". ...
Bash  curl -s -i -o - "http://127.0.0.1:8112/u5ODjHc" | head -4; echo "--- unknown:"; curl -s -i "http://127.0.0.1:8112/nosuchX" | head -4
Bash  export CHROME_DEVTOOLS_AXI_SESSION=orban-b-expiry; D=$(chrome-devtools-axi snapshot 2>&1 | grep 'textbox "Destination"' | sed 's/.*uid=\([^ ]*\).*/\1/'); chrome-devtools-axi fill @$D "https://example.com/already-over" >/dev/null 2>&1; chrome-devtools-axi eval '() => { const el = document.getElementB ...
Bash  export CHROME_DEVTOOLS_AXI_SESSION=orban-b-expiry; chrome-devtools-axi screenshot --out /tmp/expiry-past-error.png 2>&1 | tail -1
Read  /tmp/expiry-past-error.png
Bash  export CHROME_DEVTOOLS_AXI_SESSION=orban-b-expiry; chrome-devtools-axi eval '() => { const el = document.getElementById("expires-at"); return { ariaInvalid: el.getAttribute("aria-invalid"), describedBy: el.getAttribute("aria-describedby"), border: getComputedStyle(el).borderColor }; }' 2>&1 | grep r ...
Bash  ../.venv/bin/python - <<'EOF' import json, time, urllib.request from datetime import datetime, timedelta, timezone def call(path, data=None, key=False): req = urllib.request.Request("http://127.0.0.1:8112" + path, method="POST" if data else "GET") if key: req.add_header("X-API-Key", "local-dev-key") ...
Bash  cd .. && git add frontend/app/shorten-view.tsx frontend/app/globals.css && git status --short && git commit -q -F - <<'EOF' Offer expiry as an optional field in the interface The creation form takes a moment in the sharer's own timezone and sends it as an instant, so the link stops working when they ...
Bash  export CHROME_DEVTOOLS_AXI_SESSION=orban-b-expiry; chrome-devtools-axi stop 2>&1 | tail -2; pkill -f "uvicorn backend.main:app --port 8112"; pkill -f "next dev --port 3112"; sleep 1 2>/dev/null; echo stopped
Bash  .venv/bin/python -m pytest 2>&1 | tail -4; .venv/bin/python -m mypy backend --ignore-missing-imports 2>&1 | tail -2; git status --short
Bash  echo "working: expiry built and validated end to end, running /code-review" >> '~/firstmate/state/orban-b-expiry.status'; git fetch origin main 2>/dev/null; git log --oneline main -1 2>/dev/null; git merge-base --is-ancestor main HEAD && echo "branch is a fast-forward onto main"
```

**Assistant**

Now the review.

```text
Skill  /code-review
Bash   cd .. && git rev-parse main && git log main..HEAD --oneline && echo "--- diffstat" && git diff main...HEAD --stat
Agent  Standards review of expiry diff (general-purpose)
Agent  Spec review of expiry diff (general-purpose)
```

**Assistant**

Both reviews are back. Acting on the findings worth acting on:

```text
Edit  project-b-ai-assisted/tests/conftest.py
Edit  project-b-ai-assisted/tests/conftest.py
Bash  cd project-b-ai-assisted 2>/dev/null || cd <repo>/project-b-ai-assisted; python3 - <<'EOF' import re, pathlib p = pathlib.Path("tests/test_expiry.py") text = p.read_text() text = text.replace('''from backend.clock import clock from tests.test_redirect''', '''from tests.test_redirect''') text = text. ...
Bash  python3 - <<'EOF' import pathlib p = pathlib.Path("tests/test_expiry.py") text = p.read_text() text = text.replace('''def shorten_until(client, expiry, destination=A_DESTINATION): return client.post( "/short-links", json={"destination": destination, "expires_at": expiry}, )''', '''def shorten_until( ...
```

**Assistant**

Now the naming and the duplicated error envelope:

```text
Edit  project-b-ai-assisted/backend/repository.py
Edit  project-b-ai-assisted/backend/repository.py
Edit  project-b-ai-assisted/backend/repository.py
Edit  project-b-ai-assisted/backend/errors.py
Edit  project-b-ai-assisted/backend/errors.py
Edit  project-b-ai-assisted/backend/errors.py
Bash  python3 - <<'EOF' import pathlib p = pathlib.Path("backend/routes.py") text = p.read_text() text = text.replace('''from .errors import ( CODE_SHORT_CODE_UNAVAILABLE, CODE_VALIDATION_ERROR, ApiError, ErrorResponse, FieldError, )''', '''from .errors import ( CODE_SHORT_CODE_UNAVAILABLE, CODE_VALIDATIO ...
Edit  project-b-ai-assisted/backend/routes.py
Bash  .venv/bin/python -m pytest 2>&1 | tail -3; .venv/bin/python -m mypy backend --ignore-missing-imports 2>&1 | tail -2; awk 'length > 88 {print FILENAME": "FNR": "length}' backend/*.py tests/*.py
Bash  git stash list >/dev/null; sed -n '53,57p' backend/errors.py; git diff main...HEAD -- backend/errors.py | head -30
Bash  python3 - <<'EOF' import pathlib p = pathlib.Path("tests/test_expiry.py") text = p.read_text() text = text.replace( "def test_a_short_link_without_an_expiry_still_resolves_years_later(client, scripted_clock):", "def test_a_short_link_without_an_expiry_still_resolves_years_later(\n client, scripted_c ...
Bash  git diff --stat && git add -A backend tests && git status --short && git commit -q -F - <<'EOF' Take the review notes on the expiry seam Moving the clock override into a conftest fixture puts it beside the Short Code override it mirrors, so the two ways a test steers the application do not drift apa ...
```

**Assistant**

Now the report:

```text
Write  ~/firstmate/data/orban-b-expiry/report.md
Bash   cd .. && git fetch . main >/dev/null 2>&1; git log --oneline main -1; git merge-base --is-ancestor main HEAD && echo "fast-forward: yes"; git status --short; echo "--- full suite once more"; cd project-b-ai-assisted && .venv/bin/python -m pytest 2>&1 | tail -2
```

**Assistant**

main has advanced; rebasing to keep the merge a fast-forward.

```text
Bash  cd .. && git log --oneline 69f4bf9..main && echo "--- files touched by those commits:" && git diff --stat 69f4bf9..main
Bash  cd .. && git rebase main 2>&1 | tail -3 && git log --oneline -5 && git merge-base --is-ancestor main HEAD && echo "fast-forward: yes"
Bash  git rebase main 2>&1 | tail -3; git log --oneline -5; git merge-base --is-ancestor main HEAD && echo "fast-forward: yes"
Bash  cd <repo>/project-b-ai-assisted && .venv/bin/python -m pytest 2>&1 | tail -2 && .venv/bin/python -m mypy backend --ignore-missing-imports 2>&1 | tail -1 && git status --short
Bash  python3 - <<'EOF' import pathlib p = pathlib.Path("~/firstmate/data/orban-b-expiry/report.md") text = p.read_text() text = text.replace( "Branch: `fm/orban-b-expiry` (4 commits on top of `main` at 69f4bf9), project `project-b-ai-assisted`.", "Branch: `fm/orban-b-expiry` (4 commits, rebased onto `mai ...
Bash  echo "done: ready in branch fm/orban-b-expiry" >> '~/firstmate/state/orban-b-expiry.status'; git log --oneline -4
```

**Assistant**

Ticket #12 is built and committed on `fm/orban-b-expiry`, rebased onto current `main` (a72035f) so the merge stays a fast-forward.

**What shipped** (all inside `project-b-ai-assisted/`):

- `backend/clock.py` - an injectable clock, mirroring the existing `short_code_source` provider. One clock decides both whether a creation is accepted and whether a Short Link still resolves.
- Creation takes an optional `expires_at`. It must carry a timezone (a browser's `datetime-local` yields a naive string, and reading that as UTC would shift the expiry by the sharer's own offset), and a past moment is refused 422 naming `expires_at`.
- The expiry predicate lives inside the lookup SQL, so an expired Short Link is simply not found: same 404, same body, same headers as a Short Code that never existed, per ADR 0003. Nothing downstream of the lookup can count against one either.
- The creation form offers expiry as an optional field with a hint, shows a refusal against the field, and names the moment the link stops working in the sharer's own locale.

**Validation**: 35 tests pass (12 new), `mypy backend` and `tsc --noEmit` clean. Beyond the suite I ran the real pair and confirmed a two-second expiry resolved before its moment and afterwards answered byte-identically to an unknown code, and drove the form in a browser for both the success and past-expiry paths.

**Review**: `/code-review main` ran both axes. I acted on four findings (clock override moved to a `conftest` fixture beside `scripted_short_codes`, deduplicated the 422 message via a shared constant, three renames, one unused parameter) and deliberately left six with reasons - the notable ones being the injected clock as a second test seam, expiry treated as an exclusive bound, and no migration for a pre-existing database. Full write-up in `~/firstmate/data/orban-b-expiry/report.md`.

One thing outside the ticket, flagged not fixed: `npm install` warns `next@15.1.3` carries CVE-2025-66478. A framework bump isn't this ticket and `package.json` is shared with the five other workers currently in this repo.
