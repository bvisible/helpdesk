# Neoffice fork markers

Map of everything this fork changes relative to its upstream parent, so that the next
upstream merge can tell OUR intent from theirs. `grep -rn "////"` gives the complete
picture for every file that can carry a comment; this file carries what cannot
(JSON, binaries, build artifacts, submodule pointers, whitespace-only drift).

## helpdesk

**Fork**: `bvisible/helpdesk`, branch `version-15`
**Upstream**: `frappe/helpdesk` (default branch `develop`; `main` / `main-hotfix` are the
release branches, `legacy` the archived v0 line — there is no `upstream/version-15`).

### Base of the divergence

```
BASE = 33785829c10b826e834fb092135625023e00da97
     = "Merge pull request #2951 from aerodeval/fix/posthog-issue"
       Shariq Ansari, 2026-01-28, on upstream/develop
```

The branch name lies about the base, as usual: our `version-15` is **not** a fork of an
upstream `version-15` (none exists) — it is `upstream/develop` cut at 2026-01-28 plus our
own commits. Establishing it:

| upstream branch | tip contained in ours? | merge-base with `origin/version-15` | our commits since |
|---|---|---|---|
| `develop` (9b1023c86) | no (2170 commits ahead) | **33785829c1** (2026-01-28) | **32** |
| `main` (1c3361cc0) | no (2608 ahead) | 536d06681f (2025-09-16) | 936 |
| `main-hotfix` (893a3f178) | no (2602 ahead) | 536d06681f (2025-09-16) | 936 |
| `legacy` (602cacdea) | **yes** — but 3885 commits behind (2023-03-26) | itself | 3885 |

`legacy` is contained but is an archived 2023 branch that would attribute 3853 upstream
commits to us; the correct base is the merge-base with `develop`, which is the most recent
upstream commit reachable from our history.

### Attribution proof

```
git rev-list --count origin/version-15 ^BASE                                       -> 32
git rev-list --count origin/version-15 ^BASE ^upstream/develop ^upstream/main \
                                       ^upstream/main-hotfix                       -> 32
git log --format=%an origin/version-15 ^BASE | sort -u
    -> Jeremy, Jérémy Christillin, github-actions[bot]      (no upstream author)
git log --merges origin/version-15 ^BASE                    -> (empty, no merge commits)
grep -c "cherry picked from commit" over those 32 commits   -> 0  (no upstream backport)
```

`git blame` (no `-w`) on a sample of unmarked hunks — `helpdesk/search.py:124`,
`helpdesk/helpdesk/utils/email.py:34`, `helpdesk/helpdesk/doctype/hd_ticket/hd_ticket.py:507`,
`desk/src/socket.ts:12`, `pyproject.toml:7` — points at `0d407a9773`, `87dd854474`,
`8fc1e754b8`, `cc1dba969a`, `856197c286`: all ours. The 32 commits are exactly our
divergence, nothing of upstream's is attributed to us.

### Non-commentable files we changed

| Path | What we changed | Why | At the merge |
|---|---|---|---|
| `package.json` | `build` script wrapped in a guard (`[skip-build]` when `helpdesk/public/desk/assets` exists, unless `FORCE_REBUILD=1`); real build moved to `build:force` | `bench build` used to run `yarn build` on every instance and OOM-killed the 4 GB tenants. Commit-the-build: the SPA is compiled by the `build-frontend` GitHub workflow and committed; instances only pull. | keep ours, re-apply on top of upstream's script |
| `desk/package.json` | `dev` / `build` prefixed with `NODE_OPTIONS=--max-old-space-size=2048/4096` | vite runs out of Node heap on small builders | keep ours |
| `helpdesk/public/desk/manifest.webmanifest` | added (build artifact) | see "Build artifacts" below | take upstream / rebuild |
| `helpdesk/public/desk/sw.js.map` | added (build artifact) | see "Build artifacts" below | take upstream / rebuild |
| `helpdesk/locale/fr.po` | 13 `msgid` added (FR) | strings of our own additions: the acknowledgement subject `Ticket #{0}: We've received your request` and the NORA reply-suggestion dialog (`Suggested reply`, `Draft — reread before sending`, `NORA is writing…`, `Use this reply`, `Regenerate`, `Suggest a reply`, `Could not draft a reply`, `Your reply already contains text — it will be replaced.`, `Append`, `Replace`, `Instruction (optional)`, `e.g. explain the delay and offer a call`) | merge both sides; ours are additions only, no upstream `msgid` was retranslated |

**No JSON DocType is modified.** The fork adds no field and changes no DocType schema —
nothing here needs to become a Custom Field.

### Submodule pointer (unreachable — no comment syntax at all)

