---
name: atomic-task
description: 컨텍스트 효율적인 개발 문서 관리 스킬. ~200줄 단위의 원자적 작업 문서를 생성하여 컨텍스트 초기화 후에도 즉시 작업 재개 가능. 진행 상태 추적, 의도 기록, Git 커밋 연동 지원.
---

# Atomic Task

## Overview

컨텍스트 효율성을 극대화하는 개발 문서 관리 스킬.

**핵심 원칙**:
- 하나의 작업 = 하나의 문서 (~200줄)
- 컨텍스트 초기화 후 **1개 문서만 읽고** 즉시 작업 재개
- 모든 작업의 **의도(Intent)**를 기록하여 Git 커밋에 반영

## When to Use

- 새로운 기능 개발 시작 시
- 버그 수정 작업 시
- 리팩토링/개선 작업 시
- 컨텍스트가 커져서 효율적 관리가 필요할 때
- 작업 의도를 명확히 기록하고 싶을 때

## 문서 구조

```
dev-docs/
├── CLAUDE.md              # 프로젝트 전역 컨텍스트 (기존 유지)
├── DEVELOPMENT.md         # 개발 워크플로우 (기존 유지)
│
└── {user-defined-folder}/ # 사용자 정의 폴더
    └── {task-name}.md     # 원자적 작업 문서 (~200줄)
```

**폴더명과 파일명은 사용자가 정의**합니다. 개발 환경과 프로젝트에 맞게 자유롭게 구성하세요.

## Phase 1: 작업 문서 생성

### 1.1 폴더 및 파일 위치 결정

사용자에게 질문:

```
새 작업을 시작합니다. 문서를 어디에 저장할까요?

1. 기존 폴더 선택: [기존 폴더 목록 표시]
2. 새 폴더 생성: [폴더명 입력]

문서 파일명: [작업명 입력]
```

### 1.2 문서 생성

`dev-docs/{folder}/{task-name}.md` 파일 생성.

**문서 템플릿** (`templates/task-template.md` 참조):

```markdown
# {Task Title}

## Meta
- **Created**: YYYY-MM-DD HH:MM
- **Last Updated**: YYYY-MM-DD HH:MM
- **Status**: 🆕 NOT_STARTED | 🔄 IN_PROGRESS | ⏸️ PAUSED | ✅ COMPLETED
- **Related Docs**: [관련 문서 링크]

---

## Intent (의도)

### Why (왜 이 작업이 필요한가)
[이 작업의 목적과 배경을 명확히 기술]

### Expected Outcome (기대 결과)
[완료 시 어떤 상태가 되어야 하는지]

### Decisions Made (결정 사항)
[기술적 선택과 그 이유]
- 선택: [무엇을 선택했는지]
- 이유: [왜 그렇게 결정했는지]

---

## Progress Tracking

### Tasks
- [ ] Task 1: [설명]
- [ ] Task 2: [설명]
- [ ] Task 3: [설명]

### Completed
- [x] ~~Task 0: [설명]~~ (YYYY-MM-DD)

---

## Current Work

### Now Working On
**Task**: [현재 진행 중인 작업]
**Phase**: 🔴 RED | 🟢 GREEN | 🔵 REFACTOR | 📦 COMMIT
**Started**: YYYY-MM-DD HH:MM

### Context for Resume
[컨텍스트 초기화 후 이 섹션만 읽고 바로 작업 재개 가능하도록 작성]

현재 상태:
-

다음 단계:
-

작업 중인 파일:
-

---

## Changes Made

### Files Modified
| File | Change Type | Description |
|------|-------------|-------------|
| `path/to/file` | CREATE/MODIFY/DELETE | 변경 내용 |

### Code Changes Summary
[주요 코드 변경 사항 요약]

---

## Notes

### Blockers / Issues
[막힌 부분이나 이슈]

### References
[참고 자료, 링크, 문서]

---

## Git Commit Draft

### Commit Message
```
{type}({scope}): {subject}

## Why
{Intent.Why 섹션 내용}

## What
{Changes Made 섹션 요약}

📋 Task: dev-docs/{folder}/{task-name}.md
```

### Files to Stage
[커밋할 파일 목록]
```

## Phase 2: 작업 진행

### 2.1 상태 업데이트

