# Astro Plugin for Claude Code

Comprehensive Astro framework plugin providing agents, skills, hooks, and commands for building Astro-powered static sites.

## Components

### Skills (6)

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `astro` | `/astro` | Main skill - project setup, components, deployment |
| `astro-init` | `/astro-init` | Scaffold new projects with integrations |
| `astro-component` | `/astro-component` | Create components, layouts, React islands |
| `astro-deploy` | `/astro-deploy` | Deploy to GitHub Pages, Vercel, Netlify |
| `astro-i18n` | `/astro-i18n` | Internationalization setup and routing |
| `astro-content` | `/astro-content` | Content Collections schema and querying |

### Agents (4)

| Agent | Purpose |
|-------|---------|
| `astro-architect` | Architecture design, rendering strategy, integration planning |
| `astro-frontend` | UI/UX implementation, components, styles, React islands |
| `astro-devops` | Deployment, CI/CD, GitHub Actions, build optimization |
| `astro-reviewer` | Code review, performance audit, accessibility check |

### Hooks (2)

| Hook | Event | Purpose |
|------|-------|---------|
| `astro-build-check.sh` | PreToolUse | Type-check and lint before build |
| `astro-deploy-verify.sh` | PostToolUse | Verify deployed site accessibility |

### Commands (3)

| Command | Usage |
|---------|-------|
| `/astro-new` | Scaffold new Astro project |
| `/astro-build` | Build and validate site |
| `/astro-preview` | Start dev/preview server |

## Installation

### Project-level (recommended)
```bash
# Clone the plugin
git clone https://github.com/tygwan/skills.git /tmp/tygwan-skills

# Copy to your project's .claude directory
cp -r /tmp/tygwan-skills/astro/skills/*.md your-project/.claude/skills/
cp -r /tmp/tygwan-skills/astro/agents/*.md your-project/.claude/agents/
cp -r /tmp/tygwan-skills/astro/hooks/*.sh your-project/.claude/hooks/
cp -r /tmp/tygwan-skills/astro/commands/*.md your-project/.claude/commands/
```

### Global installation
```bash
cp -r /tmp/tygwan-skills/astro/ ~/.claude/skills/astro/
```

## Recommended Companion Skills

These external skills work well alongside the Astro plugin:

| Skill | Source | Purpose |
|-------|--------|---------|
| `frontend-design` | Anthropic | Production-grade UI/UX design |
| `react-expert` | jeffallan/claude-skills | React islands, hooks, TypeScript |
| `d3js-skill` | Custom | Data visualizations |
| `publishing-astro-websites` | SpillwaveSolutions | Advanced Astro patterns |

## Usage Examples

```bash
# Initialize a new portfolio site
/astro-new portfolio --template minimal --deploy github-pages

# Create a hero component
/astro-component Hero --variant brutalist

# Add i18n support
/astro-i18n --locales en,ko

# Build and deploy
/astro-build --check --analyze
/astro-deploy --target github-pages
```

## Requirements

- Node.js >= 18
- npm >= 9
- Claude Code CLI

## License

MIT
