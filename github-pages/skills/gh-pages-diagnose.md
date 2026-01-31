---
skill: gh-pages-diagnose
description: Diagnose GitHub Pages deployment conflicts - identify legacy/workflow collisions, stale content, and build failures
triggers:
  - "gh-pages diagnose"
  - "배포 진단"
  - "deploy diagnose"
  - "사이트 이전 버전"
  - "old version deployed"
model: sonnet
---

# GitHub Pages Deployment Diagnostics

## When to Use
- 배포된 사이트가 이전 버전을 표시할 때
- 워크플로우는 성공했는데 사이트가 변경되지 않을 때
- "pages build and deployment" 와 커스텀 워크플로우가 동시 실행될 때

## Diagnostic Steps

### Step 1: Check Pages Configuration
```bash
gh api repos/{owner}/{repo}/pages \
  --jq '{build_type: .build_type, source: .source, status: .status, html_url: .html_url}'
```

**Expected output for healthy setup:**
```json
{"build_type": "workflow", "source": {...}, "status": "built"}
```

**Red flags:**
- `build_type: "legacy"` + Actions workflow 존재 = **충돌**
- `status: "errored"` = 빌드 실패

### Step 2: Check Branch State
```bash
gh api repos/{owner}/{repo}/branches --jq '.[].name'
```

**Red flags:**
- `gh-pages` branch 존재 + `build_type: workflow` = 잔존 데이터 (삭제 권장)
- `gh-pages` branch 존재 + `build_type: legacy` = 정상 (legacy 모드)

### Step 3: Check Workflow Run History
```bash
gh api "repos/{owner}/{repo}/actions/runs?per_page=10" \
  --jq '.workflow_runs[] | "\(.name) | \(.conclusion) | \(.created_at)"'
```

**Red flags:**
- `pages build and deployment` (Jekyll auto-build)와 커스텀 워크플로우가 번갈아 실행
- 커스텀 워크플로우 이후 `pages build and deployment`가 실행됨 = **덮어쓰기 발생**

### Step 4: Compare Content Timestamps
```bash
# gh-pages branch 최신 커밋
gh api "repos/{owner}/{repo}/commits?sha=gh-pages&per_page=1" \
  --jq '.[0] | "\(.sha[0:7]) \(.commit.committer.date)"'

# default branch 최신 커밋
gh api "repos/{owner}/{repo}/commits?per_page=1" \
  --jq '.[0] | "\(.sha[0:7]) \(.commit.committer.date)"'
```

gh-pages 커밋이 더 최신이면 Jekyll이 Astro/Next.js 배포를 덮어쓴 것.

### Step 5: Verify Served Content
```bash
# 실제 서빙되는 페이지 프레임워크 판별
curl -sL "https://{user}.github.io/{repo}/" | grep -oE "(astro|next|jekyll|minima|vite)" | head -5
```

## Common Issues & Fixes

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Jekyll 사이트 표시 | build_type=legacy + gh-pages branch | `build_type=workflow` 전환 + gh-pages 삭제 |
| 404 Not Found | base URL 미설정 | Framework config에 base path 추가 |
| 빌드 성공인데 구버전 | CDN 캐시 | 5-10분 대기 또는 `?v={timestamp}` 추가 |
| CSS/JS 깨짐 | Asset path가 root 기준 | 상대경로 또는 base URL 적용 |
| CNAME 초기화됨 | 배포 시 CNAME 파일 누락 | public/ 디렉토리에 CNAME 파일 추가 |

## Auto-Fix Script

```bash
#!/bin/bash
# gh-pages-fix.sh - Resolve deployment conflicts
OWNER="$1"
REPO="$2"

echo "=== Diagnosing $OWNER/$REPO ==="

BUILD_TYPE=$(gh api "repos/$OWNER/$REPO/pages" --jq '.build_type')
HAS_GHPAGES=$(gh api "repos/$OWNER/$REPO/branches" --jq '.[].name' | grep -c '^gh-pages$')
HAS_WORKFLOW=$(gh api "repos/$OWNER/$REPO/contents/.github/workflows" --jq '.[].name' 2>/dev/null | grep -c 'deploy')

echo "Build type:     $BUILD_TYPE"
echo "gh-pages exists: $HAS_GHPAGES"
echo "Deploy workflow: $HAS_WORKFLOW"

if [ "$BUILD_TYPE" = "legacy" ] && [ "$HAS_WORKFLOW" -gt 0 ]; then
  echo ""
  echo "CONFLICT DETECTED: legacy build + Actions workflow"
  echo "Fix: Switch to workflow mode and delete gh-pages branch"
  echo ""
  read -p "Apply fix? (y/N): " CONFIRM
  if [ "$CONFIRM" = "y" ]; then
    gh api -X PUT "repos/$OWNER/$REPO/pages" -f build_type=workflow
    echo "-> build_type set to workflow"
    if [ "$HAS_GHPAGES" -gt 0 ]; then
      gh api -X DELETE "repos/$OWNER/$REPO/git/refs/heads/gh-pages"
      echo "-> gh-pages branch deleted"
    fi
    echo "Done. Trigger workflow: gh workflow run 'Deploy Site' --repo $OWNER/$REPO"
  fi
elif [ "$BUILD_TYPE" = "workflow" ] && [ "$HAS_GHPAGES" -gt 0 ]; then
  echo ""
  echo "WARNING: Stale gh-pages branch exists (safe to delete)"
fi
```
