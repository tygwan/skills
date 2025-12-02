---
name: railway
description: Railway MCP 설치 및 클라우드 배포 자동화 스킬 - Claude Code 전용
version: 1.0.0
triggers:
  - "railway 설정"
  - "railway mcp 설치"
  - "railway 배포"
  - "railway setup"
  - "railway deploy"
  - "railway 환경 설정"
  - "railway 프로젝트"
tools:
  - Bash
  - Read
  - Write
  - WebFetch
  - AskUserQuestion
---

# Railway 통합 스킬

Railway MCP 서버 설치부터 배포 자동화까지 Claude Code에서 Railway를 완벽하게 활용할 수 있도록 안내합니다.

## 개요

Railway는 개발자 친화적인 클라우드 플랫폼으로, 인프라 관리 없이 앱을 배포할 수 있습니다.

이 스킬은 두 가지 접근 방식을 지원합니다:

| 방식 | 설명 | 적합한 경우 |
|------|------|------------|
| **MCP 통합** | Railway API에 직접 연결 | 자연어로 프로젝트 관리, 배포, 모니터링 |
| **CLI 기반** | Railway CLI 명령어 활용 | 빠른 배포, 로그 확인, 환경 변수 관리 |

### 공식 vs 커뮤니티 MCP 서버

| 서버 | 패키지 | 특징 |
|------|--------|------|
| **공식** | `@railway/mcp-server` | 안전 중심, 파괴적 작업 제외 |
| **커뮤니티** | `@crazyrabbitltc/railway-mcp` | 146+ 도구, 100% API 커버리지 |

---

## Phase 1: 환경 확인

### Step 1.1: 사전 요구사항 확인

```yaml
checklist:
  - Node.js 18+ 설치 여부
  - Railway 계정 보유 여부
  - Railway CLI 설치 여부 (MCP 서버 필수)
  - 프로젝트 Git 연결 상태
```

### Step 1.2: 환경 진단

다음 명령어로 환경을 확인합니다:

```bash
# Node.js 버전 확인
node --version

# Railway CLI 설치 여부
railway --version

# Git 상태 확인
git status
```

### Step 1.3: 사용자 선택 요청

사용자에게 원하는 설정 방식을 물어봅니다:

**옵션 A**: 공식 MCP 서버 설치 (안전, 권장)
**옵션 B**: 커뮤니티 MCP 서버 설치 (풀 기능)
**옵션 C**: Railway CLI만 사용 (MCP 없이)
**옵션 D**: 둘 다 설정 (CLI + MCP)

---

## Phase 2: Railway CLI 설정

### Step 2.1: Railway CLI 설치

```bash
# npm으로 전역 설치
npm install -g @railway/cli

# 또는 Homebrew (macOS)
brew install railway

# 또는 Shell 스크립트 (Linux/macOS)
curl -fsSL https://railway.app/install.sh | sh

# Windows (scoop)
scoop install railway
```

### Step 2.2: Railway 로그인

```bash
# 브라우저 기반 로그인 (권장)
railway login

# 또는 토큰으로 로그인
railway login --token <YOUR_TOKEN>
```

### Step 2.3: 프로젝트 연결

```bash
# 새 프로젝트 생성
railway init

# 또는 기존 프로젝트에 연결
railway link
```

---

## Phase 3: MCP 서버 설정 (공식)

### Step 3.1: Railway CLI 필수 설치

**중요**: 공식 MCP 서버는 Railway CLI를 통해 작동합니다.

```bash
# Railway CLI 설치 확인
railway --version

# 로그인 상태 확인
railway whoami
```

### Step 3.2: MCP 서버 설치 (방법 선택)

#### 방법 A: Claude Code 명령어 (가장 간단, 권장)

```bash
claude mcp add Railway npx @railway/mcp-server
```

또는 전체 형식:

```bash
claude mcp add railway-mcp-server -- npx -y @railway/mcp-server
```

#### 방법 B: JSON 설정 추가

```bash
claude mcp add-json "railway-mcp-server" '{"command":"npx","args":["-y","@railway/mcp-server"]}'
```

#### 방법 C: 설정 파일 직접 편집

전역 설정 `~/.claude/settings.json`:

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

프로젝트별 설정 `.claude/settings.local.json`:

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

### Step 3.3: MCP 연결 확인

```bash
# Claude Code에서 MCP 서버 목록 확인
/mcp
```

`railway` 또는 `railway-mcp-server`가 목록에 표시되어야 합니다.

---

## Phase 4: MCP 서버 설정 (커뮤니티 - 풀 기능)

### Step 4.1: Railway API Token 발급

커뮤니티 버전은 API 토큰이 필요합니다:

