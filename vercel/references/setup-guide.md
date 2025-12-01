# Vercel MCP 설치 가이드

Claude Code에서 Vercel MCP를 설정하는 상세 가이드입니다.

## 1. Vercel API Token 발급

### 1.1 토큰 생성

1. [Vercel Dashboard](https://vercel.com/account/tokens) 접속
2. "Create Token" 버튼 클릭
3. 토큰 설정:
   - **Token Name**: `claude-mcp` (식별용)
   - **Scope**:
     - `Full Account`: 모든 프로젝트 접근
     - `Specific Team`: 특정 팀만 접근
   - **Expiration**: 필요에 따라 설정 (권장: 90일)
4. "Create" 클릭
5. **토큰 즉시 복사** (다시 볼 수 없음)

### 1.2 토큰 보안 관리

```bash
# 환경 변수로 설정 (권장)
export VERCEL_API_TOKEN="your_token_here"

# 또는 .env 파일에 저장
echo "VERCEL_API_TOKEN=your_token_here" >> ~/.env

# .bashrc 또는 .zshrc에 추가
echo 'export VERCEL_API_TOKEN="your_token_here"' >> ~/.zshrc
```

**주의**: 토큰을 Git에 커밋하지 마세요!

---

## 2. MCP 서버 설치 방법

### 방법 A: Claude Code 명령어 (가장 간단)

```bash
claude mcp add vercel -e VERCEL_API_TOKEN=$VERCEL_API_TOKEN -- npx -y mcp-vercel
```

### 방법 B: 설정 파일 직접 편집

#### 전역 설정 (모든 프로젝트)

`~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "vercel": {
      "command": "npx",
      "args": ["-y", "mcp-vercel"],
      "env": {
        "VERCEL_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

#### 프로젝트별 설정

`.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "vercel": {
      "command": "npx",
      "args": ["-y", "mcp-vercel"],
      "env": {
        "VERCEL_API_TOKEN": "${VERCEL_API_TOKEN}"
      }
    }
  }
}
```

### 방법 C: 로컬 서버 설치

```bash
# 1. 저장소 클론
git clone https://github.com/nganiet/mcp-vercel.git ~/mcp-servers/vercel
cd ~/mcp-servers/vercel

# 2. 의존성 설치
npm install

# 3. 환경 변수 파일 생성
cat > .env << EOF
VERCEL_API_TOKEN=your_token_here
EOF

# 4. 서버 테스트
npm start
```

로컬 설치 후 Claude Code 설정:

```json
{
  "mcpServers": {
    "vercel": {
      "command": "node",
      "args": ["~/mcp-servers/vercel/dist/index.js"],
      "env": {
        "VERCEL_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

### 방법 D: Docker 컨테이너

```bash
# 이미지 빌드
docker build -t vercel-mcp https://github.com/nganiet/mcp-vercel.git

# 컨테이너 실행
docker run -d \
  --name vercel-mcp \
  -e VERCEL_API_TOKEN=your_token_here \
  -p 3399:3399 \
  vercel-mcp
```

Claude Code 설정 (HTTP 모드):

```json
{
  "mcpServers": {
    "vercel": {
      "url": "http://localhost:3399"
    }
  }
}
```

---

## 3. 설치 확인

### 3.1 MCP 서버 상태 확인

Claude Code에서:

```
/mcp
```

`vercel` 서버가 목록에 표시되어야 합니다.

### 3.2 연결 테스트

Claude Code에서 다음을 요청:

```
"Vercel 배포 목록을 보여줘"
```

또는 직접 API 테스트:

```bash
curl -H "Authorization: Bearer $VERCEL_API_TOKEN" \
  https://api.vercel.com/v9/projects
```

### 3.3 도구 목록 확인

MCP 연결 후 사용 가능한 도구:

- `vercel-list-all-deployments`
- `vercel-get-deployment`
- `vercel-create-deployment`
- `vercel-create-project`
- `vercel-get-project`
- `vercel-get-environments`
- `vercel-create-environment-variables`
- `vercel-list-all-teams`
- `vercel-create-team`

---

## 4. Vercel CLI 병행 설치 (권장)

MCP와 함께 CLI도 설치하면 더 유연하게 사용할 수 있습니다:

```bash
# CLI 설치
npm install -g vercel

# 로그인
vercel login

# 프로젝트 연결
vercel link
```

---

## 5. 프로젝트별 설정 템플릿

새 프로젝트에서 빠르게 설정하려면:

```bash
# .claude 디렉토리 생성
mkdir -p .claude

# 설정 파일 생성
cat > .claude/settings.local.json << 'EOF'
{
  "mcpServers": {
    "vercel": {
      "command": "npx",
      "args": ["-y", "mcp-vercel"],
      "env": {
        "VERCEL_API_TOKEN": "${VERCEL_API_TOKEN}"
      }
    }
  }
}
EOF

# .gitignore에 추가
echo ".claude/settings.local.json" >> .gitignore
```

---

## 6. 팀 환경 설정

### 6.1 팀 토큰 사용

팀 프로젝트의 경우 팀 범위 토큰을 사용:

1. Vercel Dashboard → Team Settings → Tokens
2. 팀 범위 토큰 생성
3. 설정에 팀 ID 추가 (선택):

```json
{
  "mcpServers": {
    "vercel": {
      "command": "npx",
      "args": ["-y", "mcp-vercel"],
      "env": {
        "VERCEL_API_TOKEN": "team_token_here",
        "VERCEL_TEAM_ID": "team_xxxxx"
      }
    }
  }
}
```

### 6.2 다중 환경 설정

개발/스테이징/프로덕션 별도 관리:

```json
{
  "mcpServers": {
    "vercel-dev": {
      "command": "npx",
      "args": ["-y", "mcp-vercel"],
      "env": {
        "VERCEL_API_TOKEN": "${VERCEL_DEV_TOKEN}"
      }
    },
    "vercel-prod": {
      "command": "npx",
      "args": ["-y", "mcp-vercel"],
      "env": {
        "VERCEL_API_TOKEN": "${VERCEL_PROD_TOKEN}"
      }
    }
  }
}
```
