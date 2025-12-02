---
name: tdd-mvp-planner
description: This skill should be used when transforming architecture documents into executable development plans and task lists following TDD methodology. It provides a systematic 7-phase workflow for creating validated PLAN.md and TODO.md documents with Codex verification, applicable to any project type (backend, frontend, full-stack, data pipelines).
---

# TDD MVP Planner

## Overview

Transform architecture documents into actionable development plans and task lists following Test-Driven Development (TDD) principles. This skill provides a domain-neutral methodology for systematic project planning with automated validation.

**Core Philosophy**: Architecture → Strategic PLAN → Tactical TODO → Validated Execution

**Key Deliverables**:
- `PLAN.md`: Strategic milestone plan with dependency graph, risk analysis, and resource allocation
- `TODO.md`: Tactical task list with TDD cycle (RED → GREEN → REFACTOR → COMMIT)
- Codex validation ensuring completeness, feasibility, and TDD compliance

## When to Use

Use this skill when:
- Starting a new project with an architecture document
- Converting technical specifications into executable plans
- Establishing TDD-compliant development workflows
- Creating comprehensive task breakdowns for MVP delivery
- Requiring validated project plans with quality gates

**Applicable to all project types**:
- Backend API systems
- Frontend applications
- Full-stack platforms
- Data pipelines
- Microservices architectures
- Monolithic applications

## Workflow Process

### Phase 1: Context Gathering

Before generating plans, gather essential project context through targeted questions.

#### Collect Project Information

**Project Type**
Ask: "What type of project is this?"
Options: Backend API | Frontend | Full-stack | Data Pipeline | Other

**Architecture Document**
Request: "Please provide the architecture document or technical specification."
Analyze for:
- System components and their roles
- Component dependencies
- External system/API integrations
- Data models and schemas
- Security requirements (authentication, authorization, encryption)
- Performance requirements (throughput, latency)
- Scalability requirements

#### Understand Team Context

**Team Size**
Ask: "What is the development team size?"
Options: 1 (Solo) | 2 | 3-5 | 5+

**TDD Experience**
Ask: "What is the team's TDD experience level?"
Options: Extensive | Moderate | Beginner | Learning

#### Define Constraints

**Timeline**
Ask: "Are there timeline constraints?"
Options: None - Quality first | 3-month MVP | 6-month MVP | 1-year Full Product

**Quality Targets**
Ask: "What is the test coverage goal?"
Options: 70%+ | 80%+ | 90%+ | Varies by component

Ask: "How should priorities be classified?"
Options: P0 (Critical) / P1 (High) / P2 (Medium) | Custom scheme

### Phase 2: PLAN.md Generation (v1.0)

Generate strategic milestone plan following the template structure in `references/plan-template.md`.

#### Apply Milestone Decomposition Strategy

**Foundational Principles**:
1. **Foundation First**: Common infrastructure and utilities before features
2. **Dependency Order**: Respect component dependencies strictly
3. **Incremental Value**: Each milestone delivers independent value
4. **Risk Mitigation**: Address high-risk items early
5. **Parallel Capability**: Enable concurrent work where possible

**Standard Milestone Pattern**:
```
M0: Project Setup (optional)
    - Development environment
    - CI/CD pipeline
    - Code quality tools

M1: Foundation & Core Infrastructure (P0)
    - Exception handling layer
    - Common utilities
    - Configuration management
    - Logging system
    - Test infrastructure

M2: Security & Quality (P0)
    - Authentication/authorization
    - Data validation
    - Security testing
    - Quality gates

M3-MN: Feature Milestones (P0-P2)
    - Major feature units
    - Dependency-ordered
    - Integration tests included

M(N+1): Integration & E2E Testing (P1)
    - System-wide integration
    - E2E scenario testing
    - Performance testing

M(N+2): Deployment & Operations (P1-P2)
    - Deployment automation
    - Monitoring configuration
    - Documentation
    - Production readiness
```

#### Create Dependency Graph

