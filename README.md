# Claude Code Skills Collection

Claude Code를 위한 프로젝트 자동화 스킬 모음입니다. 각 스킬은 특정 워크플로우나 작업을 자동화하여 개발 생산성을 향상시킵니다.

## 스킬 요약

### 프로젝트 초기화

| 스킬 | 설명 | 도구 | 토큰 |
|------|------|:----:|:----:|
| [nextjs15-init](#nextjs15-init) | Next.js 15 App Router 기반 프로젝트 자동 생성 | 5 | ~3K |
| [flutter-init](#flutter-init) | Flutter Clean Architecture 기반 프로젝트 자동 생성 | 5 | ~3K |

### UI/UX 개발

| 스킬 | 설명 | 도구 | 토큰 |
|------|------|:----:|:----:|
| [landing-page-guide](#landing-page-guide) | 11가지 필수 요소 기반 고전환 랜딩 페이지 가이드 | 3 | ~4K |
| [theme-factory](#theme-factory) | 10개 테마로 아티팩트 스타일링 | 2 | ~2K |
| [brand-guidelines](#brand-guidelines) | Anthropic 브랜드 가이드라인 적용 | 2 | ~1K |
| [artifacts-builder](#artifacts-builder) | React/Tailwind/shadcn 멀티컴포넌트 아티팩트 생성 | 4 | ~3K |

### AI 통합 도구

| 스킬 | 설명 | 도구 | 토큰 |
|------|------|:----:|:----:|
| [codex](#codex) | OpenAI Codex CLI 실행 및 코드 분석 | 3 | ~2K |
| [codex-claude-loop](#codex-claude-loop) | Claude + Codex 듀얼 AI 협업 루프 | 4 | ~3K |

### 문서화 및 변환

| 스킬 | 설명 | 도구 | 토큰 |
|------|------|:----:|:----:|
| [web-to-markdown](#web-to-markdown) | 웹페이지 URL을 마크다운으로 변환 | 4 | ~3K |
| [code-changelog](#code-changelog) | 코드 변경사항 자동 기록 및 HTML 뷰어 | 3 | ~2K |

### 프롬프트 및 워크플로우

| 스킬 | 설명 | 도구 | 토큰 |
|------|------|:----:|:----:|
| [prompt-enhancer](#prompt-enhancer) | 간단한 요청을 상세 요구사항으로 변환 | 3 | ~2K |
| [meta-prompt-generator](#meta-prompt-generator) | 구조화된 슬래시 커맨드 자동 생성 | 4 | ~3K |
| [brainstorming](#brainstorming) | 체계적 브레인스토밍 세션 진행 | 3 | ~2K |
| [tdd-mvp-planner](#tdd-mvp-planner) | Architecture → PLAN.md + TODO.md 자동 변환 | 5 | ~8K |

### 테스팅 및 디버깅

| 스킬 | 설명 | 도구 | 토큰 |
|------|------|:----:|:----:|
| [test-driven-development](#test-driven-development) | RED→GREEN→REFACTOR TDD 사이클 강제 | 4 | ~3K |
| [systematic-debugging](#systematic-debugging) | 근본 원인 분석 기반 체계적 디버깅 | 4 | ~3K |
| [agent-testing-framework](#agent-testing-framework) | AI 에이전트 TDD/E2E/Chaos 테스트 프레임워크 | 6 | ~12K |
| [webapp-testing](#webapp-testing) | Playwright 기반 웹앱 상호작용 테스트 | 4 | ~3K |

### 개발 전문가 페르소나

| 스킬 | 설명 | 도구 | 토큰 |
|------|------|:----:|:----:|
| [senior-architect](#senior-architect) | 시스템 아키텍처 설계 전문가 | 3 | ~4K |
| [senior-backend](#senior-backend) | 백엔드 개발 전문가 | 3 | ~4K |
| [senior-secops](#senior-secops) | 보안 운영 전문가 | 3 | ~4K |

### 보안 및 신뢰성

| 스킬 | 설명 | 도구 | 토큰 |
|------|------|:----:|:----:|
| [resilience-patterns](#resilience-patterns) | Circuit Breaker/Retry/Bulkhead 패턴 구현 | 5 | ~15K |
| [consensus-engine](#consensus-engine) | 다중 AI 에이전트 합의 알고리즘 | 4 | ~8K |

### Crypto 거래 시스템

| 스킬 | 설명 | 도구 | 토큰 |
|------|------|:----:|:----:|
| [crypto-agent-architect](#crypto-agent-architect) | 5-Layer 암호화폐 거래 에이전트 아키텍처 | 6 | ~20K |
| [crypto-risk-management](#crypto-risk-management) | Kelly Criterion/청산/가스/슬리피지/MEV 리스크 관리 | 5 | ~12K |
| [crypto-trading-strategies](#crypto-trading-strategies) | Arbitrage/Market Making/Momentum 등 5가지 전략 | 5 | ~15K |

### 개발 도구

| 스킬 | 설명 | 도구 | 토큰 |
|------|------|:----:|:----:|
| [skill-creator](#skill-creator) | Claude Code 스킬 생성 가이드 | 4 | ~3K |
| [skill-manager](#skill-manager) | 스킬 마켓플레이스 관리 및 배포 | 5 | ~4K |
| [mcp-builder](#mcp-builder) | MCP 서버 생성 가이드 | 4 | ~5K |
| [using-git-worktrees](#using-git-worktrees) | Git worktree 격리 작업 환경 생성 | 3 | ~2K |
| [finishing-a-development-branch](#finishing-a-development-branch) | 개발 브랜치 통합 및 정리 | 3 | ~2K |

---

## 상세 설명

### 프로젝트 초기화

#### nextjs15-init

Next.js 15 프로젝트를 도메인 기반으로 자동 생성합니다. App Router, ShadCN, Zustand, Tanstack Query 등 현대적인 스택으로 구성된 완전한 CRUD 앱을 즉시 생성할 수 있습니다.

- **도메인 선택**: Todo, Blog, Dashboard, E-commerce, Custom
- **스택 프리셋**: Minimal, Essential, Full Stack, Custom
- **기본 포함**: TypeScript, Tailwind CSS, ESLint
- **자동화**: 코드 검증 및 빌드

#### flutter-init

Flutter 프로젝트를 Clean Architecture 기반으로 자동 생성합니다. Riverpod 3.0, Drift, Easy Localization 등 현대적인 Flutter 스택으로 구성됩니다.

- **도메인 선택**: Todo, Habit, Note, Expense, Custom
- **스택 프리셋**: Minimal, Essential, Full Stack, Custom
- **아키텍처**: Clean Architecture 구조 자동 생성
- **코드 생성**: Freezed, Drift 코드 자동 생성

---

### UI/UX 개발

#### landing-page-guide

DESIGNNAS의 11가지 필수 요소 프레임워크를 기반으로 전환율이 높은 랜딩 페이지를 만드는 가이드입니다.

- 11가지 필수 랜딩 페이지 요소 가이드
- ShadCN UI 컴포넌트 활용
- SEO 최적화 및 접근성 표준
- Next.js 14+ App Router 최적화

#### theme-factory

슬라이드, 문서, 보고서, HTML 랜딩 페이지 등 아티팩트를 테마로 스타일링합니다.

- 10개의 전문 폰트 및 컬러 테마
- 응집력 있는 컬러 팔레트 (hex 코드)
- 헤더/본문용 보완 폰트 페어링
- 맞춤형 테마 즉석 생성

#### brand-guidelines

Anthropic의 공식 브랜드 컬러와 타이포그래피를 모든 아티팩트에 적용합니다.

- 공식 브랜드 컬러 (Dark, Orange, Blue, Green)
- 타이포그래피 시스템 (Poppins, Lora)
- 스마트 폰트 적용 및 자동 폴백

#### artifacts-builder

React, Tailwind CSS, shadcn/ui를 사용하여 멀티 컴포넌트 HTML 아티팩트를 생성합니다.

- React 18 + TypeScript + Vite + Parcel
- 40+ shadcn/ui 컴포넌트 사전 설치
- 단일 HTML 파일로 번들링
- Path alias (@/) 설정

---

### AI 통합 도구

#### codex

OpenAI Codex CLI를 실행하여 코드 분석, 리팩토링, 자동 편집을 수행합니다.

- **모델**: gpt-5, gpt-5-codex
- **Reasoning effort**: low, medium, high
- **Sandbox**: read-only, workspace-write, danger-full-access
- 세션 재개 기능

#### codex-claude-loop

Claude Code와 Codex가 협력하는 듀얼 AI 엔지니어링 루프입니다.

- **Claude**: 아키텍처, 계획, 실행
- **Codex**: 검증 및 코드 리뷰
- 지속적인 상호 리뷰
- 컨텍스트 핸드오프

---

### 문서화 및 변환

#### web-to-markdown

웹페이지 URL을 마크다운으로 변환합니다.

- **일반 모드**: 읽기 좋은 마크다운
- **AI 최적화**: 구조화된 변환
- **듀얼 모드**: 원본 + AI 최적화 동시 생성
- Playwright 폴백 (동적 콘텐츠)

#### code-changelog

AI가 생성한 코드 변경사항을 자동으로 기록합니다.

- 매 수정마다 MD 파일 자동 생성
- HTML 뷰어 (Python 서버)
- 다크 모드 UI
- 최신 문서 우선 표시

---

### 프롬프트 및 워크플로우

#### prompt-enhancer

간단한 개발 요청을 프로젝트 컨텍스트 분석을 통해 상세한 요구사항으로 변환합니다.

- 프로젝트 구조 자동 분석
- 기술 스택 감지
- 기존 패턴 파악
- 구조화된 요구사항 문서

#### meta-prompt-generator

간단한 설명으로 병렬 처리 가능한 구조화된 슬래시 커맨드를 생성합니다.

- 지능형 웹 검색 지식 수집
- 단계 기반 워크플로우 설계
- 병렬 실행 전략 최적화
- 프레임워크별 검증 요구사항

#### brainstorming

프로젝트 아이디어, 기능 설계, 문제 해결을 위한 체계적인 브레인스토밍을 진행합니다.

- 아이디어 발산 및 수렴 프로세스
- 다각도 분석 (기술, 비즈니스, UX)
- 구조화된 의사결정 프레임워크
- 실행 가능한 액션 아이템

#### tdd-mvp-planner

Architecture 문서를 TDD 기반 PLAN.md와 TODO.md로 체계적으로 변환합니다.

- **7-phase 워크플로우**: Context → PLAN → TODO
- **TDD 원칙**: RED → GREEN → REFACTOR → COMMIT
- Codex 자동 검증 및 품질 보증
- 의존성 그래프 및 리스크 분석

---

### 테스팅 및 디버깅

#### test-driven-development

TDD 방법론을 엄격하게 적용합니다.

- 철저한 TDD 원칙 (테스트 우선)
- RED → GREEN → REFACTOR 사이클
- 실패 테스트 검증 필수
- 최소 코드 구현 원칙

#### systematic-debugging

체계적인 디버깅 방법론으로 복잡한 버그를 효율적으로 해결합니다.

- 체계적 문제 분석 프레임워크
- 근본 원인 식별 (Root Cause Analysis)
- 증거 기반 가설 검증
- 예방적 개선 제안

#### agent-testing-framework

AI 에이전트 시스템을 위한 종합 테스트 프레임워크입니다.

- **커버리지**: Unit 90%+, Integration 80%+
- **테스트 유형**: TDD, Unit, Integration, E2E, Load, Chaos
- LLM 응답 모킹 및 합의 테스트
- Circuit Breaker/Retry 검증
- Playwright E2E, Hypothesis 속성 기반 테스트

#### webapp-testing

Playwright로 로컬 웹앱을 상호작용하고 테스트합니다.

- Python Playwright 스크립트 작성
- 다중 서버 라이프사이클 관리
- Reconnaissance-then-action 패턴
- DOM 검사 및 셀렉터 발견

---

### 개발 전문가 페르소나

#### senior-architect

시스템 아키텍처 전문가로 확장 가능하고 유지보수 가능한 아키텍처를 설계합니다.

- 시스템 설계 및 아키텍처 패턴
- 기술 스택 선택 가이드
- 확장성 및 성능 고려사항
- 아키텍처 의사결정 프레임워크

#### senior-backend

백엔드 개발 전문가로 안정적이고 확장 가능한 서버 시스템을 구축합니다.

- API 설계 패턴 및 베스트 프랙티스
- 데이터베이스 최적화
- 백엔드 보안 프랙티스
- 마이크로서비스 아키텍처

#### senior-secops

보안 운영 전문가로 시스템의 보안성과 운영 안정성을 책임집니다.

- 보안 표준 및 컴플라이언스
- 취약점 관리 가이드
- CI/CD 보안 통합
- 인시던트 대응 절차

---

### 보안 및 신뢰성

#### resilience-patterns

시스템 복원력을 높이기 위한 설계 패턴과 구현 가이드입니다.

- **패턴**: Circuit Breaker, Retry, Timeout, Bulkhead, Fallback, Rate Limiter
- Python/TypeScript 구현 코드
- 조합 패턴 및 통합 가이드
- 복원력 테스트 시나리오

#### consensus-engine

다중 AI 에이전트 간의 합의 알고리즘을 구현합니다.

- **투표 전략**: Majority, Unanimous, Weighted, Quorum
- 충돌 감지 및 해결
- 합의 품질 메트릭
- 분산 시스템 일관성 보장

---

### Crypto 거래 시스템

#### crypto-agent-architect

5-Layer 아키텍처로 프로덕션급 암호화폐 거래 에이전트를 설계합니다.

```
Layer 1: Smart Consensus (Multi-LLM 의사결정)
Layer 2: Binance Adapter (Resilient Exchange API)
Layer 3: Trading Strategy (Risk & Position Management)
Layer 4: Data Pipeline (Market Data & Validation)
Layer 5: Monitoring & Observability
```

- Multi-LLM 합의 (GPT-4, Claude, Gemini)
- 80%+ 테스트 커버리지 요구
- MEV 보호, 가스 최적화
- Kill Switch 및 Paper Trading

#### crypto-risk-management

암호화폐 거래의 6가지 핵심 리스크를 관리합니다.

| 리스크 | 심각도 | 감지 시간 |
|--------|--------|----------|
| Liquidation | Critical | Real-time |
| Drawdown | High | Daily |
| Slippage | Medium | Per-trade |
| Gas Costs | Medium | Pre-tx |
| MEV | Medium | Post-tx |
| Position Sizing | High | Pre-trade |

- **Kelly Criterion**: Fractional Kelly (0.25) 포지션 사이징
- 청산 모니터링 (30초 주기)
- 가스 최적화 및 배칭
- Flashbots MEV 보호

#### crypto-trading-strategies

5가지 프로덕션급 거래 전략을 구현합니다.

| 전략 | 유형 | 승률 | Sharpe |
|------|------|------|--------|
| Arbitrage | Market-neutral | 95%+ | 3-5 |
| Market Making | Liquidity | 80-90% | 1-3 |
| Momentum | Trend-following | 40-60% | 0.5-2 |
| Mean Reversion | Contrarian | 60-75% | 1.5-3 |
| Grid Trading | Range-bound | 70-85% | 1-2.5 |

- 백테스팅 프레임워크
- 가스비/슬리피지/MEV 고려
- crypto-agent-architect Layer 3 통합

---

### 개발 도구

#### skill-creator

효과적인 Claude Code 스킬을 생성하기 위한 가이드입니다.

- 스킬 구조 이해
- 단계별 생성 프로세스
- 스크립트/레퍼런스/에셋 관리
- 자동 검증 및 패키징

#### skill-manager

Claude Code 스킬과 마켓플레이스를 관리하고 배포합니다.

- 마켓플레이스 초기화 및 관리
- Semantic versioning 자동화
- Conventional commits 및 Git 태그
- Changelog 자동 생성

#### mcp-builder

MCP (Model Context Protocol) 서버를 생성하는 가이드입니다.

- Python (FastMCP), Node/TypeScript (MCP SDK)
- Agent-Centric Design 원칙
- 단계별 구현 프로세스
- 평가 프레임워크

#### using-git-worktrees

Git worktree로 격리된 작업 환경을 생성합니다.

- 체계적인 디렉토리 선택
- 안전성 검증 (.gitignore)
- 프로젝트 자동 설정 (npm/cargo/pip)
- 기준 테스트 검증

#### finishing-a-development-branch

구현 완료 후 작업을 통합하는 가이드입니다.

- 테스트 검증 → 옵션 제시 → 선택 실행
- 로컬 merge 또는 PR 생성
- Worktree 자동 정리
- 안전한 작업 삭제

---

## 사용 방법

```bash
# 스킬 목록 확인
/skills

# 특정 스킬 사용 (자동 감지)
"Next.js Todo 앱 만들어줘" → nextjs15-init 활성화
"Flutter 습관 트래커 앱 만들어줘" → flutter-init 활성화
"이 URL 마크다운으로 변환해줘" → web-to-markdown 활성화
```

## 설치 방법

### 마켓플레이스 설치 (권장)

```bash
# 1. 마켓플레이스 추가
/plugin marketplace add tygwan/skills

# 2. 스킬 설치
/plugin install nextjs15-init@tygwan-skills
/plugin install flutter-init@tygwan-skills

# 3. 확인
/help
```

### 수동 설치

```bash
git clone https://github.com/tygwan/skills.git
cp -r skills/* /path/to/your-project/.claude/skills/
```

## 기여하기

1. Fork this repository
2. Create feature branch (`git checkout -b feature/amazing-skill`)
3. Commit changes (`git commit -m 'Add amazing skill'`)
4. Push to branch (`git push origin feature/amazing-skill`)
5. Open Pull Request

## 라이선스

MIT License

## 관련 링크

- [Claude Code 공식 문서](https://docs.claude.com/en/docs/claude-code)
- [스킬 작성 가이드](./skill-creator/)
- [MCP 프로토콜](https://modelcontextprotocol.io/)

---

**Made with Claude Code**
