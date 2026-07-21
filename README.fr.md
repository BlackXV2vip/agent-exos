<p align="center">
  <a href="https://exos-agent.ai">
    <picture>
      <source srcset="packages/console/app/src/asset/logo-ornate-dark.svg" media="(prefers-color-scheme: dark)">
      <source srcset="packages/console/app/src/asset/logo-ornate-light.svg" media="(prefers-color-scheme: light)">
      <img src="packages/console/app/src/asset/logo-ornate-light.svg" alt="Logo Exos Agent">
    </picture>
  </a>
</p>
<p align="center">L'agent de codage IA open source.</p>
<p align="center">
  <a href="https://exos-agent.ai/discord"><img alt="Discord" src="https://img.shields.io/discord/1391832426048651334?style=flat-square&label=discord" /></a>
  <a href="https://www.npmjs.com/package/exos-agent"><img alt="npm" src="https://img.shields.io/npm/v/exos-agent?style=flat-square" /></a>
  <a href="https://github.com/BlackXV2vip/agent-exos/actions/workflows/publish.yml"><img alt="Build status" src="https://img.shields.io/github/actions/workflow/status/BlackXV2vip/agent-exos/publish.yml?style=flat-square&branch=dev" /></a>
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh.md">简体中文</a> |
  <a href="README.zht.md">繁體中文</a> |
  <a href="README.ko.md">한국어</a> |
  <a href="README.de.md">Deutsch</a> |
  <a href="README.es.md">Español</a> |
  <a href="README.fr.md">Français</a> |
  <a href="README.it.md">Italiano</a> |
  <a href="README.da.md">Dansk</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.pl.md">Polski</a> |
  <a href="README.ru.md">Русский</a> |
  <a href="README.bs.md">Bosanski</a> |
  <a href="README.ar.md">العربية</a> |
  <a href="README.no.md">Norsk</a> |
  <a href="README.br.md">Português (Brasil)</a> |
  <a href="README.th.md">ไทย</a> |
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a> |
  <a href="README.bn.md">বাংলা</a> |
  <a href="README.gr.md">Ελληνικά</a> |
  <a href="README.vi.md">Tiếng Việt</a>
</p>

[![Exos Agent Terminal UI](packages/web/src/assets/lander/screenshot.png)](https://exos-agent.ai)

---

### Installation

```bash
# YOLO
curl -fsSL https://exos-agent.ai/install | bash

# Gestionnaires de paquets
npm i -g exos-agent@latest        # ou bun/pnpm/yarn
scoop install exos-agent             # Windows
choco install exos-agent             # Windows
brew install BlackXV2vip/tap/exos-agent # macOS et Linux (recommandé, toujours à jour)
brew install exos-agent              # macOS et Linux (formule officielle brew, mise à jour moins fréquente)
sudo pacman -S exos-agent            # Arch Linux (Stable)
paru -S exos-agent-bin               # Arch Linux (Latest from AUR)
mise use -g exos-agent               # n'importe quel OS
nix run nixpkgs#exos-agent           # ou github:BlackXV2vip/agent-exos pour la branche dev la plus récente
```

> [!TIP]
> Supprimez les versions antérieures à 0.1.x avant d'installer.

### Application de bureau (BETA)

Exos Agent est aussi disponible en application de bureau. Téléchargez-la directement depuis la [page des releases](https://github.com/BlackXV2vip/agent-exos/releases) ou [exos-agent.ai/download](https://exos-agent.ai/download).

| Plateforme            | Téléchargement                     |
| --------------------- | ---------------------------------- |
| macOS (Apple Silicon) | `exos-agent-desktop-mac-arm64.dmg`   |
| macOS (Intel)         | `exos-agent-desktop-mac-x64.dmg`     |
| Windows               | `exos-agent-desktop-windows-x64.exe` |
| Linux                 | `.deb`, `.rpm`, ou AppImage        |

```bash
# macOS (Homebrew)
brew install --cask exos-agent-desktop
# Windows (Scoop)
scoop bucket add extras; scoop install extras/exos-agent-desktop
```

#### Répertoire d'installation

Le script d'installation respecte l'ordre de priorité suivant pour le chemin d'installation :

1. `$EXOS_AGENT_INSTALL_DIR` - Répertoire d'installation personnalisé
2. `$XDG_BIN_DIR` - Chemin conforme à la spécification XDG Base Directory
3. `$HOME/bin` - Répertoire binaire utilisateur standard (s'il existe ou peut être créé)
4. `$HOME/.exos-agent/bin` - Repli par défaut

```bash
# Exemples
EXOS_AGENT_INSTALL_DIR=/usr/local/bin curl -fsSL https://exos-agent.ai/install | bash
XDG_BIN_DIR=$HOME/.local/bin curl -fsSL https://exos-agent.ai/install | bash
```

### Agents

Exos Agent inclut deux agents intégrés que vous pouvez basculer avec la touche `Tab`.

- **build** - Par défaut, agent avec accès complet pour le travail de développement
- **plan** - Agent en lecture seule pour l'analyse et l'exploration du code
  - Refuse les modifications de fichiers par défaut
  - Demande l'autorisation avant d'exécuter des commandes bash
  - Idéal pour explorer une base de code inconnue ou planifier des changements

Un sous-agent **general** est aussi inclus pour les recherches complexes et les tâches en plusieurs étapes.
Il est utilisé en interne et peut être invoqué via `@general` dans les messages.

En savoir plus sur les [agents](https://exos-agent.ai/docs/agents).

### Documentation

Pour plus d'informations sur la configuration d'Exos Agent, [**consultez notre documentation**](https://exos-agent.ai/docs).

### Contribuer

Si vous souhaitez contribuer à Exos Agent, lisez nos [docs de contribution](./CONTRIBUTING.md) avant de soumettre une pull request.

### Construire avec Exos Agent

Si vous travaillez sur un projet lié à Exos Agent et que vous utilisez "exos-agent" dans le nom du projet (par exemple, "exos-agent-dashboard" ou "exos-agent-mobile"), ajoutez une note dans votre README pour préciser qu'il n'est pas construit par l'équipe Exos Agent et qu'il n'est pas affilié à nous.

---

**Rejoignez notre communauté** [Discord](https://discord.gg/exos-agent) | [X.com](https://x.com/exos-agent)
