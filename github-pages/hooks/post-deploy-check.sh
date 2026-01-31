#!/bin/bash
# post-deploy-check.sh
# GitHub Pages 배포 후 자동 검증 훅
# Usage: ./post-deploy-check.sh {owner} {repo}

set -euo pipefail

OWNER="${1:?Usage: $0 <owner> <repo>}"
REPO="${2:?Usage: $0 <owner> <repo>}"
URL="https://$OWNER.github.io/$REPO/"
MAX_WAIT=120
INTERVAL=10

echo "[deploy-check] Verifying $OWNER/$REPO deployment..."

# 1. Check Pages config
BUILD_TYPE=$(gh api "repos/$OWNER/$REPO/pages" --jq '.build_type' 2>/dev/null || echo "none")
if [ "$BUILD_TYPE" != "workflow" ]; then
  echo "[deploy-check] WARNING: build_type is '$BUILD_TYPE', expected 'workflow'"
fi

# 2. Check for conflicting branches
if gh api "repos/$OWNER/$REPO/branches" --jq '.[].name' 2>/dev/null | grep -q '^gh-pages$'; then
  echo "[deploy-check] WARNING: gh-pages branch still exists (potential conflict source)"
fi

# 3. Wait for site to be available
echo "[deploy-check] Waiting for site at $URL ..."
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
  STATUS=$(curl -sL -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null || echo "000")
  if [ "$STATUS" = "200" ]; then
    echo "[deploy-check] Site is live (HTTP $STATUS)"
    break
  fi
  echo "[deploy-check] HTTP $STATUS, retrying in ${INTERVAL}s..."
  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done

if [ "$STATUS" != "200" ]; then
  echo "[deploy-check] FAIL: Site not reachable after ${MAX_WAIT}s (HTTP $STATUS)"
  exit 1
fi

# 4. Check latest workflow run
LATEST_RUN=$(gh api "repos/$OWNER/$REPO/actions/runs?per_page=1" \
  --jq '.workflow_runs[0] | "\(.name): \(.conclusion)"' 2>/dev/null || echo "unknown")
echo "[deploy-check] Latest run: $LATEST_RUN"

# 5. Summary
echo "[deploy-check] Verification complete for $URL"
