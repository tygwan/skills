# Progress Tracking Reference

README 상단에 개발 진행상황을 표시하는 Progress Bar 시스템입니다.

## Progress Bar 형식

### 기본 템플릿

```markdown
> **Development Progress**
> ```
> Overall:  [████████░░] 80% (24/30 tasks)
> v0.1.0:   [██████████] 100% Complete
> v0.2.0:   [██████░░░░] 60%  In Progress
> v0.3.0:   [░░░░░░░░░░] 0%   Pending
> ```
> **Current Phase**: GREEN | **Last Updated**: YYYY-MM-DD
```

### Progress Bar 문자

| 문자 | 의미 | 사용 |
|------|------|------|
| `█` | 완료된 진행률 | 10% 단위로 1개 |
| `░` | 남은 진행률 | 10% 단위로 1개 |
| `[` `]` | Bar 경계 | 고정 |

### 상태 표시

| 상태 | 표시 | 조건 |
|------|------|------|
| Complete | `100% Complete` | 진행률 100% |
| In Progress | `XX%  In Progress` | 0% < 진행률 < 100% |
| Pending | `0%   Pending` | 진행률 0% |

### Phase 표시

| Phase | 설명 |
|-------|------|
| RED | 테스트 작성 중 |
| GREEN | 구현 중 |
| REFACTOR | 리팩토링 중 |
| COMMIT | 커밋 중 |

## 진행률 계산 방법

### TODO.md에서 파싱

```markdown
## Summary by Milestone
| Milestone | Total | Done | Remaining | Progress |
|-----------|-------|------|-----------|----------|
| v0.1.0    | 10    | 10   | 0         | 100%     |
| v0.2.0    | 15    | 9    | 6         | 60%      |
```

### 계산 공식

```
Milestone Progress = (Done / Total) * 100
Overall Progress = (Total Done across all milestones / Total Tasks) * 100
```

### 체크박스 카운트

```markdown
- [x] Completed task  → Done +1
- [ ] Pending task    → Remaining +1
```

## Progress Bar 생성 함수

### Bar 생성 로직

```
1. 진행률을 10으로 나누어 채워진 칸 수 계산
2. 10에서 채워진 칸 수를 빼서 빈 칸 수 계산
3. █를 채워진 칸 수만큼, ░를 빈 칸 수만큼 반복
```

예시:
- 0% → `[░░░░░░░░░░]`
- 30% → `[███░░░░░░░]`
- 75% → `[████████░░]` (반올림)
- 100% → `[██████████]`

## README 업데이트 위치

Progress Bar는 README.md 최상단에 위치해야 합니다:

```markdown
# Project Name

> **Development Progress**
> ```
> Overall:  [████░░░░░░] 40% (12/30 tasks)
> ...
> ```

## Overview
(기존 내용)
```

## 연동 스킬

이 Progress Tracking 시스템은 다음 스킬들과 함께 동작합니다:

| 스킬 | 역할 | 트리거 |
|------|------|--------|
| **tdd-mvp-planner** | Progress Bar 초기화 | TODO.md 생성 완료 시 |
| **test-driven-development** | Progress 업데이트 | COMMIT 단계 완료 시 |
| **finishing-a-development-branch** | Progress 검증 | 브랜치 완료 전 |

## 초기화 (tdd-mvp-planner)

TODO.md 생성 후 README에 초기 Progress Bar 추가:

```markdown
> **Development Progress**
> ```
> Overall:  [░░░░░░░░░░] 0% (0/30 tasks)
> v0.1.0:   [░░░░░░░░░░] 0%   Pending
> v0.2.0:   [░░░░░░░░░░] 0%   Pending
> ```
> **Current Phase**: RED | **Last Updated**: YYYY-MM-DD
```

## 업데이트 (test-driven-development)

COMMIT 완료 후:
1. TODO.md에서 완료된 작업 카운트
2. 각 Milestone별 진행률 계산
3. README Progress Bar 업데이트
4. Current Phase 업데이트

## 검증 (finishing-a-development-branch)

브랜치 완료 전 확인:
- [ ] Overall Progress 100% 확인
- [ ] 모든 Milestone Complete 상태
- [ ] 미완료 작업 없음 경고
