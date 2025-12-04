# TDD MVP Planner Skill

A domain-neutral skill for transforming architecture documents into validated, executable development plans and task lists following Test-Driven Development (TDD) methodology.

## Overview

This skill provides a systematic 10-phase workflow for converting technical specifications and architecture documents into comprehensive development documentation:

**All documents are saved in the project's `dev-docs/` folder:**

- **dev-docs/PLAN.md**: Strategic milestone-based implementation plan with dependency analysis, risk assessment, and resource allocation
- **dev-docs/TODO.md**: Tactical task list with TDD-structured tasks (RED → GREEN → REFACTOR → COMMIT)
- **dev-docs/CLAUDE.md**: Project-specific Claude Code context with tech stack, commands, and development rules
- **dev-docs/DEVELOPMENT.md**: Development workflow guide with TDD cycle, commit conventions, and testing strategy
- **Codex Validation**: Automated quality assurance and completeness verification

## Key Features

### Domain Neutral
- **Not tied to any specific technology, framework, or domain**
- Applicable to backend, frontend, full-stack, data pipelines, microservices, and more
- Provides methodology and process, not domain-specific solutions

### TDD-Driven
- **Enforces test-first development** at the planning stage
- Every implementation task paired with corresponding test tasks
- Correct cycle order: RED → GREEN → REFACTOR → COMMIT
- Explicit test coverage targets and strategies

### Automated Validation
- **Codex integration** for objective quality assessment
- Validates completeness, structure, feasibility, and TDD compliance
- Identifies critical issues and suggests improvements
- Iterative refinement until validation passes

### Comprehensive Planning
- **Context gathering** through targeted questions
- **Milestone decomposition** with dependency graph
- **Three-point time estimation** for realistic scheduling
- **Risk analysis** with concrete mitigation strategies
- **Quality gates** and success metrics

## When to Use

Use this skill when:
- Starting a new project with an architecture document
- Converting technical specifications into actionable plans
- Establishing TDD-compliant development workflows
- Creating comprehensive task breakdowns for MVP delivery
- Requiring validated project plans with quality assurance

## Project Types Supported

✅ Backend API systems
✅ Frontend applications
✅ Full-stack platforms
✅ Data pipelines
✅ Microservices architectures
✅ Monolithic applications
✅ Mobile applications
✅ Desktop applications

## Quick Start

### Prerequisites

- Architecture document or technical specification
- Project context (team size, timeline, quality goals)
- Codex CLI installed (for validation)

### Basic Usage

1. **Provide Architecture Document**
   ```
   "I have an architecture document for [project type]. I need to create a development plan and task list."
   ```

2. **Answer Context Questions**
   - Project type
   - Team size and experience
   - Timeline constraints
   - Quality targets

3. **Skill Generates PLAN.md v1.0**
   - Strategic milestone plan
   - Dependency graph
   - Time estimates
   - Risk analysis

4. **Codex Validates PLAN.md**
   - Automated quality check
   - Critical issues identified
   - Improvements suggested

5. **PLAN.md Refined to v2.0**
   - Issues resolved
   - Changes documented
   - Re-validated

6. **Skill Generates TODO.md v1.0**
   - Tactical task breakdown
   - TDD-structured tasks
   - Time estimates per task

7. **Codex Validates TODO.md**
   - TDD compliance verified
   - Completeness checked
   - Time estimates validated

8. **TODO.md Refined to v2.0**
   - Final refinements
   - Ready for execution

### Example Command

```bash
# After generating PLAN.md
cat PLAN.md | codex exec -m gpt-5-codex \
  --config model_reasoning_effort="medium" \
  --sandbox read-only

# After generating TODO.md
cat TODO.md | codex exec -m gpt-5-codex \
  --config model_reasoning_effort="medium" \
  --sandbox read-only
```

## Workflow Phases

### Phase 1: Context Gathering
Collect essential project information through targeted questions:
- Project type and architecture document
- Team size and TDD experience
- Timeline constraints
- Quality targets and priorities