Generate ASCII dependency graph showing:
- Milestone relationships
- Critical path identification
- Parallel execution opportunities
- Blocking dependencies

#### Perform Time Estimation

Use three-point estimation for each milestone:
- **Optimistic**: Best-case scenario (20% probability)
- **Realistic**: Most likely duration (60% probability)
- **Pessimistic**: Worst-case scenario (20% probability)

Calculate expected duration: `(Optimistic + 4×Realistic + Pessimistic) / 6`

#### Conduct Risk Analysis

For each milestone, identify:
- **Technical Risks**: Technology unknowns, integration challenges
- **Schedule Risks**: Resource constraints, dependency delays
- **Resource Risks**: Team availability, skill gaps

Specify mitigation strategies for each risk.

### Phase 3: PLAN.md Validation with Codex

Validate the generated PLAN.md using Codex for automated quality assurance.

#### Run Validation Command

```bash
cat PLAN.md | codex exec -m gpt-5-codex \
  --config model_reasoning_effort="medium" \
  --sandbox read-only
```

#### Validation Criteria

**Completeness**:
- All architecture components reflected
- Security/performance requirements included
- Test strategy explicitly defined

**Structure**:
- Milestone dependencies clear
- No circular dependencies
- Critical path identified

**Feasibility**:
- Time estimates realistic
- Resource planning appropriate
- Risk analysis comprehensive

**TDD Compliance**:
- Test-first approach specified
- Coverage targets set
- Test strategy detailed

#### Parse Validation Results

Codex output format:
```
**Critical Issues**
- Issue #1: [Description and location]
- Issue #2: [Description and location]

**Improvements**
- [Suggested enhancement 1]
- [Suggested enhancement 2]

**Recommended Changes**
1. [Specific actionable change]
2. [Specific actionable change]
```

### Phase 4: PLAN.md Refinement (v2.0)

Address validation feedback and refine PLAN.md.

#### Resolution Process

1. **Prioritize Critical Issues**: Address all critical issues first (blocking)
2. **Review Improvements**: Evaluate and apply valuable suggestions
3. **Update Version**: Increment version number (v1.0 → v2.0)
4. **Document Changes**: Add "Key Changes from v1.0" section
5. **Re-validate**: Run Codex validation again if major changes made

#### Iteration Criteria

Continue refinement until:
- ✅ Codex validation passes (EXIT CODE 0)
- ✅ Zero critical issues
- ✅ User approval obtained
- ✅ Team review completed (if applicable)

### Phase 5: TODO.md Generation (v1.0)

Transform PLAN.md milestones into granular tasks following TDD cycle.

#### Task Decomposition Principles

**Core Rules**:
1. **1-Day Completion**: Each task completable within one day
2. **Single Responsibility**: One task addresses one specific responsibility
3. **Clear Acceptance**: Unambiguous completion criteria
4. **TDD Cycle**: Always follow RED → GREEN → REFACTOR → COMMIT
5. **Independence**: Tasks executable independently when possible

#### Apply TDD Cycle to Each Feature

For every feature implementation:
```
1. [RED] Write test for happy path (0.5-1h)
2. [GREEN] Implement basic functionality (1-2h)
3. [RED] Write test for edge cases (0.5-1h)
4. [GREEN] Handle edge cases (0.5-1h)
5. [RED] Write test for error handling (0.5h)
6. [GREEN] Implement error handling (0.5-1h)
7. [REFACTOR] Extract common logic (0.5h)
8. [COMMIT] Git commit with message (0.5h)
```

#### Task Categorization

Use these category tags:
- `[RED]`: Write failing test
- `[GREEN]`: Implement code to pass test
- `[REFACTOR]`: Improve code structure while tests pass
- `[COMMIT]`: Git commit with descriptive message
- `[DOC]`: Documentation task
- `[INT]`: Integration test
- `[E2E]`: End-to-end test
- `[SEC]`: Security test
- `[PERF]`: Performance test

#### Task Sizing Guidelines

