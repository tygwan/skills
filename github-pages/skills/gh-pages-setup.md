---
skill: gh-pages-setup
description: Set up GitHub Actions deployment for GitHub Pages projects with framework-specific templates
triggers:
  - "gh-pages setup"
  - "배포 설정"
  - "deploy setup"
  - "pages setup"
model: sonnet
---

# GitHub Pages Setup

## When to Use
- 새 프로젝트에 GitHub Pages 배포를 처음 설정할 때
- Legacy 배포에서 GitHub Actions 배포로 마이그레이션할 때
- 프레임워크 변경 후 배포 설정을 갱신할 때

## Setup Workflow

### Step 1: Detect Framework

```bash
# 프로젝트 루트에서 프레임워크 자동 감지
detect_framework() {
  if [ -f "astro.config.mjs" ] || [ -f "astro.config.ts" ]; then echo "astro"
  elif [ -f "next.config.js" ] || [ -f "next.config.mjs" ]; then echo "nextjs"
  elif [ -f "vite.config.ts" ] || [ -f "vite.config.js" ]; then echo "vite"
  elif [ -f "_config.yml" ]; then echo "jekyll"
  elif [ -f "hugo.toml" ] || [ -f "config.toml" ]; then echo "hugo"
  elif [ -f "package.json" ]; then echo "node-generic"
  else echo "static"
  fi
}
```

### Step 2: Configure Base URL

**Astro:**
```javascript
// astro.config.mjs
export default defineConfig({
  site: 'https://{user}.github.io',
  base: '/{repo}/',
});
```

**Vite / React:**
```javascript
// vite.config.ts
export default defineConfig({
  base: '/{repo}/',
});
```

**Next.js (Static Export):**
```javascript
// next.config.mjs
const nextConfig = {
  output: 'export',
  basePath: '/{repo}',
  images: { unoptimized: true },
};
export default nextConfig;
```

### Step 3: Create Workflow File

**Astro:**
```yaml
# .github/workflows/deploy-site.yml
name: Deploy Site

on:
  push:
    branches: [main]
    paths: ['site/**', '.github/workflows/deploy-site.yml']
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: ./package-lock.json
      - run: npm ci
      - run: npx astro build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./dist

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

**Vite / React:**
```yaml
name: Deploy Site

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./dist

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

**Static HTML (no build):**
```yaml
name: Deploy Site

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - uses: actions/deploy-pages@v4
        id: deployment
```

### Step 4: Enable GitHub Actions as Pages Source

```bash
# Pages 활성화 (아직 없는 경우)
gh api -X POST "repos/{owner}/{repo}/pages" \
  -f build_type=workflow \
  -f source[branch]=main \
  -f source[path]=/

# 또는 기존 설정을 workflow로 전환
gh api -X PUT "repos/{owner}/{repo}/pages" -f build_type=workflow
```

### Step 5: Clean Up Legacy Artifacts

```bash
# gh-pages branch가 남아있으면 삭제
gh api "repos/{owner}/{repo}/branches" --jq '.[].name' | grep -q '^gh-pages$' && \
  gh api -X DELETE "repos/{owner}/{repo}/git/refs/heads/gh-pages" && \
  echo "gh-pages branch deleted"

# Jekyll 설정 파일 잔존 확인
for f in _config.yml Gemfile .nojekyll; do
  [ -f "$f" ] && echo "WARNING: $f still exists in project root"
done
```

### Step 6: Trigger & Verify

```bash
# 워크플로우 수동 트리거
gh workflow run "Deploy Site" --repo {owner}/{repo}

# 실행 상태 추적
sleep 5
gh api "repos/{owner}/{repo}/actions/runs?per_page=1" \
  --jq '.workflow_runs[0] | "\(.name): \(.status) \(.conclusion)"'

# 배포 완료 후 검증
gh api "repos/{owner}/{repo}/pages" --jq '{status, build_type, html_url}'
```

## Monorepo / Subdirectory Projects

Site 소스가 서브디렉토리에 있는 경우:

```yaml
# 예: site/portfolio/ 에 Astro 프로젝트가 있는 경우
jobs:
  build:
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: site/portfolio/package-lock.json  # 정확한 경로
      - run: npm ci
        working-directory: site/portfolio                          # working-directory 지정
      - run: npx astro build
        working-directory: site/portfolio
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site/portfolio/dist                                # 빌드 출력 경로
```

## Checklist

- [ ] `build_type` 이 `workflow`인지 확인
- [ ] `gh-pages` branch 존재 여부 확인 (없어야 함)
- [ ] Base URL이 `/{repo}/` 형태로 설정됨
- [ ] `workflow_dispatch` 트리거 포함됨
- [ ] `concurrency.group: pages` 설정됨
- [ ] `permissions: pages: write, id-token: write` 포함됨
- [ ] CNAME 필요시 `public/CNAME` 파일 존재
- [ ] `.nojekyll` 파일이 빌드 출력에 포함됨 (non-Jekyll 프로젝트)
