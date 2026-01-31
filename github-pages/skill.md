---
skill: github-pages
description: GitHub Pages deployment rules, diagnostics, and automation - prevent legacy/workflow conflicts and ensure correct site version is served
triggers:
  - github pages
  - "깃허브 페이지"
  - "gh-pages"
  - "github.io"
  - "배포 충돌"
  - "deploy conflict"
  - "pages deploy"
model: sonnet
---

# GitHub Pages Deployment Skill

## Overview

GitHub Pages 배포 규칙을 명세화한 스킬. Legacy branch 배포와 GitHub Actions workflow 배포 간의 충돌을 방지하고, 올바른 버전이 서빙되는지 검증한다.

### Origin

physical-unity 프로젝트에서 발생한 실제 장애 사례를 기반으로 작성:
- `gh-pages` branch (Jekyll) + `master` branch (Astro) 두 배포 경로가 동시 존재
- Jekyll 자동 빌드가 Astro 배포를 덮어씀
- `build_type: legacy` 설정이 Actions 배포를 무력화

## Quick Reference

| Sub-skill | Trigger | Purpose |
|-----------|---------|---------|
| `/gh-pages-diagnose` | Deploy issue | 배포 충돌 진단 및 원인 분석 |
| `/gh-pages-setup` | New deploy | GitHub Actions 배포 초기 설정 |
| `/gh-pages-verify` | Post-deploy | 배포 후 버전 검증 |

## Core Rules

### Rule 1: Single Deployment Source (CRITICAL)

**하나의 저장소에는 반드시 하나의 배포 경로만 존재해야 한다.**

```
FORBIDDEN: gh-pages branch (legacy) + GitHub Actions workflow (workflow)
ALLOWED:   GitHub Actions workflow only (build_type: workflow)
ALLOWED:   gh-pages branch only (build_type: legacy) - not recommended
```

위반 시: 마지막에 실행된 빌드가 이전 배포를 덮어씀.

### Rule 2: Build Type Verification

배포 설정 변경 시 반드시 `build_type`을 확인한다:

```bash
# 현재 설정 확인
gh api repos/{owner}/{repo}/pages --jq '{build_type, source}'

# workflow로 변경 (GitHub Actions 유일 경로)
gh api -X PUT repos/{owner}/{repo}/pages -f build_type=workflow
```

| build_type | 의미 | 배포 트리거 |
|-----------|------|------------|
| `legacy` | Branch에서 직접 빌드 | Branch push |
| `workflow` | GitHub Actions만 허용 | Actions workflow |

### Rule 3: Branch Cleanup

`build_type: workflow`로 전환 후, 잔존하는 `gh-pages` branch를 삭제한다:

```bash
# gh-pages branch 삭제
gh api -X DELETE repos/{owner}/{repo}/git/refs/heads/gh-pages

# 삭제 확인
gh api repos/{owner}/{repo}/branches --jq '.[].name'
```

**주의**: Branch 삭제 전에 필요한 데이터가 없는지 확인.

### Rule 4: Framework-Specific Base URL

GitHub Pages는 `https://{user}.github.io/{repo}/` 구조. Base URL 미설정 시 리소스 404 발생.

| Framework | 설정 파일 | Base URL 설정 |
|-----------|----------|---------------|
| Astro | `astro.config.mjs` | `site: 'https://user.github.io', base: '/repo/'` |
| Next.js | `next.config.js` | `basePath: '/repo'`, `output: 'export'` |
| Vite/React | `vite.config.ts` | `base: '/repo/'` |
| Jekyll | `_config.yml` | `baseurl: '/repo'` |
| Hugo | `config.toml` | `baseURL = 'https://user.github.io/repo/'` |

**예외**: `{user}.github.io` repo는 root 배포이므로 base 불필요.

### Rule 5: Post-Deploy Verification

배포 후 반드시 검증 수행:

```bash
# 1. 배포 상태 확인
gh api repos/{owner}/{repo}/pages --jq '{status, build_type, html_url}'

# 2. 최신 워크플로우 실행 결과 확인
gh api "repos/{owner}/{repo}/actions/runs?per_page=3" \
  --jq '.workflow_runs[] | "\(.name): \(.conclusion) (\(.created_at))"'

# 3. 실제 사이트 내용 검증 (서빙 중인 콘텐츠)
curl -sL https://{user}.github.io/{repo}/ | head -20

# 4. 충돌 경로 확인 (legacy + workflow 동시 존재 여부)
gh api "repos/{owner}/{repo}/actions/runs?per_page=10" \
  --jq '.workflow_runs[].name' | sort | uniq -c
```

`pages build and deployment`(Jekyll 자동빌드)와 사용자 워크플로우가 모두 나타나면 **충돌 상태**.

### Rule 6: Workflow File Convention

```yaml
# .github/workflows/deploy-site.yml
name: Deploy Site                    # 명확한 이름

on:
  push:
    branches: [main]                 # default branch
    paths:
      - 'site/**'                    # 변경 감지 경로 한정
      - '.github/workflows/deploy-site.yml'
  workflow_dispatch:                  # 수동 트리거 항상 포함

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages                       # 동시 배포 방지
  cancel-in-progress: false          # 진행 중 배포 취소 안 함

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./dist               # 빌드 출력 디렉토리

  deploy:
    needs: build
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
```

## Diagnostic Flowchart

```
사이트가 이전 버전으로 표시됨
  │
  ├─ gh api repos/{o}/{r}/pages --jq .build_type
  │   ├─ "legacy" → Rule 2 위반 가능
  │   │   ├─ Actions workflow도 있나? → YES → Rule 1 위반 (충돌!)
  │   │   │   └─ 해결: build_type=workflow 전환 + gh-pages 삭제
  │   │   └─ 워크플로우 없음 → gh-pages branch 내용 확인
  │   └─ "workflow" → 워크플로우 실행 이력 확인
  │       ├─ 최근 실행 실패? → 빌드 로그 확인
  │       └─ 성공인데 구버전? → CDN 캐시 (5-10분 대기)
  │
  └─ Pages 설정 없음 → Settings > Pages에서 활성화 필요
```

## Integration with Other Skills

| Skill | Usage |
|-------|-------|
| `astro` | Astro 프로젝트 빌드 + 배포 워크플로우 |
| `git-workflow` | Branch 관리, PR 전략 |
| `ci-workflow` | CI/CD 파이프라인 설정 |
