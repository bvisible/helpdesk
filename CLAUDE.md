<!-- //// Neoffice — added file (no upstream equivalent): the branch and build
     //// conventions of THIS fork for Claude Code sessions. Upstream has no such
     //// file, so nothing here ever conflicts; at the merge, keep ours whole.
     //// (Ironically this file was meant to be gitignored — see the defect noted
     //// on desk/stats.htmlCLAUDE.md in .gitignore.) -->

# Git Configuration

## Branche de production
- **Branche:** `version-15`
- **Remote:** `origin` (bvisible)

## Build pipeline (commit-the-build)

⚠️ **Ne jamais lancer `yarn build` ou `bench build --app helpdesk` localement sur un serveur Neoffice** (4 GB RAM → OOM-kill garanti). Le build se fait UNIQUEMENT sur GitHub Actions (ubuntu-latest, 16 GB RAM).

### Comment ça marche

1. Modif d'un fichier source (`desk/...`) en local → `git commit` → `git push origin version-15`. **Ne pas builder localement.**
2. Le workflow `.github/workflows/build-frontend.yml` détecte le push, lance `yarn build` sur ubuntu-latest (~1-2 min) et commit les artefacts back avec un commit `[skip-build] frontend artifacts for <SHA>` (par `github-actions[bot]`).
3. Sur les instances clients, le pipeline d'update fait `git pull` (ramène ton commit + le commit du bot). Quand `bench build --app helpdesk` tourne, il appelle `yarn build` à la racine — **le `package.json` voit les artefacts déjà présents et skip vite** (gate). Plus d'OOM-kill.

### Paths spécifiques

- **Source frontend** : `desk/`
- **Artefacts vite (commités)** : `helpdesk/public/desk/`
- **SPA HTML(s) (commités)** : `helpdesk/www/helpdesk/index.html`
- **Build script root** : `yarn workspace (`cd desk && yarn build`, frontend dans `desk/`)`

### Forcer un rebuild local (si vraiment nécessaire)

```bash
FORCE_REBUILD=1 yarn build
```

### Documentation complète

- Doc canonique : `bvisible/neoffice-devops:main` → `docs/COMMIT-BUILD-PATTERN.md`
- Doc batch migration (12 apps) : même fichier, sections "Apps that have adopted the pattern" + "Edge cases discovered"
- Vault Obsidian : `[[NORA/04-savoir-faire/drive-frontend-build-pattern]]`

### Edge cases spécifiques à helpdesk

- ⚠️ Frontend dans `desk/` (pas `frontend/`), artefacts dans `public/desk/`, SPA HTML dans `www/helpdesk/index.html` (sub-folder).
- **socket.ts**: pattern window-fallback (sync, `window.socketio_port || "9000"`) — `export const socket = initSocket()` top-level oblige à garder sync.
- **telemetry.ts**: import `posthog.js` retiré (commit `86671e31`).
- App pas installée par défaut sur Osiris. Sur nouvelles instances, elle est dans `Required App` (install_order 90).
