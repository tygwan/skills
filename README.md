# Claude Code Skills Collection

Claude Code를 위한 프로젝트 자동화 스킬 모음입니다. 각 스킬은 특정 워크플로우나 작업을 자동화하여 개발 생산성을 향상시킵니다.

## 📋 스킬 목록

### 🛠️ 프로젝트 초기화

#### [nextjs15-init](./nextjs15-init/)
Next.js 15 프로젝트를 도메인 기반으로 자동 생성합니다. App Router, ShadCN, Zustand, Tanstack Query 등 현대적인 스택으로 구성된 완전한 CRUD 앱을 즉시 생성할 수 있습니다.

**주요 기능:**
- 도메인 선택: Todo/Blog/Dashboard/E-commerce/Custom
- 스택 프리셋: Minimal/Essential/Full Stack/Custom
- TypeScript, Tailwind CSS, ESLint 기본 포함
- 자동 코드 검증 및 빌드

#### [flutter-init](./flutter-init/)
Flutter 프로젝트를 Clean Architecture 기반으로 자동 생성합니다. Riverpod 3.0, Drift, Easy Localization 등 현대적인 Flutter 스택으로 구성된 완전한 CRUD 앱을 즉시 생성할 수 있습니다.

**주요 기능:**
- 도메인 선택: Todo/Habit/Note/Expense/Custom
- 스택 프리셋: Minimal/Essential/Full Stack/Custom
- Clean Architecture 구조 자동 생성
- Freezed, Drift 코드 자동 생성

### 🎨 UI/UX 개발

#### [landing-page-guide](./landing-page-guide/)
고품질 랜딩 페이지를 Next.js 또는 React로 제작하기 위한 가이드입니다. DESIGNNAS의 11가지 필수 요소 프레임워크를 기반으로 전환율이 높은 랜딩 페이지를 만들 수 있습니다.

**주요 기능:**
- 11가지 필수 랜딩 페이지 요소 가이드
- ShadCN UI 컴포넌트 활용
- SEO 최적화 및 접근성 표준
- Next.js 14+ App Router 최적화

#### [theme-factory](./theme-factory/)
슬라이드, 문서, 보고서, HTML 랜딩 페이지 등 아티팩트를 테마로 스타일링하는 툴킷입니다. 10개의 사전 설정 테마 또는 즉석에서 생성한 새 테마를 적용할 수 있습니다.

**주요 기능:**
- 10개의 전문 폰트 및 컬러 테마
- 응집력 있는 컬러 팔레트 (hex 코드 포함)
- 헤더 및 본문 텍스트용 보완 폰트 페어링
- 맞춤형 테마 즉석 생성

#### [brand-guidelines](./brand-guidelines/)
Anthropic의 공식 브랜드 컬러와 타이포그래피를 모든 아티팩트에 적용합니다. 브랜드 컬러, 스타일 가이드라인, 시각적 포매팅이 필요한 경우 사용합니다.

**주요 기능:**
- Anthropic 공식 브랜드 컬러 (Dark, Orange, Blue, Green)
- 타이포그래피 시스템 (Poppins, Lora)
- 스마트 폰트 적용 및 자동 폴백
- 텍스트 및 도형 스타일링

### 🤖 AI 통합 도구

#### [codex](./codex/)
OpenAI Codex CLI를 실행하여 코드 분석, 리팩토링, 자동 편집을 수행합니다.

**주요 기능:**
- 모델 선택: gpt-5, gpt-5-codex
- Reasoning effort 설정: low/medium/high
- Sandbox 모드: read-only/workspace-write/danger-full-access
- 세션 재개 기능

#### [codex-claude-loop](./codex-claude-loop/)
Claude Code와 Codex가 협력하는 듀얼 AI 엔지니어링 루프를 구현합니다. Claude는 설계 및 구현을, Codex는 검증 및 리뷰를 담당하여 최적의 코드 품질을 달성합니다.

**주요 기능:**
- Claude: 아키텍처, 계획, 실행
- Codex: 검증 및 코드 리뷰
- 지속적인 상호 리뷰
- 컨텍스트 핸드오프

