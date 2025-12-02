# Railway MCP 설치 가이드

Claude Code에서 Railway MCP를 설정하는 상세 가이드입니다.

---

## 1. 사전 요구사항

### 1.1 Railway CLI 설치 (필수)

공식 MCP 서버는 Railway CLI를 통해 작동하므로 반드시 설치해야 합니다.

**npm (권장)**
```bash
npm install -g @railway/cli
```

**Homebrew (macOS)**
```bash
brew install railway
```

**Shell 스크립트 (Linux/macOS)**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

**Scoop (Windows)**
```bash
scoop install railway
```

**설치 확인**
```bash
railway --version
# 예: railway version 3.x.x
```

### 1.2 Railway 로그인

```bash
# 브라우저 기반 로그인 (권장)
railway login

# 또는 토큰으로 로그인
railway login --token <YOUR_TOKEN>

# 로그인 상태 확인
railway whoami
```

---

## 2. 공식 MCP 서버 설치

### 방법 A: Claude Code 명령어 (가장 간단)

```bash
claude mcp add Railway npx @railway/mcp-server
```

또는 전체 형식:

```bash
claude mcp add railway-mcp-server -- npx -y @railway/mcp-server
```

### 방법 B: JSON 형식으로 추가

```bash
claude mcp add-json "railway-mcp-server" '{"command":"npx","args":["-y","@railway/mcp-server"]}'
```

### 방법 C: 설정 파일 직접 편집

#### 전역 설정 (모든 프로젝트)

`~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "railway": {
      "command": "npx",
      "args": ["-y", "@railway/mcp-server"]
    }
  }
}
```

#### 프로젝트별 설정

`.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "railway": {
      "command": "npx",
      "args": ["-y", "@railway/mcp-server"]
    }
  }
}
```

### 방법 D: 로컬 개발 설치

개발/디버깅 용도:

```bash
# 저장소 클론
git clone https://github.com/railwayapp/railway-mcp-server.git
cd railway-mcp-server

# 의존성 설치 (pnpm 필요)
pnpm install

# 개발 모드 실행
pnpm dev
```

Claude Code 설정 (로컬):

```bash
claude mcp add railway-mcp-server node /path/to/railway-mcp-server/dist/index.js
```

---

## 3. 커뮤니티 MCP 서버 설치 (풀 기능)

커뮤니티 버전은 146+ 도구로 100% Railway API를 지원합니다.

### 3.1 Railway API Token 발급

1. [Railway Dashboard](https://railway.app/account/tokens) 접속
2. "Create Token" 클릭
3. 토큰 이름 입력 (예: `claude-mcp`)
4. **토큰 즉시 복사** (다시 볼 수 없음)

### 3.2 토큰 보안 관리

```bash
# 환경 변수로 설정 (권장)
export RAILWAY_API_TOKEN="your_token_here"

# 또는 .bashrc/.zshrc에 추가
echo 'export RAILWAY_API_TOKEN="your_token_here"' >> ~/.zshrc
```

**주의**: 토큰을 Git에 커밋하지 마세요!

### 3.3 커뮤니티 MCP 서버 설치

**Claude Code 명령어:**

```bash
claude mcp add railway-full -e RAILWAY_API_TOKEN=$RAILWAY_API_TOKEN -- npx -y @crazyrabbitltc/railway-mcp
```

**설정 파일 방식:**

```json
{
  "mcpServers": {
    "railway-full": {
      "command": "npx",
      "args": ["-y", "@crazyrabbitltc/railway-mcp"],
      "env": {
        "RAILWAY_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

**환경 변수 참조 방식:**

```json
{
  "mcpServers": {
    "railway-full": {
      "command": "npx",
      "args": ["-y", "@crazyrabbitltc/railway-mcp"],
      "env": {
        "RAILWAY_API_TOKEN": "${RAILWAY_API_TOKEN}"
      }
    }
  }
}
```

---

## 4. 설치 확인

### 4.1 MCP 서버 상태 확인

Claude Code에서:

```
/mcp
```

`railway` 또는 `railway-mcp-server`가 목록에 표시되어야 합니다.

### 4.2 연결 테스트

Claude Code에서 다음을 요청:

```
"Railway 프로젝트 목록을 보여줘"
```

또는 CLI로 직접 확인:

```bash
railway status
```

### 4.3 CLI 상태 확인

```bash
# CLI 버전 확인
railway --version

# 로그인 상태 확인
railway whoami

# 현재 연결된 프로젝트 확인
railway status
```

---

## 5. 다중 환경 설정

### 5.1 공식 + 커뮤니티 동시 설정

두 서버를 모두 사용하려면:

```json
{
  "mcpServers": {
    "railway": {
      "command": "npx",
      "args": ["-y", "@railway/mcp-server"]
    },
    "railway-full": {
      "command": "npx",
      "args": ["-y", "@crazyrabbitltc/railway-mcp"],
      "env": {
        "RAILWAY_API_TOKEN": "${RAILWAY_API_TOKEN}"
      }
    }
  }
}
```

- `railway`: 안전한 기본 작업용
- `railway-full`: 고급 기능 필요시

### 5.2 프로젝트별 설정

개발/프로덕션 별도 관리:

```json
{
  "mcpServers": {
    "railway-dev": {
      "command": "npx",
      "args": ["-y", "@railway/mcp-server"]
    },
    "railway-prod": {
      "command": "npx",
      "args": ["-y", "@crazyrabbitltc/railway-mcp"],
      "env": {
        "RAILWAY_API_TOKEN": "${RAILWAY_PROD_TOKEN}"
      }
    }
  }
}
```

---

## 6. 프로젝트 빠른 설정 템플릿

새 프로젝트에서 빠르게 설정:

```bash
# .claude 디렉토리 생성
mkdir -p .claude

# 공식 MCP 설정 파일 생성
cat > .claude/settings.local.json << 'EOF'
{
  "mcpServers": {
    "railway": {
      "command": "npx",
      "args": ["-y", "@railway/mcp-server"]
    }
  }
}
EOF

# .gitignore에 추가 (토큰 보호)
echo ".claude/settings.local.json" >> .gitignore
```

---

## 7. VS Code / Cursor 설정

### VS Code

`.vscode/mcp.json`:

```json
{
  "servers": {
    "railway": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@railway/mcp-server"]
    }
  }
}
```

### Cursor

`.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "railway-mcp-server": {
      "command": "npx",
      "args": ["-y", "@railway/mcp-server"]
    }
  }
}
```

---

## 8. 업그레이드 및 유지보수

### MCP 서버 업데이트

NPX를 사용하면 항상 최신 버전이 실행됩니다.

수동 업데이트가 필요한 경우:

```bash
# npm 캐시 정리
npm cache clean --force

# 또는 특정 버전 지정
claude mcp add railway -- npx -y @railway/mcp-server@latest
```

### Railway CLI 업데이트

```bash
# npm
npm update -g @railway/cli

# Homebrew
brew upgrade railway
```

---

## 9. 요약: 빠른 시작

**1단계: Railway CLI 설치**
```bash
npm install -g @railway/cli
railway login
```

**2단계: MCP 서버 추가**
```bash
claude mcp add Railway npx @railway/mcp-server
```

**3단계: 확인**
```
/mcp
```

**4단계: 사용**
```
"Railway 프로젝트 목록 보여줘"
"새 프로젝트 만들고 배포해줘"
```