**Appropriate sizes**:
- 0.5h: Simple test or small implementation
- 1.0h: Standard task (default)
- 2.0h: Complex task requiring careful implementation
- 4.0h: Half-day task (maximum, consider splitting)

**Too small** (merge tasks):
```
❌ Import library (0.1h)
❌ Create class (0.1h)
✅ Set up [Component] class with imports (0.5h)
```

**Too large** (split tasks):
```
❌ Implement entire authentication system (8h)
✅ Split into multiple 1-2h TDD cycle tasks
```

### Phase 6: TODO.md Validation with Codex

Validate task list for granularity, TDD compliance, and completeness.

#### Run Validation Command

```bash
cat TODO.md | codex exec -m gpt-5-codex \
  --config model_reasoning_effort="medium" \
  --sandbox read-only
```

#### Validation Criteria

**Task Granularity**:
- All tasks follow 1-day completion rule
- No oversized or undersized tasks
- Clear completion criteria for each task

**TDD Compliance**:
- Every implementation has corresponding test
- Correct order: RED → GREEN → REFACTOR → COMMIT
- Tests written before implementation code

**Completeness**:
- All PLAN.md deliverables reflected
- Integration/E2E tests included
- Documentation tasks present

**Time Estimates**:
- Realistic time allocations
- Accurate total calculation
- Timeline appropriate for team size

**Dependencies**:
- No circular dependencies
- Correct execution order
- Blockers clearly identified

### Phase 7: TODO.md Refinement (v2.0)

Resolve validation issues and finalize task list.

#### Resolution Process

1. **Address Critical Issues**: Fix all blocking issues
2. **Apply Improvements**: Incorporate valuable suggestions
3. **Recalculate Totals**: Verify task counts and time estimates
4. **Update Version**: Increment version (v1.0 → v2.0)
5. **Final Validation**: Run Codex validation once more
6. **Obtain Approval**: Get user confirmation

#### Completion Criteria

Mark complete when:
- ✅ Codex validation passes (EXIT CODE 0)
- ✅ Zero critical issues remain
- ✅ All time calculations accurate
- ✅ User approves final version
- ✅ Ready for development execution

### Phase 8: README Progress Bar 초기화

TODO.md 생성 완료 후, README.md 상단에 Progress Bar를 추가합니다.

> **연동 스킬**: 이 Phase는 `test-driven-development`, `finishing-a-development-branch` 스킬과 함께 동작합니다.

#### Progress Bar 형식

README.md 최상단에 다음 형식으로 추가:

```markdown
> **Development Progress**
> ```
> Overall:  [░░░░░░░░░░] 0% (0/N tasks)
> v0.1.0:   [░░░░░░░░░░] 0%   Pending
> v0.2.0:   [░░░░░░░░░░] 0%   Pending
> ...
> ```
> **Current Phase**: RED | **Last Updated**: YYYY-MM-DD
```

#### 초기화 절차

1. **TODO.md 파싱**: Milestone별 총 Task 수 추출
2. **Progress Bar 생성**: 모든 Milestone 0% 상태로 초기화
3. **README.md 업데이트**: 기존 내용 위에 Progress Bar 추가
4. **타임스탬프**: 현재 날짜로 Last Updated 설정

#### Progress Bar 문자 규칙

| 진행률 | Bar 표시 |
|--------|----------|
| 0% | `[░░░░░░░░░░]` |
| 10% | `[█░░░░░░░░░]` |
| 50% | `[█████░░░░░]` |
| 100% | `[██████████]` |

상세 내용은 `references/progress-tracking.md` 참조.

#### 완료 조건

- ✅ README.md 상단에 Progress Bar 추가됨
- ✅ 모든 Milestone이 0% Pending 상태
- ✅ Total tasks 수가 TODO.md와 일치
- ✅ Current Phase가 RED로 설정됨

## Version Management

**File Naming Convention**:
```
PLAN.md          (current version)
PLAN_v1.md       (archived previous version)
PLAN_v2.md       (archived previous version)

TODO.md          (current version)
TODO_v1.md       (archived previous version)
TODO_v2.md       (archived previous version)
```