#### [artifacts-builder](./artifacts-builder/)
React, Tailwind CSS, shadcn/ui를 사용하여 정교한 멀티 컴포넌트 claude.ai HTML 아티팩트를 생성합니다. 상태 관리, 라우팅, shadcn/ui 컴포넌트가 필요한 복잡한 아티팩트에 사용됩니다.

**주요 기능:**
- React 18 + TypeScript + Vite + Parcel
- Tailwind CSS + 40+ shadcn/ui 컴포넌트 사전 설치
- 단일 HTML 파일로 번들링
- Path alias 설정 (@/)

### 📝 문서화 및 변환

#### [web-to-markdown](./web-to-markdown/)
웹페이지 URL을 입력받아 마크다운 형태로 변환하여 저장합니다. 일반 모드, AI 최적화 모드, 듀얼 모드를 지원하여 다양한 목적에 맞게 변환할 수 있습니다.

**주요 기능:**
- 일반 모드: 읽기 좋은 마크다운 변환
- AI 최적화 모드: AI 컨텍스트용 구조화된 변환
- 듀얼 모드: 원본 + AI 최적화 버전 동시 생성
- Playwright 폴백으로 동적 콘텐츠 처리

#### [code-changelog](./code-changelog/)
AI가 생성한 모든 코드 변경사항을 reviews 폴더에 기록하고, 간단한 HTML 뷰어로 웹 브라우저에서 실시간 확인할 수 있습니다.

**주요 기능:**
- 자동 문서 생성 (매 수정마다 MD 파일)
- 간단한 HTML 뷰어 (Python 서버)
- 자동 index.html 업데이트
- 다크 모드 UI
- 최신 문서 우선 표시

### 🧠 프롬프트 및 워크플로우

#### [prompt-enhancer](./prompt-enhancer/)
사용자의 간단한 개발 요청을 프로젝트 컨텍스트를 분석하여 명확하고 상세한 요구사항으로 변환합니다.

**주요 기능:**
- 프로젝트 구조 자동 분석
- 기술 스택 감지
- 기존 패턴 파악
- 구조화된 요구사항 문서 생성

#### [meta-prompt-generator](./meta-prompt-generator/)
간단한 설명을 받아 단계별 병렬 처리가 가능한 구조화된 커스텀 슬래시 커맨드를 자동으로 생성합니다.

**주요 기능:**
- 지능형 지식 수집 (웹 검색)
- 단계 기반 워크플로우 설계
- 포괄적인 테스트 생성
- 병렬 실행 전략 최적화
- 프레임워크별 검증 요구사항 포함

### 🔧 개발 도구

#### [skill-creator](./skill-creator/)
효과적인 Claude Code 스킬을 생성하기 위한 가이드입니다. 스킬의 구조, 작성 방법, 패키징 등을 단계별로 안내합니다.

**주요 기능:**
- 스킬 구조 이해
- 단계별 생성 프로세스
- 스크립트, 레퍼런스, 에셋 관리
- 자동 검증 및 패키징

#### [skill-manager](./skill-manager/)
Claude Code 스킬과 마켓플레이스를 효율적으로 관리하고 배포합니다. 마켓플레이스 초기화, 스킬 업데이트, Git 워크플로우, 버전 관리, 릴리스 노트를 자동화합니다.

**주요 기능:**
- 마켓플레이스 초기화 및 관리
- 스킬 추가 및 메타데이터 업데이트
- Semantic versioning 자동화
- Conventional commits 및 Git 태그
- Changelog 자동 생성

#### [mcp-builder](./mcp-builder/)
고품질 MCP (Model Context Protocol) 서버를 생성하기 위한 가이드입니다. LLM이 외부 서비스와 효과적으로 상호작용할 수 있는 도구를 제공합니다.

**주요 기능:**
- Python (FastMCP) 및 Node/TypeScript (MCP SDK) 지원
- Agent-Centric Design 원칙
- 단계별 구현 프로세스
- 평가 프레임워크

#### [using-git-worktrees](./using-git-worktrees/)
Git worktree를 사용하여 격리된 작업 환경을 생성합니다. 현재 작업 공간에서 분리가 필요한 기능 작업이나 구현 계획 실행 전에 사용합니다.

