---
name: vercel
description: Vercel MCP 설치 및 배포 자동화 스킬 - Claude Code 전용
version: 1.0.0
triggers:
  - "vercel 설정"
  - "vercel mcp 설치"
  - "vercel 배포"
  - "vercel setup"
  - "vercel deploy"
  - "vercel 환경 설정"
tools:
  - Bash
  - Read
  - Write
  - WebFetch
  - AskUserQuestion
---

# Vercel 통합 스킬

Vercel MCP 서버 설치부터 배포 자동화까지 Claude Code에서 Vercel을 완벽하게 활용할 수 있도록 안내합니다.

## 개요

이 스킬은 두 가지 접근 방식을 지원합니다:

| 방식 | 설명 | 적합한 경우 |
|------|------|------------|
| **MCP 통합** | Vercel API에 직접 연결 | 실시간 배포 관리, 환경 변수 조작 |
| **CLI 기반** | Vercel CLI 명령어 활용 | 간단한 배포, 빠른 설정 |

---

## Phase 1: 환경 확인

### Step 1.1: 사전 요구사항 확인

```yaml
checklist:
  - Node.js 18+ 설치 여부
  - Vercel 계정 보유 여부
  - Vercel API Token 발급 여부
  - 프로젝트 Git 연결 상태
```

### Step 1.2: 환경 진단

다음 명령어로 환경을 확인합니다:

```bash
# Node.js 버전 확인
node --version

# Vercel CLI 설치 여부
vercel --version

# Git 상태 확인
git status
```

### Step 1.3: 사용자 선택 요청

사용자에게 원하는 설정 방식을 물어봅니다:

**옵션 A**: MCP 서버 설치 (풀 기능)
**옵션 B**: Vercel CLI만 사용 (간단 배포)
**옵션 C**: 둘 다 설정

---

## Phase 2: Vercel CLI 설정

### Step 2.1: Vercel CLI 설치

```bash
# npm으로 전역 설치
npm install -g vercel

# 또는 pnpm
pnpm add -g vercel
```

### Step 2.2: Vercel 로그인

```bash
# 브라우저 기반 로그인
vercel login

# 또는 토큰으로 로그인
vercel login --token <YOUR_TOKEN>
```

### Step 2.3: 프로젝트 연결

```bash
# 현재 디렉토리를 Vercel 프로젝트에 연결
vercel link
```

---

## Phase 3: MCP 서버 설정

### Step 3.1: Vercel API Token 발급

1. [Vercel Dashboard](https://vercel.com/account/tokens) 접속
2. "Create Token" 클릭
3. 토큰 이름 입력 (예: "claude-mcp")
4. Scope 선택: Full Account 또는 특정 팀
5. 토큰 복사 및 안전하게 보관

### Step 3.2: MCP 서버 설치 (방법 선택)

#### 방법 A: NPX로 직접 실행 (권장)

Claude Code 설정에 추가:

```bash
claude mcp add vercel -e VERCEL_API_TOKEN=your_token_here -- npx -y @anthropic/vercel-mcp
```

#### 방법 B: 로컬 설치

```bash
# 저장소 클론
git clone https://github.com/nganiet/mcp-vercel.git
cd mcp-vercel

# 의존성 설치
npm install

# 환경 변수 설정
echo "VERCEL_API_TOKEN=your_token_here" > .env

# 서버 시작
npm start
```

#### 방법 C: Claude Code 설정 파일 직접 편집

`~/.claude/settings.json` 또는 프로젝트의 `.claude/settings.local.json`:

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

### Step 3.3: MCP 연결 확인

```bash
# Claude Code에서 MCP 서버 목록 확인
/mcp
```

---

## Phase 4: 배포 워크플로우

### 4.1: 빌드 검증

배포 전 반드시 빌드를 검증합니다:

```bash
# 빌드 실행
npm run build

# 린트 검사
npm run lint

# 타입 체크 (TypeScript)
npm run type-check
```

### 4.2: 환경별 배포

```bash
# Preview 배포 (기본)
vercel

# Production 배포
vercel --prod

# 특정 환경 지정
vercel --env production
```

### 4.3: MCP를 통한 배포 (연결된 경우)

MCP 연결 시 자연어로 배포 가능:

```
"현재 프로젝트를 Vercel에 프로덕션 배포해줘"
"최근 5개 배포 목록 보여줘"
"production 환경에 API_KEY 환경 변수 추가해줘"
```

---

## Phase 5: 환경 변수 관리

### 5.1: CLI로 환경 변수 설정

```bash
# 단일 변수 추가
vercel env add VARIABLE_NAME

# 파일에서 일괄 추가
vercel env pull .env.local
vercel env push
```

### 5.2: MCP로 환경 변수 관리

MCP 연결 시:

```
"DATABASE_URL 환경 변수를 production에 추가해줘"
"현재 프로젝트의 환경 변수 목록 보여줘"
```

---

## Phase 6: 도메인 관리

### 6.1: 커스텀 도메인 추가

```bash
# 도메인 추가
vercel domains add example.com

# 도메인 목록 확인
vercel domains ls
```

### 6.2: DNS 설정 안내

Vercel에 도메인 연결 후:
- A 레코드: `76.76.21.21`
- CNAME: `cname.vercel-dns.com`

---

## Quick Reference

### 자주 사용하는 명령어

| 명령어 | 설명 |
|--------|------|
| `vercel` | Preview 배포 |
| `vercel --prod` | Production 배포 |
| `vercel env pull` | 환경 변수 로컬 동기화 |
| `vercel logs` | 배포 로그 확인 |
| `vercel inspect <url>` | 배포 상세 정보 |
| `vercel rollback` | 이전 배포로 롤백 |

### MCP 도구 목록

| 도구 | 기능 |
|------|------|
| `vercel-list-all-deployments` | 배포 목록 조회 |
| `vercel-get-deployment` | 배포 상세 조회 |
| `vercel-create-deployment` | 새 배포 생성 |
| `vercel-create-project` | 프로젝트 생성 |
| `vercel-get-environments` | 환경 변수 조회 |
| `vercel-create-environment-variables` | 환경 변수 생성 |
| `vercel-list-all-teams` | 팀 목록 조회 |

---

## 트러블슈팅

### 일반적인 문제

**MCP 연결 실패**
```bash
# 토큰 유효성 확인
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.vercel.com/v9/projects

# Claude Code MCP 재시작
/mcp restart vercel
```

**배포 실패**
```bash
# 빌드 로그 확인
vercel logs --follow

# 로컬 빌드 테스트
vercel build
```

**환경 변수 누락**
```bash
# 환경 변수 동기화
vercel env pull .env.local
```

---

## 참고 자료

- [Vercel 공식 문서](https://vercel.com/docs)
- [Vercel CLI 레퍼런스](https://vercel.com/docs/cli)
- [mcp-vercel GitHub](https://github.com/nganiet/mcp-vercel)
- [MCP 프로토콜 문서](https://modelcontextprotocol.io/)
