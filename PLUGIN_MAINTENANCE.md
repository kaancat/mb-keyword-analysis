# Plugin Maintenance Guide

## Plugin Locations

| Location | Path | Purpose |
|----------|------|---------|
| **Source** | `/Users/kaancatalkaya/Desktop/Plugins/mb-keyword-analysis/` | Where you edit code |
| **Marketplace** | `~/.claude/plugins/marketplaces/mb-plugins/.claude-plugin/marketplace.json` | Version registry |
| **Cache** | `~/.claude/plugins/cache/mb-plugins/mb-keyword-analysis/{version}/` | Installed version |

---

## Key Files to Edit

| File | Purpose |
|------|---------|
| `skills/keyword-analysis/SKILL.md` | Main workflow methodology |
| `templates/presentation_template.html` | HTML presentation output |
| `hooks/rules/*.md` | Validation hooks |
| `CLAUDE.md` | Plugin usage instructions |
| `.claude-plugin/plugin.json` | Plugin metadata & version |
| `schemas/*.json` | Deliverable validation schemas |

---

## Push Workflow

### 1. Make changes and commit

```bash
cd /Users/kaancatalkaya/Desktop/Plugins/mb-keyword-analysis
git add .
git commit -m "feat: description of changes"
git push origin main
```

### 2. Bump version in plugin.json

Edit `.claude-plugin/plugin.json`:
```json
{
  "version": "X.Y.Z"
}
```

### 3. Commit version bump

```bash
git add . && git commit -m "chore: bump to X.Y.Z" && git push
```

### 4. Update marketplace to match

Edit `~/.claude/plugins/marketplaces/mb-plugins/.claude-plugin/marketplace.json`:
- Find the `mb-keyword-analysis` entry
- Change version to `"X.Y.Z"`

### 5. Push marketplace

```bash
cd ~/.claude/plugins/marketplaces/mb-plugins
git add . && git commit -m "chore: bump mb-keyword-analysis to X.Y.Z" && git push
```

### 6. Restart Claude Code

The new version will be fetched on next session start.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.4.3 | 2026-01-21 | **FEATURE: Branding support** - client logo, agency logo in footer, email CTA support via brand.json |
| 1.4.2 | 2026-01-21 | **FIX: Presentation bugs** - inline **bold** markdown now renders, URL overflow fixed in ad preview |
| 1.3.5 | 2026-01-11 | **FIX: Q9-Q10 now in commands/keyword-analysis.md** - service validation questions in discovery flow |
| 1.3.4 | 2026-01-11 | Discovery UI flow table in SKILL.md (didn't fix question issue) |
| 1.3.3 | 2026-01-11 | Created discovery_brief.md template |
| 1.3.2 | 2026-01-11 | Quality assurance: service validation, Q9-Q13, Phase 3.5, negative keywords schema |
| 1.3.1 | - | Previous stable |
| 1.3.0 | - | Standalone plugin with central credentials |

---

## GitHub Repository

https://github.com/kaancat/mb-keyword-analysis.git