**주요 기능:**
- 체계적인 디렉토리 선택 프로세스
- 안전성 검증 (.gitignore 확인)
- 프로젝트 자동 설정 (npm/cargo/pip)
- 기준 테스트 검증

#### [finishing-a-development-branch](./finishing-a-development-branch/)
구현 완료 후 작업을 통합하는 방법을 안내합니다. 모든 테스트가 통과한 후 merge, PR, 또는 정리를 위한 구조화된 옵션을 제시합니다.

**주요 기능:**
- 테스트 검증 → 옵션 제시 → 선택 실행 → 정리
- 로컬 merge 또는 PR 생성
- Worktree 자동 정리
- 안전한 작업 삭제 (확인 필요)

#### [webapp-testing](./webapp-testing/)
Playwright를 사용하여 로컬 웹 애플리케이션을 상호작용하고 테스트합니다. 프론트엔드 기능 검증, UI 동작 디버깅, 브라우저 스크린샷 캡처, 브라우저 로그 확인을 지원합니다.

**주요 기능:**
- Python Playwright 스크립트 작성
- 서버 라이프사이클 관리 (다중 서버 지원)
- Reconnaissance-then-action 패턴
- DOM 검사 및 셀렉터 발견

## 🚀 사용 방법

각 스킬은 Claude Code에서 자동으로 활성화됩니다. 다음과 같이 사용할 수 있습니다:

```
# 스킬 목록 확인
/skills

# 특정 스킬 사용 (자동 감지)
"Next.js Todo 앱 만들어줘" → nextjs15-init 스킬 활성화
"Flutter 습관 트래커 앱 만들어줘" → flutter-init 스킬 활성화
"이 URL 마크다운으로 변환해줘" → web-to-markdown 스킬 활성화
```

## 📦 설치 방법

### 방법 1: 마켓플레이스 설치 (권장) 🎉

Claude Code의 플러그인 마켓플레이스 시스템을 사용하여 쉽게 설치할 수 있습니다:

#### 1단계: 마켓플레이스 추가
```bash
/plugin marketplace add tygwan/skills
```

#### 2단계: 원하는 스킬 설치
```bash
# 전체 목록 확인
/plugin

# 개별 스킬 설치
/plugin install nextjs15-init@tygwan-skills
/plugin install flutter-init@tygwan-skills
/plugin install web-to-markdown@tygwan-skills
/plugin install codex-claude-loop@tygwan-skills

# 또는 한 번에 모두 설치
/plugin install nextjs15-init flutter-init landing-page-guide codex codex-claude-loop web-to-markdown code-changelog prompt-enhancer meta-prompt-generator skill-creator mcp-builder @tygwan-skills
```

#### 3단계: 설치 확인
```bash
/help  # 새로운 스킬이 자동으로 표시됩니다
```

**장점:**
- ✅ 한 줄 명령으로 간편한 설치
- ✅ 자동 업데이트 지원
- ✅ 개별 스킬 선택 설치 가능
- ✅ 프로젝트 간 재사용 가능

### 방법 2: 수동 설치

1. 이 저장소를 클론합니다:
```bash
git clone https://github.com/tygwan/skills.git
```

2. Claude Code 프로젝트의 `.claude/skills` 폴더에 복사합니다:
```bash
cp -r skills/* /path/to/your-project/.claude/skills/
```

3. Claude Code에서 자동으로 스킬을 인식합니다.

## 🤝 기여하기

스킬 개선이나 새로운 스킬 추가를 환영합니다!

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/amazing-skill`)
3. Commit your changes (`git commit -m 'Add some amazing skill'`)
4. Push to the branch (`git push origin feature/amazing-skill`)
5. Open a Pull Request

## 📄 라이선스

MIT License - 자유롭게 사용하고 수정할 수 있습니다.

## 🔗 관련 링크

- [Claude Code 공식 문서](https://docs.claude.com/en/docs/claude-code)
- [스킬 작성 가이드](./skill-creator/)
- [MCP 프로토콜](https://modelcontextprotocol.io/)

---

**Made with ❤️ for Claude Code community**