작업 시작 시:
```markdown
## Meta
- **Status**: 🔄 IN_PROGRESS
- **Last Updated**: [현재 시간]
```

### 2.2 Progress Tracking 업데이트

작업 완료 시마다:
```markdown
## Progress Tracking

### Tasks
- [x] Task 1: [설명] ← 체크
- [ ] Task 2: [설명] ← 현재 작업
- [ ] Task 3: [설명]
```

### 2.3 Current Work 갱신

**항상 최신 상태 유지** - 컨텍스트 초기화 후 이 섹션만 읽고 재개 가능해야 함:

```markdown
## Current Work

### Now Working On
**Task**: 로그인 API 엔드포인트 구현
**Phase**: 🟢 GREEN
**Started**: 2025-12-04 15:30

### Context for Resume
현재 상태:
- 로그인 테스트 작성 완료 (tests/auth/login.test.ts)
- 테스트 실패 확인 (RED 완료)
- 기본 엔드포인트 구조 작성 중

다음 단계:
- POST /api/auth/login 핸들러 완성
- bcrypt로 비밀번호 검증 로직 추가
- JWT 토큰 반환 구현

작업 중인 파일:
- src/api/auth/login.ts (라인 45에서 중단)
- tests/auth/login.test.ts
```

### 2.4 Changes Made 누적

변경사항 발생 시마다 기록:

```markdown
## Changes Made

### Files Modified
| File | Change Type | Description |
|------|-------------|-------------|
| `src/models/user.ts` | MODIFY | password hash 필드 추가 |
| `src/api/auth/login.ts` | CREATE | 로그인 엔드포인트 생성 |
| `tests/auth/login.test.ts` | CREATE | 로그인 테스트 작성 |

### Code Changes Summary
- User 모델에 passwordHash 필드 추가
- bcrypt를 사용한 비밀번호 검증 함수 구현
- JWT 토큰 생성 로직 추가
```

## Phase 3: 컨텍스트 관리

### 3.1 컨텍스트 상태 확인

작업 중 컨텍스트 사용량이 높아지면 사용자에게 선택지 제공:

```
⚠️ 컨텍스트 사용량이 높습니다.

어떻게 진행하시겠습니까?
1. 계속 진행 - 현재 상태로 작업 계속
2. 문서 저장 후 초기화 - Current Work 업데이트 후 /clear
3. 커밋 후 초기화 - 변경사항 커밋하고 /clear
```

### 3.2 저장 후 초기화

선택 시 수행할 작업:

1. **Current Work 섹션 완전히 업데이트**
   - 현재 상태, 다음 단계, 작업 중인 파일 명확히 기록
2. **Changes Made 최신화**
3. **파일 저장**
4. **사용자에게 /clear 안내**

```
✅ 문서가 저장되었습니다.

/clear 후 다음 명령으로 작업을 재개하세요:
"dev-docs/{folder}/{task-name}.md 읽고 작업 계속해줘"
```

### 3.3 컨텍스트 초기화 후 재개

사용자가 문서를 참조하며 작업 재개 요청 시:

1. **해당 작업 문서만 읽기** (~200줄, ~2-3K tokens)
2. **Current Work 섹션 확인**
3. **즉시 작업 재개**

```
📂 dev-docs/auth/login-feature.md 로드 완료

현재 상태: 🔄 IN_PROGRESS (3/7 tasks)
현재 작업: Task 4 - 로그인 API 엔드포인트 (🟢 GREEN 단계)

바로 작업을 재개합니다...
```

## Phase 4: Git Commit 연동

### 4.1 커밋 메시지 자동 구성

작업 문서의 Intent + Changes Made → 커밋 메시지:

```bash
git commit -m "$(cat <<'EOF'
feat(auth): implement JWT-based login endpoint

## Why
사용자 인증을 위한 JWT 기반 로그인 시스템 구현.
세션 기반 대신 JWT를 선택한 이유: 마이크로서비스 확장성 고려.

## What
- User 모델에 passwordHash 필드 추가
- bcrypt를 사용한 비밀번호 검증 함수 구현
- POST /api/auth/login 엔드포인트 구현
- JWT 토큰 생성 및 반환 로직 추가

📋 Task: dev-docs/auth/login-feature.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 4.2 커밋 후 문서 업데이트

커밋 완료 후:

```markdown
## Meta
- **Status**: ✅ COMPLETED (또는 진행 중이면 유지)
- **Last Updated**: [현재 시간]