### Phase 2: PLAN.md Generation (v1.0)
Create strategic milestone plan:
- Milestone decomposition (M0-MN)
- Dependency graph with critical path
- Three-point time estimation
- Risk analysis with mitigation strategies
- Test strategy definition

### Phase 3: PLAN.md Validation
Codex automated validation:
- Completeness check
- Structure verification
- Feasibility assessment
- TDD compliance review

### Phase 4: PLAN.md Refinement (v2.0)
Address validation feedback:
- Resolve critical issues
- Apply improvements
- Update version and change log
- Re-validate until EXIT CODE 0

### Phase 5: TODO.md Generation (v1.0)
Transform plan into tasks:
- Task decomposition (0.5-4.0h per task)
- TDD cycle application (RED → GREEN → REFACTOR → COMMIT)
- Task categorization and time estimation
- Dependency ordering

### Phase 6: TODO.md Validation
Codex automated validation:
- Task granularity check
- TDD compliance verification
- Completeness assessment
- Time estimate validation

### Phase 7: TODO.md Refinement (v2.0)
Finalize task list:
- Resolve validation issues
- Apply improvements
- Final validation
- User approval

## Documentation Structure

```
tdd-mvp-planner/
├── SKILL.md                      # Main skill file (10-phase workflow)
├── README.md                     # This file
└── references/                   # Reference materials
    ├── plan-template.md          # PLAN.md complete template
    ├── todo-template.md          # TODO.md complete template
    ├── tdd-principles.md         # TDD best practices
    ├── progress-tracking.md      # Progress bar integration
    └── validation-guide.md       # Codex validation guide
```

**Output Structure** (프로젝트에 생성되는 파일):
```
project-root/
└── dev-docs/                     # 모든 개발 문서 저장 위치
    ├── PLAN.md                   # 전략적 마일스톤 계획
    ├── TODO.md                   # 상세 작업 목록
    ├── CLAUDE.md                 # Claude Code 컨텍스트
    └── DEVELOPMENT.md            # 개발 워크플로우 가이드
```

## Templates

### PLAN.md Template Structure
- Version and metadata
- Project overview and principles
- Dependency graph
- Milestones (M0-MN) with:
  - Goals and deliverables
  - Test-first approach
  - Time estimates (3-point)
  - Risk analysis
  - Success validation
- Risk analysis summary
- Timeline and resources
- Quality gates

### TODO.md Template Structure
- Version and metadata
- Usage instructions
- Task format and categories
- Milestones with tasks:
  - TDD cycle tasks (RED → GREEN → REFACTOR → COMMIT)
  - Integration and E2E tests
  - Documentation tasks
  - Git commit tasks
- Summary tables
- Execution order
- Quality gates

## Best Practices

### Milestone Planning
✅ Start with foundation and infrastructure
✅ Respect component dependencies strictly
✅ Include explicit test strategies
✅ Define clear deliverables
✅ Allocate buffer time (20-30%)

### Task Breakdown
✅ Follow TDD cycle for all implementations
✅ Write specific, action-oriented descriptions
✅ Include git commit as explicit tasks
✅ Group related tasks within components
✅ Verify totals match milestone estimates

### Validation
✅ Run Codex validation for both PLAN and TODO
✅ Address all critical issues before proceeding
✅ Document changes between versions
✅ Re-validate after significant modifications
✅ Obtain user approval before finalizing

## Deliverables

Upon completion of all phases:

1. **PLAN.md (validated)**
   - Strategic milestone plan
   - Dependency graph
   - Risk analysis
   - Resource allocation
   - Codex validated (EXIT CODE 0)

2. **TODO.md (validated)**
   - Complete task list (280-400+ tasks typical)
   - TDD-structured tasks
   - Time estimates (~500-800h for MVPs)
   - Execution order
   - Codex validated (EXIT CODE 0)

3. **Validation Reports**
   - Codex outputs
   - Resolution summaries
   - Version change logs

4. **Execution Guidance**
   - Recommended starting point
   - Critical path emphasis
   - Risk monitoring suggestions

## Quality Metrics

### PLAN.md Quality
- ✅ All architecture components mapped
- ✅ No circular dependencies
- ✅ Realistic time estimates
- ✅ Comprehensive risk analysis
- ✅ Explicit test strategies
- ✅ Codex score ≥ 75