| Path | Ours | Upstream at BASE | Note |
|---|---|---|---|
| `frappe-ui` (gitlink, `.gitmodules` → `frappe/frappe-ui`) | `3d0c58a03c342bc64db55684e1c31ddacc9ff017` = **v0.1.232, 2025-12-04** | `a302a61dc32bfe1e868412f67dad6f7ca144254d` = v0.1.259, 2026-01-19 | **This is a rollback, not an upgrade**, and it rode along inside `8fc1e754b8 "fix: use received communications to determine reply email account"` — a commit about email accounts. Almost certainly a stale local submodule checkout committed by accident. **At the merge: take upstream's pointer.** A gitlink cannot carry a comment and `git show HEAD:frappe-ui` is not a blob, so `fork_markers.py check` will always report this hunk. |

### Build artifacts (commit-the-build) — mark the SOURCE, never the artifact

Since `cc1dba969a` (2026-05-07) this fork commits its compiled SPA so that instances pull
it instead of rebuilding (4 GB tenants OOM on `yarn build`). The `.gitignore` change that
un-ignores them carries the marker; the artifacts themselves are regenerated by the
`build-frontend` workflow on every push touching `desk/**` and must never be hand-edited.
`desk/vite.config.js` sets `outDir: ../helpdesk/public/desk` with **`emptyOutDir: true`**
and `indexHtmlPath: ../helpdesk/www/helpdesk/index.html`: every build wipes that directory
and rewrites that file, so a marker written into any of them is guaranteed to be erased.

| Artifact | Source that carries the marker |
|---|---|
| `helpdesk/public/desk/**` (assets/, manifest/, videos/, images, `sw.js`, `workbox-*.js`, `registerSW.js`) | `.gitignore` + `desk/**` |
| `helpdesk/public/desk/index.html` | `desk/index.html` (unmodified) + `.gitignore` |
| `helpdesk/public/desk/favicon.svg` | `desk/public/favicon.svg` (unmodified) |
| `helpdesk/www/helpdesk/index.html` | generated copy of `helpdesk/public/desk/index.html`; `.gitignore` |

`fork_markers.py` skips `**/assets/**` and the hashed chunks on its own, but still reports
these three (their `.html` / `.svg` extension looks commentable to it):
`helpdesk/public/desk/index.html`, `helpdesk/public/desk/favicon.svg`,
`helpdesk/www/helpdesk/index.html`. **They are artifacts — expected, do not mark them.**

**At the merge**: drop all of `helpdesk/public/desk/` and `helpdesk/www/helpdesk/index.html`
from the conflict resolution and let the workflow rebuild them from the merged sources.

### Files we added (no upstream equivalent)

