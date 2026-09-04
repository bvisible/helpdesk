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
| `frappe-ui` (gitlink, `.gitmodules` → `frappe/frappe-ui`) | `a302a61dc32bfe1e868412f67dad6f7ca144254d` = v0.1.259, 2026-01-19 (**repaired 2026-09-04**, `4bc1b1948`; was `3d0c58a03c342bc64db55684e1c31ddacc9ff017` = v0.1.232, 2025-12-04) | `a302a61dc32bfe1e868412f67dad6f7ca144254d` = v0.1.259, 2026-01-19 | **This WAS a rollback, not an upgrade** — fixed, ours and BASE now agree and there is nothing of ours to preserve on this gitlink. It had ridden along inside `8fc1e754b8 "fix: use received communications to determine reply email account"` — a commit about email accounts. Almost certainly a stale local submodule checkout committed by accident. **At the merge: take upstream's pointer** (nothing is lost, ours is BASE's). A gitlink cannot carry a comment and `git show HEAD:frappe-ui` is not a blob, so `fork_markers.py check` will always report this hunk. |

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
| `.gitignore` | 6+/0−, 5 commits | keep our un-ignores. The `desk/stats.htmlCLAUDE.md` weld is already fixed (`b7eace9e6`), so upstream's `desk/stats.html` line merges clean. |
| `desk/src/components/layouts/DesktopLayout.vue` | 2+/3−, 2 commits | small conflict on the `<Sidebar />` swap. |
| `helpdesk/locale/fr.po` | (locale) | merge both sides, ours are additions only. |
| `frappe-ui` | submodule | **take upstream's pointer** — ours is now the same commit (rollback repaired, `4bc1b1948`). |

`desk/src/socket.ts` and `helpdesk/helpdesk/utils/email.py` are untouched upstream since
BASE (0 commits): they merge clean.

### Defects found while marking — status

Recorded during the marking pass of 2026-09-04 and worked through the same day. Each line
says what was actually done and which commit did it. **Two of them were wrong diagnoses**;
they are kept here with the correction rather than deleted, because the wrong version was
written down first and someone will meet it again.

| # | Where | Status |
|---|---|---|
| 1 | `.gitignore` — `desk/stats.htmlCLAUDE.md` welded into one dead entry | **fixed**, `b7eace9e6` |
| 2 | `frappe-ui` gitlink rolled back 27 releases | **fixed**, `4bc1b1948` |
| 3 | `helpdesk/search.py:227` — legacy `FT.DROP` said to use the wrong name | **NOT FOUNDED** |
| 4 | `helpdesk/search.py:142` — index said not to be namespaced per site | **NOT FOUNDED** |
| 5 | `helpdesk/helpdesk/utils/email.py` — `LIMIT 1` with no `ORDER BY` | **fixed**, `48cd88935` |
| 6 | `NeoSuggestReplyDialog.vue` — draft interpolated into HTML unescaped | **fixed**, `82093ab0a` |
| 7 | `desk/src/socket.ts` — `window.socketio_port` read but never written | **fixed**, `8d19ec94a` |
| 8 | `.github/workflows/build-frontend.yml` — artifact push with no retry | **fixed**, `1e4259efa` |
| 9 | French `////` markers and comments in three files | **fixed**, `31534ca9f` |
| 10 | `helpdesk/www/helpdesk/index.py` — `allow_guest` gated only by a flag | **reviewed, kept**, `ac6aa3247` |

1. `.gitignore` — `b713b86fd "chore: add CLAUDE.md to gitignore"` appended `CLAUDE.md` to a
   file whose last line had no trailing newline, welding it onto the previous entry, so from
   that day **neither** path was ignored. Upstream's `desk/stats.html` is restored on its own
   line. `CLAUDE.md` stays **tracked on purpose**: it carries this fork's branch and
   commit-the-build conventions, and a clone that cannot see it cannot follow them.
2. `frappe-ui` — pointer restored to `a302a61dc` (v0.1.259), the version `desk/package.json`
   pins. The build never noticed because it resolves frappe-ui from the npm registry and
   `build-frontend.yml` checks out without submodules; only a human running `git submodule
   update` — or the next three-way merge — was misled.