## Git Commits
| Commit | Date | Message |
|--------|------|---------|
| `abc1234` | 2025-12-04 | feat(auth): implement JWT-based login |
```

### 4.3 커밋 타입 가이드

| Type | 사용 시점 |
|------|----------|
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `refactor` | 리팩토링 (기능 변화 없음) |
| `style` | 코드 스타일 변경 |
| `docs` | 문서 수정 |
| `test` | 테스트 추가/수정 |
| `chore` | 빌드, 설정 등 기타 |

## Phase 5: 작업 완료

### 5.1 완료 처리

모든 Tasks 완료 시:

```markdown
## Meta
- **Status**: ✅ COMPLETED
- **Last Updated**: [현재 시간]
- **Completed**: YYYY-MM-DD

## Progress Tracking

### Tasks
(모두 체크됨)

### Completed
- [x] Task 1: [설명] (2025-12-03)
- [x] Task 2: [설명] (2025-12-04)
- [x] Task 3: [설명] (2025-12-04)
```

### 5.2 아카이브 (선택)

완료된 문서 관리 방법 (사용자 선택):

1. **현재 위치 유지** - 참조용으로 보관
2. **archive 폴더로 이동** - `dev-docs/archive/{folder}/{task-name}.md`
3. **삭제** - Git 히스토리에만 보관

## 대규모 작업 분할

### ~200줄 초과 시 분할

하나의 작업이 ~200줄로 감당 안 될 경우:

```
dev-docs/auth/
├── 01-database-schema.md    # Phase 1: DB 스키마
├── 02-user-model.md         # Phase 2: 모델 구현
├── 03-api-endpoints.md      # Phase 3: API 구현
└── 04-integration-test.md   # Phase 4: 통합 테스트
```

각 파일은 독립적으로 실행 가능한 단위로 구성.

### 분할 문서 연결

각 문서에 연결 정보 포함:

```markdown
## Meta
- **Part**: 2/4
- **Previous**: 01-database-schema.md
- **Next**: 03-api-endpoints.md
- **Parent Task**: 인증 시스템 구현
```

## 기존 규칙 연동

### TDD 원칙 유지

Current Work의 Phase 표시:
- 🔴 **RED**: 실패하는 테스트 작성
- 🟢 **GREEN**: 테스트 통과하는 최소 코드
- 🔵 **REFACTOR**: 코드 개선 (테스트 유지)
- 📦 **COMMIT**: 변경사항 커밋

### CLAUDE.md 연동

프로젝트 전역 컨텍스트는 CLAUDE.md 참조:

```markdown
## Related Docs
- 프로젝트 컨텍스트: `dev-docs/CLAUDE.md`
- 개발 워크플로우: `dev-docs/DEVELOPMENT.md`
```

## Quick Reference

### 문서 생성
```
"[작업명] 작업을 시작할게. dev-docs/[폴더명]/[파일명].md로 문서 만들어줘"
```

### 작업 재개
```
"dev-docs/[폴더명]/[파일명].md 읽고 작업 계속해줘"
```

### 컨텍스트 저장
```
"현재 작업 상태 저장해줘"
```

### 커밋 요청
```
"지금까지 변경사항 커밋해줘"
```

## 체크리스트

### 문서 생성 시
- [ ] 폴더/파일 위치 결정
- [ ] Intent 섹션 작성 (Why, Expected Outcome)
- [ ] Tasks 목록 작성
- [ ] Status: 🆕 NOT_STARTED

### 작업 중
- [ ] Status: 🔄 IN_PROGRESS
- [ ] Current Work 최신 상태 유지
- [ ] Progress Tracking 업데이트
- [ ] Changes Made 누적

### 컨텍스트 초기화 전
- [ ] Current Work 완전히 업데이트
- [ ] 다음 단계 명확히 기록
- [ ] 작업 중인 파일 목록 확인

### 커밋 시
- [ ] Intent → Why 섹션 반영
- [ ] Changes Made → What 섹션 반영
- [ ] 커밋 후 문서에 Commit Reference 추가

### 완료 시
- [ ] Status: ✅ COMPLETED
- [ ] 모든 Tasks 체크
- [ ] 최종 Git Commits 기록