| Path | Purpose |
|---|---|
| `desk/src/components/NeoCockpitBridge.vue` | mounts the shared Neoffice chrome (the `frappe-sidebar-react` IIFE bundle) inside the Vue SPA |
| `desk/src/components/NeoCockpitHDSidebar.vue` | NeoCockpit as the Helpdesk sidebar, with upstream's `Sidebar.vue` as the fallback |
| `desk/src/components/NeoSuggestReplyDialog.vue` | NORA reply-suggestion dialog (read-only towards the ticket) |
| `CLAUDE.md` | branch/build conventions of this fork for Claude Code sessions |
| `.github/workflows/build-frontend.yml` | commit-the-build pipeline |
| `.github/workflows/tests.yml` | fleet CI caller (`bvisible/neoffice-ci`) |
| `.github/workflows/upstream-preview.yml` | weekly bench on upstream `frappe`/`erpnext` (tracker #138) |
| `.github/workflows/fork-markers.yml` | this discipline, enforced on every push |

`.github/**` is skipped by `fork_markers.py` by design (a marker added there would be
counted as a non-comment addition); the four workflows are ours in full and carry their
own header comment.

### Merge forecast (measured 2026-09-04 against `upstream/develop` = 9b1023c86)

Upstream is **2170 commits** ahead of BASE and has touched **628 files**; we touched 25
(artifacts excluded). The intersection is 14 files — those are the whole conflict surface:

| File | upstream churn since BASE | expected at the merge |
|---|---|---|
| `desk/src/components/EmailEditor.vue` | 529+/219−, 73 commits | **hard conflict**. Our NORA button + `applyNeoSuggestion` are additions in a heavily rewritten file. Re-apply by hand from the markers. |
| `helpdesk/helpdesk/doctype/hd_ticket/hd_ticket.py` | 486+/261−, 88 commits | **hard conflict**, and one trap: upstream now writes `subject=_("Ticket #{0}: We've received your request").format(self.name)` — the same line as ours **minus `lang=self.reply_language()`**. Taking upstream there silently re-breaks the language in workers. |
| `desk/vite.config.js` | 138+/81−, 23 commits | conflict on the `build` block; keep ours, it is a memory constraint of our runners. |
| `desk/src/index.css` | 163+/1−, 25 commits | trivial: ours is appended at the end, re-append after upstream's file. |
| `desk/src/components/CommunicationArea.vue` | 122+/75−, 17 commits | one-line conflict on the `onClickOutside` `ignore` list. |
| `desk/src/telemetry.ts` | 4+/88−, 2 commits | **take upstream whole** — it rewrote the file around `useTelemetry` and dropped the posthog import itself. Our change is spent. |
| `helpdesk/search.py` | 8+/38−, 5 commits | upstream removed HD Ticket from the Redis index (tickets moved to `search_sqlite.py`); the Article index remains, so our idempotent `create_index` / `drop_index` still apply. Keep ours. |
| `desk/package.json` | 14+/5−, 23 commits | keep our `NODE_OPTIONS` prefixes. |
| `package.json` | 2+/5−, 4 commits | keep our `[skip-build]` guard + `build:force`. |
| `pyproject.toml` | 12+/1−, 8 commits | keep `requires-python = ">=3.10"` until the fleet moves to 3.14. |
| `.gitignore` | 6+/0−, 5 commits | keep our un-ignores; take the chance to fix the `desk/stats.htmlCLAUDE.md` defect. |
| `desk/src/components/layouts/DesktopLayout.vue` | 2+/3−, 2 commits | small conflict on the `<Sidebar />` swap. |
| `helpdesk/locale/fr.po` | (locale) | merge both sides, ours are additions only. |
| `frappe-ui` | submodule | **take upstream's pointer** (ours is a rollback, see above). |

`desk/src/socket.ts` and `helpdesk/helpdesk/utils/email.py` are untouched upstream since
BASE (0 commits): they merge clean.

### Known defects recorded while marking (NOT fixed here)

1. `.gitignore:58` — `desk/stats.htmlCLAUDE.md`. Commit `b713b86fd "chore: add CLAUDE.md to
   gitignore"` appended `CLAUDE.md` to a file that had no trailing newline, welding it onto
   the previous entry. Net effect: **neither `desk/stats.html` nor `CLAUDE.md` is ignored**
   — and `CLAUDE.md` is in fact committed in this repo, which is what the commit meant to
   prevent.
2. `frappe-ui` submodule rolled back 27 releases inside an unrelated commit (table above).
3. `helpdesk/search.py:227` — the RediSearch < 2.0 fallback calls
   `FT.DROP <make_key(index_name)>`, but the index is created and dropped under the RAW
   name (`self.redis.ft(self.index_name)`, `index_name = "helpdesk_idx"`). The namespaced
   name is a different index, so `FT.DROP` answers "Unknown Index name" and the
   `suppress(ResponseError)` around it turns that into a silent no-op: the legacy path
   never drops anything.
4. `helpdesk/search.py:142` — `create_index()` now retries after `drop_index()`. Because
   `index_name` is NOT namespaced per site while the document `prefix` IS, two sites
   sharing one Redis (mutualised bench) share one index definition: the second site's
   rebuild now DROPS the first site's index with `delete_documents=True` instead of just
   failing as upstream did. Per-instance benches are unaffected; the shared hosts are not.
5. `helpdesk/helpdesk/utils/email.py:43` — with `enable_outgoing == 1` several support
   mailboxes can match, and `.limit(1)` has no `ORDER BY`: the account picked is whatever
   the database returns first. Upstream's `default_outgoing == 1` could only ever match
   one. Only reached as the third fallback of `sender_email()`, so latent.
6. `desk/src/components/NeoSuggestReplyDialog.vue:161-163` — the plain-text draft is turned
   into HTML by string interpolation with no escaping of `& < >`. The thread it is drafted
   from is customer-supplied, so customer text echoed by the model lands unescaped in the
   agent's editor and in the outgoing mail.
7. `desk/src/socket.ts:28` — `window.socketio_port` is set by nothing in this repo (nor by
   the SPA shell), so the `"9000"` fallback is the only value ever used. Harmless in
   production (`window.location.port` is empty, so the port is dropped), wrong anywhere the
   site is served on a port.
8. `.github/workflows/build-frontend.yml:55` — the artifact commit ends with a bare
   `git push`, no fetch/rebase and no retry. Any push landing on `version-15` while the
   build runs (a human, or the `fork-markers` bot pushing its own marker commit) makes it
   fail `! [rejected] (fetch first)` and leaves `helpdesk/public/desk/` **one build behind
   the sources**, with nothing but a red run to say so. `concurrency: cancel-in-progress`
   does not cover it: a push that misses the `paths:` filter queues no run, so it cannot
   cancel the one already building. Hit for real on 2026-09-04 during this pass.
9. French comments in code, against the English-only rule: the `//// Neoffice` markers in
   `hd_ticket.py` (l. 157-163, 552-566, 584-586, 845-852) and `CommunicationArea.vue`
   (l. 225-230),
   and the plain comments in `NeoSuggestReplyDialog.vue` (l. 14-16, 27-28, 53-55, 64).
   Not rewritten here: this pass may only ADD lines.

## Auto-marked (fork-markers workflow)

- `frappe-ui` — submodule pointer restored from `3d0c58a03` (v0.1.232, 2025-12-04) to
  `a302a61dc` (v0.1.259, 2026-01-19) — the pointer had been rolled back 27 releases as a
  stale checkout carried, unqualified, inside `8fc1e754b8` ("fix: use received
  communications to determine reply email account"), a commit about an unrelated email fix
  (4bc1b1948 "fix(submodule): frappe-ui pointer back to v0.1.259, it had been rolled back 27 releases")
