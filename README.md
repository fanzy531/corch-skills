# corch-skills

Codex skills for the c-lab content community ecosystem.

## Quick install

```bash
# One-line setup (installs all skills + dependencies)
curl -sL https://raw.githubusercontent.com/fanzy531/corch-skills/main/scripts/setup.sh | bash
```

Or one by one:

```bash
codex skill install fanzy531/corch-skills --path skills/corch-digest/SKILL.md
codex skill install fanzy531/corch-skills --path skills/corch-action/SKILL.md
codex skill install fanzy531/corch-skills --path skills/corch-hub/SKILL.md
```

## Skills

| Skill | Description | CPT |
|---|---|---|
| **corch-digest** | Read, digest, rewrite articles from URLs, publish to WordPress | voice（他山之石）|
| **corch-action** | Parse structured markdown projects, publish to WordPress | action（实践现场）|
| **corch-hub** | Query C-Hub knowledge base for community placemaking knowledge | — |

## Dependencies

System packages (installed by setup script):
- `Pillow` — image compression (pip)
- `poppler` — PDF text & image extraction (brew)
- `markitdown` — document format conversion (Codex skill)

## Project structure

```
corch-skills/
├── .skill-requirements.json    # Manifest for one-click install
├── CHANGELOG.md
├── scripts/
│   └── setup.sh                # Auto-installer
└── skills/
    ├── corch-digest/            # v1.5.1
    ├── corch-action/            # v0.3.0
    └── corch-hub/
```