1. [Railway Dashboard](https://railway.app/account/tokens) 접속
2. "Create Token" 클릭
3. 토큰 이름 입력 (예: "claude-mcp")
4. 토큰 복사 및 안전하게 보관

### Step 4.2: 커뮤니티 MCP 서버 설치

```bash
claude mcp add railway-full -e RAILWAY_API_TOKEN=your_token_here -- npx -y @crazyrabbitltc/railway-mcp
```

또는 설정 파일:

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

**주의**: 커뮤니티 버전은 삭제 등 파괴적 작업도 포함됩니다.

---

## Phase 5: 배포 워크플로우

### 5.1: CLI를 통한 배포

```bash
# 현재 디렉토리 배포
railway up

# 로그 실시간 확인
railway logs

# 환경 변수 설정
railway variables set KEY=value

# 도메인 생성
railway domain
```

### 5.2: MCP를 통한 배포 (연결된 경우)

MCP 연결 시 자연어로 배포 가능:

```
"현재 프로젝트를 Railway에 배포해줘"
"Next.js 앱을 생성하고 Railway에 배포해줘. 도메인도 할당해줘"
"Postgres 데이터베이스 배포해줘"
"최근 실패한 배포를 찾아서 로그 보여주고 수정안 제안해줘"
```

### 5.3: 템플릿 배포

Railway는 다양한 템플릿을 제공합니다:

```
"Postgres 데이터베이스 배포해줘"
"Redis 캐시 서버 배포해줘"
"단일 노드 ClickHouse 데이터베이스 배포해줘"
```

---

## Phase 6: 환경 관리

### 6.1: 환경 변수 관리

CLI 사용:

```bash
# 변수 목록 확인
railway variables

# 변수 설정
railway variables set DATABASE_URL="postgres://..."

# 변수 삭제
railway variables delete OLD_KEY

# 로컬로 환경 변수 가져오기
railway variables > .env
```

MCP 사용:

```
"DATABASE_URL 환경 변수를 설정해줘"
"현재 환경 변수 목록 보여줘"
```

### 6.2: 환경 복제

```
"production 환경을 복제해서 development 환경을 만들어줘"
"staging 환경 생성해줘"
```

---

## Phase 7: 도메인 관리

### 7.1: Railway 도메인 생성

```bash
# 자동 도메인 생성
railway domain

# 결과: your-app-production.up.railway.app
```

MCP 사용:

```
"이 서비스에 도메인 할당해줘"
```

### 7.2: 커스텀 도메인 연결

1. Railway Dashboard에서 서비스 선택
2. Settings → Domains
3. Custom Domain 추가
4. DNS 설정:
   - CNAME: `your-app.up.railway.app`

---

## Quick Reference

### 자주 사용하는 CLI 명령어

| 명령어 | 설명 |
|--------|------|
| `railway login` | 로그인 |
| `railway init` | 새 프로젝트 생성 |
| `railway link` | 기존 프로젝트 연결 |
| `railway up` | 배포 |
| `railway logs` | 로그 확인 |
| `railway variables` | 환경 변수 관리 |
| `railway domain` | 도메인 생성 |
| `railway open` | 대시보드 열기 |
| `railway status` | 상태 확인 |

### MCP 도구 목록 (공식)

| 도구 | 기능 |
|------|------|
| `check-railway-status` | CLI 설치 및 로그인 상태 확인 |
| `list-projects` | 프로젝트 목록 조회 |
| `create-project-and-link` | 프로젝트 생성 및 연결 |
| `list-services` | 서비스 목록 조회 |
| `link-service` | 서비스 연결 |
| `deploy` | 배포 실행 |
| `deploy-template` | 템플릿 배포 (DB 등) |
| `create-environment` | 환경 생성 |
| `link-environment` | 환경 연결 |
| `list-variables` | 환경 변수 조회 |
| `set-variables` | 환경 변수 설정 |
| `generate-domain` | 도메인 생성 |
| `get-logs` | 로그 조회 |

---

## 트러블슈팅

### 일반적인 문제

**MCP 연결 실패**
```bash
# Railway CLI 설치 확인
railway --version

# 로그인 상태 확인
railway whoami

# Claude Code MCP 재시작
/mcp restart railway
```

**배포 실패**
```bash
# 빌드 로그 확인
railway logs

# 로컬 빌드 테스트
npm run build
```

**환경 변수 누락**
```bash
# 환경 변수 확인
railway variables

# 변수 설정
railway variables set KEY=value
```

---

## 참고 자료

- [Railway 공식 문서](https://docs.railway.com/)
- [Railway MCP Server 문서](https://docs.railway.com/reference/mcp-server)
- [Railway CLI 레퍼런스](https://docs.railway.com/reference/cli-api)
- [railway-mcp-server GitHub](https://github.com/railwayapp/railway-mcp-server)
- [@railway/mcp-server NPM](https://www.npmjs.com/package/@railway/mcp-server)
