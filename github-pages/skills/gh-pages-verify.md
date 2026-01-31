---
skill: gh-pages-verify
description: Post-deployment verification for GitHub Pages - content validation, performance check, and conflict detection
triggers:
  - "gh-pages verify"
  - "배포 검증"
  - "deploy verify"
  - "사이트 확인"
model: sonnet
---

# GitHub Pages Post-Deploy Verification

## When to Use
- 배포 워크플로우 성공 후 실제 사이트 확인
- 정기 배포 상태 점검
- 새 프로젝트 첫 배포 후 검증

## Verification Steps

### 1. Deployment Status
```bash
OWNER="{owner}"
REPO="{repo}"

echo "=== Pages Configuration ==="
gh api "repos/$OWNER/$REPO/pages" \
  --jq '"Status: \(.status)\nBuild: \(.build_type)\nURL: \(.html_url)"'
```

Expected: `Status: built`, `Build: workflow`

### 2. Workflow Health
```bash
echo "=== Recent Deployments ==="
gh api "repos/$OWNER/$REPO/actions/runs?per_page=5" \
  --jq '.workflow_runs[] | "\(.name) | \(.conclusion) | \(.created_at)"'
```

**Healthy pattern**: 하나의 워크플로우 이름만 나타남
**Unhealthy pattern**: `pages build and deployment` + 커스텀 워크플로우 혼재

### 3. Content Validation
```bash
echo "=== Live Content Check ==="
URL="https://$OWNER.github.io/$REPO/"

# HTTP 상태 코드
STATUS=$(curl -sL -o /dev/null -w "%{http_code}" "$URL")
echo "HTTP Status: $STATUS"

# 페이지 타이틀 추출
TITLE=$(curl -sL "$URL" | grep -oP '(?<=<title>).*?(?=</title>)' | head -1)
echo "Page Title: $TITLE"

# 프레임워크 감지
FRAMEWORK=$(curl -sL "$URL" | grep -oiE "(astro|next|vite|jekyll|hugo)" | head -1)
echo "Framework: ${FRAMEWORK:-unknown}"
```

### 4. Conflict Detection
```bash
echo "=== Conflict Check ==="

# build_type 확인
BUILD_TYPE=$(gh api "repos/$OWNER/$REPO/pages" --jq '.build_type')

# gh-pages branch 존재 여부
BRANCHES=$(gh api "repos/$OWNER/$REPO/branches" --jq '.[].name')
HAS_GHPAGES=$(echo "$BRANCHES" | grep -c '^gh-pages$')

# Actions 워크플로우 존재 여부
HAS_DEPLOY_WF=$(gh api "repos/$OWNER/$REPO/contents/.github/workflows" \
  --jq '.[].name' 2>/dev/null | grep -c 'deploy')

if [ "$BUILD_TYPE" = "legacy" ] && [ "$HAS_DEPLOY_WF" -gt 0 ]; then
  echo "CONFLICT: Legacy mode + Deploy workflow found"
elif [ "$BUILD_TYPE" = "workflow" ] && [ "$HAS_GHPAGES" -gt 0 ]; then
  echo "WARNING: Stale gh-pages branch (recommend deletion)"
else
  echo "OK: No conflicts detected"
fi
```

### 5. Asset Integrity
```bash
echo "=== Asset Check ==="
URL="https://$OWNER.github.io/$REPO/"

# CSS 로드 확인
CSS_COUNT=$(curl -sL "$URL" | grep -c 'rel="stylesheet"')
echo "CSS files referenced: $CSS_COUNT"

# JS 로드 확인
JS_COUNT=$(curl -sL "$URL" | grep -c '<script')
echo "JS files referenced: $JS_COUNT"

# 404 리소스 확인 (주요 자산)
curl -sL "$URL" | grep -oP 'href="[^"]*\.css"' | while read -r line; do
  ASSET_URL=$(echo "$line" | grep -oP '"[^"]*"' | tr -d '"')
  # 상대 경로를 절대 경로로 변환
  if [[ ! "$ASSET_URL" =~ ^http ]]; then
    ASSET_URL="${URL%/}/$ASSET_URL"
  fi
  ASSET_STATUS=$(curl -sL -o /dev/null -w "%{http_code}" "$ASSET_URL")
  [ "$ASSET_STATUS" != "200" ] && echo "BROKEN: $ASSET_URL ($ASSET_STATUS)"
done
echo "Asset check complete"
```

## Multi-Repo Batch Verification

여러 프로젝트 페이지를 한번에 검증:

```bash
#!/bin/bash
OWNER="tygwan"
REPOS=("physical-unity" "AgenticLabeling" "cc-initializer" "DXTnavis")

echo "=== Batch Verification for $OWNER ==="
printf "%-25s %-10s %-10s %-8s %s\n" "REPO" "BUILD" "STATUS" "BRANCH" "URL"
echo "---"

for REPO in "${REPOS[@]}"; do
  PAGES=$(gh api "repos/$OWNER/$REPO/pages" 2>/dev/null)
  if [ $? -ne 0 ]; then
    printf "%-25s %-10s\n" "$REPO" "NO PAGES"
    continue
  fi

  BUILD=$(echo "$PAGES" | jq -r '.build_type')
  STATUS=$(echo "$PAGES" | jq -r '.status')
  URL=$(echo "$PAGES" | jq -r '.html_url')
  HAS_GP=$(gh api "repos/$OWNER/$REPO/branches" --jq '.[].name' 2>/dev/null | grep -c '^gh-pages$')
  BRANCH_WARN=""
  [ "$HAS_GP" -gt 0 ] && [ "$BUILD" = "workflow" ] && BRANCH_WARN="WARN"

  printf "%-25s %-10s %-10s %-8s %s\n" "$REPO" "$BUILD" "$STATUS" "${BRANCH_WARN:-OK}" "$URL"
done
```

## Pass/Fail Criteria

| Check | Pass | Fail |
|-------|------|------|
| HTTP Status | 200 | 404, 500, etc. |
| build_type | `workflow` | `legacy` with workflow files |
| gh-pages branch | Absent (workflow mode) | Present (workflow mode) |
| Workflow history | Single workflow type | Mixed (Jekyll + custom) |
| Page title | Matches expected | Empty or wrong title |
| CSS/JS assets | All 200 | Any 404 |