**Version Header Format**:
```markdown
## Version: 2.0
**Last Updated**: YYYY-MM-DD
**Review Status**: Codex validated
**Based on**: PLAN.md v2.0

**Key Changes from v1.0**:
- ✅ Fixed: [Issue description]
- ✅ Added: [New content]
- ✅ Improved: [Enhancement]
```

## Templates and Guidelines

Detailed templates and reference materials are provided in the `references/` directory:

- `references/plan-template.md`: Complete PLAN.md structure with examples
- `references/todo-template.md`: Complete TODO.md structure with examples
- `references/tdd-principles.md`: TDD best practices and principles
- `references/validation-guide.md`: Codex validation detailed guide

To use templates, read the appropriate reference file and adapt to project specifics.

## Best Practices

### Milestone Planning

**DO**:
- Start with foundation and infrastructure
- Respect component dependencies strictly
- Include explicit test strategies for each milestone
- Define clear deliverables and acceptance criteria
- Allocate buffer time (20-30%) for unknowns

**DON'T**:
- Jump directly to features without foundation
- Create circular dependencies between milestones
- Underestimate integration and testing time
- Skip risk analysis and mitigation planning
- Assume optimistic timelines

### Task Breakdown

**DO**:
- Follow TDD cycle rigidly for all implementation tasks
- Write specific, action-oriented task descriptions
- Include git commit as explicit tasks
- Group related tasks within components
- Verify total time matches milestone estimates

**DON'T**:
- Combine multiple features in one task
- Skip test-writing tasks to save time
- Use vague descriptions like "implement component"
- Forget documentation and deployment tasks
- Ignore edge cases and error handling

### Validation

**DO**:
- Run Codex validation for both PLAN and TODO
- Address all critical issues before proceeding
- Document all changes between versions
- Re-validate after significant modifications
- Obtain user approval before finalizing

**DON'T**:
- Skip validation to save time
- Ignore "minor" critical issues
- Make undocumented changes
- Assume validation passes without checking
- Proceed without user confirmation

## Verification Checklist

### PLAN.md Completion

Before considering PLAN.md complete:

- [ ] All architecture components mapped to milestones
- [ ] Dependency graph created and validated
- [ ] Critical path identified clearly
- [ ] Time estimates use three-point method
- [ ] Risk analysis covers technical, schedule, and resource risks
- [ ] Test strategy defined for each milestone
- [ ] Coverage targets specified
- [ ] Codex validation passes (EXIT CODE 0)
- [ ] Zero critical issues remain
- [ ] User has reviewed and approved

### TODO.md Completion

Before considering TODO.md complete:

- [ ] All PLAN.md deliverables have corresponding tasks
- [ ] Every task follows TDD cycle structure
- [ ] All tests written before implementation
- [ ] Task sizes within 0.5-4.0h range
- [ ] Clear category tags applied ([RED], [GREEN], etc.)
- [ ] Time estimates realistic and summed correctly
- [ ] Dependencies identified and ordered correctly
- [ ] Integration, E2E, and security tests included
- [ ] Documentation tasks present
- [ ] Git commit tasks included
- [ ] Codex validation passes (EXIT CODE 0)
- [ ] Zero critical issues remain
- [ ] User has reviewed and approved

## Final Output

Upon completion of all phases, deliver:

1. **PLAN.md** (final validated version)
   - Strategic milestone plan
   - Dependency graph
   - Risk analysis
   - Resource allocation
   - Codex validated

2. **TODO.md** (final validated version)
   - Complete task list
   - TDD-structured tasks
   - Time estimates
   - Execution order
   - Codex validated

3. **Validation Reports**
   - Codex validation outputs
   - Resolution summary
   - Version change logs

4. **Execution Guidance**
   - Recommended starting point
   - Critical path emphasis
   - Risk monitoring suggestions

The project is now ready for TDD-driven development execution.
