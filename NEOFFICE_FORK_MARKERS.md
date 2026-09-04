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
`build-frontend` workflow on every push touching `desk/**` and must never be hand-edited —
a marker written into them dies at the next build.

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

### Known defects recorded while marking (NOT fixed here)

1. `.gitignore:42` — `desk/stats.htmlCLAUDE.md`. Commit `b713b86fd "chore: add CLAUDE.md to
   gitignore"` appended `CLAUDE.md` to a file that had no trailing newline, welding it onto
   the previous entry. Net effect: **neither `desk/stats.html` nor `CLAUDE.md` is ignored**
   — and `CLAUDE.md` is in fact committed in this repo, which is what the commit meant to
   prevent.
2. `frappe-ui` submodule rolled back 27 releases inside an unrelated commit (table above).