3. **NOT FOUNDED.** The note claimed the RediSearch < 2.0 fallback drops a namespaced name
   while the index is created under the raw one. It is the opposite: `HelpdeskSearch.redis`
   is `frappe.cache()`, and `frappe.cache().ft(name)` returns
   `RedisearchWrapper(index_name=self.make_key(name))`, where `make_key` prefixes with
   `frappe.conf.db_name`. So `ft()` and the explicit `make_key` on line 227 speak the **same**
   name and the fallback drops the right index. `search.py` is untouched.
4. **NOT FOUNDED**, same root cause as 3: the index name IS namespaced per site, through the
   very same `make_key` as the document prefix. Two sites sharing one Redis get two distinct
   index names, and one site rebuilding cannot drop the other's. Verified 2026-09-04 in
   `frappe/utils/redis_wrapper.py` (`ft()` l. 292, `make_key()` l. 41).
5. `helpdesk/helpdesk/utils/email.py` — our widening to `enable_outgoing == 1` can match
   several support mailboxes where upstream's `default_outgoing == 1` matched at most one, and
   the `LIMIT 1` had no `ORDER BY`: the mailbox a ticket answered from was whatever the engine
   returned first. Now `ORDER BY default_outgoing DESC, name ASC`. Only the third fallback of
   `sender_email()`, so it was latent — but it is the one that runs when the two above are
   silent.
6. `NeoSuggestReplyDialog.vue` — the draft is written **from the customer's own thread**, so
   text they typed could come back through the model and reach the agent's editor and the
   outgoing mail as live markup. `& < > "` are now escaped before the `<p>`/`<br>` are built,
   `&` first so the other entities are not escaped twice.
7. `desk/src/socket.ts` — `window.socketio_port` is now emitted by `get_boot()` in
   `helpdesk/www/helpdesk/index.py`, which covers the rendered page and the dev path through
   `get_context_for_dev()` alike. **Related finding, deliberately left alone**: the
   `window.site_name = "{{ site_name }}"` line in `desk/index.html` is dead — `site_name` is
   not in the website context, so Jinja never substitutes it and the page carries the literal
   placeholder. It is harmless only because `get_boot()` overwrites the key further down the
   same page. Upstream's line; take upstream's at the merge.
8. `.github/workflows/build-frontend.yml` — the artifact step now fetches, resets onto the
   current tip, replays the built artifacts (emptyOutDir semantics preserved: a chunk this
   build no longer emits must not survive) and retries up to three times. Rebasing was
   rejected on purpose — artifacts are derived, never authored, and a rebase would only
   invite conflicts over vite's hashed chunk names.
9. French `////` markers and comments rewritten in English in `hd_ticket.py`,
   `CommunicationArea.vue` and `NeoSuggestReplyDialog.vue`. Wording only, no behaviour
   change. It matters most in `hd_ticket.py`, which the forecast above calls a hard conflict:
   a marker exists to tell the resolver our intent, and one they cannot read does not.
10. `helpdesk/www/helpdesk/index.py` — `get_context_for_dev` is `allow_guest=True` behind
    nothing but `developer_mode`. **Reviewed and kept.** `desk/src/main.js` awaits it before
    `app.mount()`, and the router guard that sends a logged-out visitor to `/login` only runs
    after the mount, so refusing Guest would leave a logged-out developer on a blank page with
    no way to sign in. What keeps it safe is the shape of the payload: `get_boot()` returns
    the caller's OWN session (its own `csrf_token`, its own `session_user`) plus site-wide
    display settings — nothing belonging to another user, no credential. That property is now
    stated next to the code, because **any key added to `get_boot()` becomes readable by an
    anonymous visitor of a developer_mode site**.

## Auto-marked (fork-markers workflow)

- `frappe-ui` — submodule pointer restored from `3d0c58a03` (v0.1.232, 2025-12-04) to
  `a302a61dc` (v0.1.259, 2026-01-19) — the pointer had been rolled back 27 releases as a
  stale checkout carried, unqualified, inside `8fc1e754b8` ("fix: use received
  communications to determine reply email account"), a commit about an unrelated email fix
  (4bc1b1948 "fix(submodule): frappe-ui pointer back to v0.1.259, it had been rolled back 27 releases")