### TODO.md Quality
- ✅ All deliverables have tasks
- ✅ TDD compliance (test before code)
- ✅ Task granularity (0.5-4.0h)
- ✅ Time totals match PLAN
- ✅ Clear execution order
- ✅ Codex score ≥ 75

## Success Criteria

**Project Ready for Execution When**:
- ✅ PLAN.md validated (EXIT CODE 0)
- ✅ TODO.md validated (EXIT CODE 0)
- ✅ Zero critical issues
- ✅ User approval obtained
- ✅ Team aligned on approach
- ✅ Clear starting point identified

## Common Use Cases

### New Project Kickoff
1. Provide architecture document
2. Answer context questions
3. Generate validated PLAN and TODO
4. Begin development with first task

### MVP Planning
1. Define MVP scope in architecture
2. Use skill to create execution plan
3. Focus on P0 and P1 milestones
4. Defer P2 tasks to post-MVP

### Team Onboarding
1. Use PLAN.md for project overview
2. Use TODO.md for work assignment
3. TDD tasks provide clear guidance
4. Documentation tasks ensure knowledge transfer

### Project Estimation
1. Generate TODO.md for accurate task count
2. Use time estimates for realistic scheduling
3. Apply buffer for unknowns
4. Present to stakeholders with confidence

## Tips for Success

### For Best Results
- **Provide detailed architecture**: More detail = better planning
- **Answer questions honestly**: Realistic context = realistic plans
- **Address all critical issues**: Don't skip validation feedback
- **Review with team**: Get team buy-in on approach
- **Start small**: Focus on P0 milestones for MVP

### Common Pitfalls to Avoid
- ❌ Skipping context gathering questions
- ❌ Ignoring Codex validation feedback
- ❌ Underestimating time (be realistic)
- ❌ Skipping buffer time allocation
- ❌ Not following TDD cycle in tasks
- ❌ Vague task descriptions
- ❌ Missing test or documentation tasks

## Troubleshooting

### Validation Keeps Failing
- Review critical issues carefully
- Address each issue specifically
- Don't skip improvements
- Re-validate after changes
- Ask for clarification if needed

### Time Estimates Seem Off
- Calibrate based on team velocity
- Add buffer for unknowns (20-30%)
- Account for meetings, reviews
- Include debugging time
- Be realistic, not optimistic

### Tasks Too Large/Small
- Split tasks > 4h into smaller units
- Merge tasks < 0.5h into logical groups
- One task = one responsibility
- Clear completion criteria

### Missing Components
- Review architecture document thoroughly
- Check all requirements captured
- Verify security/performance included
- Ensure testing infrastructure planned

## Support and Resources

### Reference Materials
- `references/plan-template.md`: Complete PLAN.md structure
- `references/todo-template.md`: Complete TODO.md structure
- `references/tdd-principles.md`: TDD methodology deep-dive
- `references/validation-guide.md`: Codex usage and troubleshooting

### External Resources
- Kent Beck - "Test Driven Development: By Example"
- Martin Fowler - "Refactoring"
- Robert C. Martin - "Clean Code"
- TDD Katas for practice

## Version History

### v1.0 (Current)
- Initial release
- 7-phase workflow
- PLAN.md and TODO.md generation
- Codex validation integration
- Comprehensive templates and guides
- Domain-neutral methodology

## License

See LICENSE.txt for complete terms.

## Contributing

This is a domain-neutral skill. Feedback and improvements welcome:
- Suggest template enhancements
- Share validation experiences
- Report workflow issues
- Propose methodology improvements

## Acknowledgments

Created based on requirements in `tdd-mvp-planner-requirements.md`.

Inspired by:
- Test-Driven Development methodology (Kent Beck)
- SOLID principles (Robert C. Martin)
- Agile estimation techniques
- Project management best practices

---

**Ready to transform your architecture into an executable plan?**

Start by providing your architecture document and answering a few context questions. Within minutes, you'll have validated PLAN.md and TODO.md ready for TDD-driven development.
