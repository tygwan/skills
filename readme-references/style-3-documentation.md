# Style 3: Documentation-First (문서 중심)

> 상세한 설명, 명확한 구조, 전문적인 기술 문서 스타일. [Best-README-Template](https://github.com/othneildrew/Best-README-Template) 참고.

---

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/tygwan/my-skills">
    <img src="assets/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">My Skills</h3>

  <p align="center">
    A curated collection of Claude Code skills for enhanced developer productivity
    <br />
    <a href="#documentation"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="#quick-start">Quick Start</a>
    ·
    <a href="https://github.com/tygwan/my-skills/issues">Report Bug</a>
    ·
    <a href="https://github.com/tygwan/my-skills/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#skills-catalog">Skills Catalog</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

---

## About The Project

Skills are modular packages that extend Claude Code's capabilities with specialized knowledge, workflows, and tool integrations. This repository contains 30+ production-ready skills covering:

- **Project Scaffolding** - Next.js, Flutter, and more
- **Testing & Debugging** - TDD, systematic debugging
- **Deployment** - Vercel, Railway integration
- **Documentation** - Markdown conversion, changelogs

### Built With

* [![Claude][Claude-badge]][Claude-url]
* [![Markdown][Markdown-badge]][Markdown-url]
* [![Python][Python-badge]][Python-url]

---

## Getting Started

### Prerequisites

- Claude Code CLI installed
- Git

### Installation

1. Clone the repository
   ```sh
   git clone https://github.com/tygwan/my-skills.git
   ```

2. Create skills directory in your project
   ```sh
   mkdir -p .claude/skills
   ```

3. Copy desired skills
   ```sh
   cp -r my-skills/nextjs15-init .claude/skills/
   ```

4. Verify installation
   ```sh
   # In Claude Code
   /skills
   ```

---

## Usage

```bash
# List installed skills
/skills

# Invoke a specific skill
/skill nextjs15-init
```

_For more examples, please refer to the [Documentation](https://github.com/tygwan/my-skills/wiki)_

---

## Skills Catalog

### Project Initialization
| Skill | Description | Tokens |
|-------|-------------|--------|
| [nextjs15-init](./nextjs15-init/) | Next.js 15 App Router project | ~3K |
| [flutter-init](./flutter-init/) | Flutter Clean Architecture | ~3K |

### Testing
| Skill | Description | Tokens |
|-------|-------------|--------|
| [test-driven-development](./test-driven-development/) | TDD workflow | ~3K |
| [systematic-debugging](./systematic-debugging/) | Root cause analysis | ~3K |

[**View complete catalog →**](./SKILLS.md)

---

## Roadmap

- [x] Core skills (30+)
- [x] Skill creator guide
- [ ] Skill marketplace
- [ ] Auto-update system

See [open issues](https://github.com/tygwan/my-skills/issues) for proposed features.

---

## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingSkill`)
3. Commit your Changes (`git commit -m 'Add AmazingSkill'`)
4. Push to the Branch (`git push origin feature/AmazingSkill`)
5. Open a Pull Request

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

<!-- MARKDOWN LINKS & IMAGES -->
[Claude-badge]: https://img.shields.io/badge/Claude-D97757?style=for-the-badge&logo=anthropic&logoColor=white
[Claude-url]: https://claude.ai
[Markdown-badge]: https://img.shields.io/badge/Markdown-000000?style=for-the-badge&logo=markdown&logoColor=white
[Markdown-url]: https://www.markdownguide.org/
[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://python.org
