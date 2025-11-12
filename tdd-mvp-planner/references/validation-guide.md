# Codex Validation Guide

This guide explains how to use Codex for automated validation of PLAN.md and TODO.md documents, interpret results, and address identified issues.

---

## Table of Contents

1. [Codex Overview](#codex-overview)
2. [PLAN.md Validation](#planmd-validation)
3. [TODO.md Validation](#todomd-validation)
4. [Interpreting Results](#interpreting-results)
5. [Addressing Issues](#addressing-issues)
6. [Common Issues & Solutions](#common-issues--solutions)
7. [Best Practices](#best-practices)

---

## Codex Overview

### What is Codex?

Codex is an AI-powered code analysis tool that provides:
- Automated quality validation
- Consistency checking
- Completeness verification
- Best practice recommendations
- Security and performance insights

### Why Use Codex for Validation?

**Benefits**:
- **Objective Analysis**: Unbiased review of planning documents
- **Comprehensive**: Catches issues humans might miss
- **Consistent**: Same standards applied every time
- **Fast**: Instant feedback on large documents
- **Learning**: Improves planning skills over time

**Use Cases**:
- Initial validation of generated plans
- Pre-review quality gates
- Continuous improvement feedback
- Team alignment on standards

### Codex Configuration

**Model Selection**:
- `gpt-5-codex`: Recommended for planning documents
- Reasoning effort: `medium` (balanced speed/quality)
- Sandbox: `read-only` (safe analysis mode)

---

## PLAN.md Validation

### Validation Command

```bash
cat PLAN.md | codex exec -m gpt-5-codex \
  --config model_reasoning_effort="medium" \
  --sandbox read-only
```

**Parameters**:
- `cat PLAN.md`: Read the plan file
- `codex exec`: Execute Codex analysis
- `-m gpt-5-codex`: Use GPT-5 Codex model
- `--config model_reasoning_effort="medium"`: Balanced analysis
- `--sandbox read-only`: Safe read-only mode (no file modifications)

### Validation Criteria

#### 1. Completeness

**What Codex Checks**:
- All architecture components mapped to milestones
- Security requirements addressed
- Performance requirements included
- Test strategy explicitly defined
- All dependencies documented
- Risk analysis comprehensive

**Critical Issues**:
```
❌ Missing security milestone for authentication
❌ No test strategy defined for M3
❌ Architecture component "Payment Gateway" not mapped
❌ Performance requirements not addressed
```

**How to Fix**:
- Review architecture document
- Identify missing components
- Add corresponding milestones
- Define test strategies
- Document all requirements

#### 2. Structure

**What Codex Checks**:
- Milestone dependencies are logical
- No circular dependencies exist
- Critical path identified correctly
- Parallel work opportunities noted
- Dependency graph matches milestone descriptions

**Critical Issues**:
```
❌ Circular dependency: M3 depends on M4, M4 depends on M3
❌ Critical path not identified
❌ M5 depends on M6 but M6 comes after M5
❌ Dependency graph missing
```

**How to Fix**:
- Draw dependency graph
- Verify logical order
- Identify critical path
- Resolve circular dependencies
- Reorder milestones if needed

#### 3. Feasibility

**What Codex Checks**:
- Time estimates are realistic (not overly optimistic)
- Resource allocation is appropriate
- Buffer time included for unknowns
- Risk mitigation strategies are actionable
- Timeline accounts for dependencies

**Critical Issues**:
```
❌ M2 estimated at 1 week but includes 80 hours of work (with 2 developers = 40h/week)
❌ No buffer time allocated
❌ Risk mitigation "hire more developers" not actionable
❌ Pessimistic estimate = optimistic estimate (no uncertainty)
```

**How to Fix**:
- Review time estimates (use 3-point estimation)
- Add 20-30% buffer for complex milestones
- Calculate hours per developer realistically
- Make mitigation strategies concrete and actionable
- Account for meetings, reviews, unknowns

#### 4. TDD Compliance

**What Codex Checks**:
- Test-first approach specified for each milestone
- Coverage targets defined
- Test strategy detailed (unit, integration, E2E)
- Testing infrastructure milestone included
- Test types matched to milestone purpose

**Critical Issues**:
```
❌ No test coverage target specified for M3
❌ Test strategy says "write tests" (too vague)
❌ No testing infrastructure milestone
❌ M2 (Security) has no security test strategy
```

**How to Fix**:
- Define explicit coverage targets (e.g., "90%+ unit tests")
- Specify test types for each milestone
- Add concrete test strategy (not just "test it")
- Include testing infrastructure early (M1)
- Add security/performance testing where appropriate

### Sample PLAN.md Validation Output

```
CODEX VALIDATION REPORT - PLAN.md
==================================

EXIT CODE: 1 (Issues Found)

CRITICAL ISSUES (3)
-------------------

1. Missing Security Milestone
   Location: Milestone section
   Issue: Architecture document specifies OAuth2 authentication but no
          security milestone exists
   Impact: Critical security requirement not planned
   Fix: Add M2: Security & Authentication milestone

2. Circular Dependency Detected
   Location: Dependency graph
   Issue: M4 depends on M5, but M5 depends on M4
   Impact: Impossible execution order, will block development
   Fix: Restructure dependencies or split milestones

3. Unrealistic Time Estimate
   Location: M3 duration
   Issue: M3 estimated at 1 week with 120 hours of tasks (2 devs = 80h/week)
   Impact: Schedule will slip, team will be pressured
   Fix: Increase duration to 1.5-2 weeks or reduce scope

IMPROVEMENTS (4)
----------------

1. Add Buffer Time
   Suggestion: Current plan has 0% buffer. Recommend 20-30% buffer.
   Benefit: Accommodates unknowns, reduces schedule risk

2. Specify Test Strategy Details
   Suggestion: Test strategy is vague. Add specific test types and
               coverage targets for each milestone.
   Benefit: Clear quality expectations, measurable progress

3. Expand Risk Mitigation
   Suggestion: Risk "technology learning curve" has mitigation "training".
               Make more specific: "2-day onboarding, pair programming,
               code reviews"
   Benefit: Actionable mitigation, trackable progress

4. Add Success Metrics
   Suggestion: Define quantifiable success metrics for each milestone
   Benefit: Objective completion criteria, clear expectations

RECOMMENDED CHANGES
-------------------

1. Add M2: Security & Authentication (P0, 2 weeks)
   - OAuth2 integration
   - Session management
   - Security testing
   - Coverage target: 95%+

2. Restructure M4-M5 Dependencies
   Option A: Make M4 depend on M3, M5 depend on M4
   Option B: Split M4 into M4a and M4b

3. Adjust M3 Timeline
   From: 1 week
   To: 2 weeks (or reduce scope by 40 hours)

4. Add 20% buffer to total timeline
   From: 12 weeks
   To: 14.4 weeks (round to 15 weeks)

VALIDATION SCORE: 72/100
========================

Completeness:    ████████░░ 80%
Structure:       ██████░░░░ 60%
Feasibility:     ███████░░░ 70%
TDD Compliance:  ████████░░ 75%

RECOMMENDATION: Address 3 critical issues before proceeding
```

---

## TODO.md Validation

### Validation Command

```bash
cat TODO.md | codex exec -m gpt-5-codex \
  --config model_reasoning_effort="medium" \
  --sandbox read-only
```

### Validation Criteria

#### 1. Task Granularity

**What Codex Checks**:
- Tasks follow 1-day completion rule (0.5-4.0h)
- No oversized tasks (> 4h without justification)
- No undersized tasks (< 0.5h, consider merging)
- Clear completion criteria for each task
- Single responsibility per task

**Critical Issues**:
```
❌ Task "Implement authentication system" is 8h (too large)
❌ Task "Import library" is 0.1h (too small)
❌ Task description "Fix bugs" is vague (unclear completion criteria)
❌ Task "Implement login and registration" has multiple responsibilities
```

**How to Fix**:
- Split large tasks (> 4h) into smaller units
- Merge small tasks (< 0.5h) into logical groups
- Make task descriptions specific and action-oriented
- One task = one responsibility
- Define clear "done" criteria

#### 2. TDD Compliance

**What Codex Checks**:
- Every [GREEN] task has a preceding [RED] task
- Tests written before implementation
- Correct cycle: RED → GREEN → REFACTOR → COMMIT
- No [GREEN] tasks without corresponding tests
- Test coverage tasks included

**Critical Issues**:
```
❌ [GREEN] Implement user login (1.5h) - No preceding [RED] task
❌ [RED] task comes after [GREEN] task (reversed order)
❌ [REFACTOR] without preceding [GREEN] (no implementation yet)
❌ Missing test tasks for M3 deliverables
```

**How to Fix**:
- Add [RED] task before every [GREEN] task
- Reorder tasks to follow RED → GREEN → REFACTOR → COMMIT
- Remove [REFACTOR] tasks that have no implementation
- Ensure every feature has corresponding test tasks
- Verify test/implementation ratio (target ≥ 1:1.5)

#### 3. Completeness

**What Codex Checks**:
- All PLAN.md deliverables have corresponding tasks
- Integration tests included
- E2E tests for critical paths
- Security tests for sensitive features
- Documentation tasks present
- Git commit tasks included

**Critical Issues**:
```
❌ PLAN.md deliverable "Rate limiting" has no TODO tasks
❌ No integration tests for M3
❌ No E2E tests defined
❌ Missing documentation tasks
❌ No commit tasks for features
```

**How to Fix**:
- Map each PLAN.md deliverable to TODO tasks
- Add integration test tasks for each milestone
- Include E2E test tasks for user workflows
- Add documentation tasks throughout
- Include git commit tasks for each feature

#### 4. Time Estimates

**What Codex Checks**:
- Estimates are realistic (not overly optimistic)
- Total task time matches milestone estimates
- Time includes testing, debugging, documentation
- Estimates account for team experience level
- Complex tasks have appropriate time allocation

**Critical Issues**:
```
❌ M2 tasks total 120h but PLAN.md estimates 160h (40h discrepancy)
❌ Task "Implement OAuth2" is 1h (likely underestimated)
❌ Test tasks are 0.5h but implementation is 4h (imbalanced)
❌ No time allocated for debugging or rework
```

**How to Fix**:
- Recalculate task totals per milestone
- Increase estimates for complex tasks
- Balance test time with implementation time
- Add buffer for debugging (10-20% of implementation time)
- Adjust based on team experience

#### 5. Dependencies

**What Codex Checks**:
- Tasks in logical execution order
- No circular dependencies
- Blockers explicitly noted
- Parallel work opportunities identified
- Cross-milestone dependencies clear

**Critical Issues**:
```
❌ Task "Use auth middleware" before "Implement auth middleware"
❌ Circular dependency between Task 45 and Task 48
❌ M3 tasks start before M2 tasks complete (blocking dependency)
❌ No indication which tasks can be parallel
```

**How to Fix**:
- Reorder tasks to respect dependencies
- Note blocking tasks explicitly
- Mark tasks that can run in parallel
- Verify milestone order matches dependencies
- Highlight critical path tasks

### Sample TODO.md Validation Output

```
CODEX VALIDATION REPORT - TODO.md
==================================

EXIT CODE: 1 (Issues Found)

CRITICAL ISSUES (5)
-------------------

1. Missing Test Tasks for Implementation
   Location: M3, Tasks 45-52
   Issue: 8 [GREEN] implementation tasks with no preceding [RED] test tasks
   Impact: Violates TDD principles, no test coverage for features
   Fix: Add [RED] test tasks before each [GREEN] implementation task

2. Oversized Task
   Location: M2, Task 23
   Issue: "Implement OAuth2 integration" is 6h (exceeds 4h limit)
   Impact: Cannot complete in one day, unclear progress tracking
   Fix: Split into smaller tasks:
         - Set up OAuth2 provider configuration (1.5h)
         - Implement authorization flow (2h)
         - Implement token exchange (1.5h)
         - Add error handling (1h)

3. Time Estimate Mismatch
   Location: M3 subtotal
   Issue: Tasks total 140h but PLAN.md estimates 160h (20h missing)
   Impact: Schedule will slip, milestone completion uncertain
   Fix: Review tasks for missing work or adjust PLAN.md estimate

4. Incorrect Task Order
   Location: M4, Tasks 67-70
   Issue: Task 68 [GREEN] comes before Task 67 [RED]
   Impact: Implementation before tests violates TDD
   Fix: Reorder to: Task 67 [RED] → Task 68 [GREEN]

5. Missing Integration Tests
   Location: M2 (Security milestone)
   Issue: No integration tests defined for auth system
   Impact: No validation of component interactions
   Fix: Add integration test tasks:
         - Auth + Database integration (2h)
         - Auth + API integration (2h)
         - End-to-end auth flow (3h)

IMPROVEMENTS (6)
----------------

1. Add Task Descriptions
   Suggestion: Many tasks lack detailed descriptions. Add specifics on
               what to test/implement.
   Example: "Write test for login" → "Write test for successful login
            with valid credentials returning JWT token"

2. Include Documentation Tasks
   Suggestion: No documentation tasks in M3-M5. Add [DOC] tasks.
   Benefit: Ensures documentation stays current with implementation

3. Add Security Test Tasks
   Suggestion: M2 is security-focused but has no [SEC] tasks
   Benefit: Explicit security validation, compliance verification

4. Specify Commit Messages
   Suggestion: [COMMIT] tasks don't specify commit message format
   Example: "Commit feature" → "Commit: feat(auth): add JWT authentication"

5. Add E2E Tests
   Suggestion: No E2E tests defined for critical user journeys
   Recommendation: Add 3-5 E2E test tasks for main workflows

6. Balance Test/Implementation Ratio
   Suggestion: Implementation tasks are 65% of total, tests are 25%
   Target: Aim for 40-45% test tasks, 50-55% implementation

RECOMMENDED CHANGES
-------------------

1. Add Missing Test Tasks (HIGH PRIORITY)
   Add [RED] task before each of these [GREEN] tasks:
   - Task 45, 46, 47, 48, 49, 50, 51, 52

   Template:
   - [ ] [RED] Write test for [feature] (1.0h) [RED] {M3}
   - [ ] [GREEN] Implement [feature] (1.5h) [GREEN] {M3}

2. Split Oversized Tasks
   Task 23: "Implement OAuth2 integration" (6h)
   Split into:
   - [ ] Set up OAuth2 config (1.5h) [GREEN] {M2}
   - [ ] Implement authorization flow (2.0h) [GREEN] {M2}
   - [ ] Implement token exchange (1.5h) [GREEN] {M2}
   - [ ] Add OAuth2 error handling (1.0h) [GREEN] {M2}

3. Add Integration Tests to M2
   - [ ] Write auth + database integration test (2.0h) [INT] {M2}
   - [ ] Write auth + API integration test (2.0h) [INT] {M2}
   - [ ] Write end-to-end auth flow test (3.0h) [E2E] {M2}

4. Reorder M4 Tasks
   Current: Task 68 [GREEN] → Task 67 [RED]
   Fixed: Task 67 [RED] → Task 68 [GREEN]

5. Add Documentation Tasks
   - [ ] Document authentication API (1.5h) [DOC] {M2}
   - [ ] Document M3 feature usage (1.0h) [DOC] {M3}
   - [ ] Update architecture docs (1.0h) [DOC] {M5}

6. Reconcile M3 Time Estimates
   Current: 140h tasks, PLAN expects 160h
   Options:
   A. Add 20h of missing tasks (tests, docs, etc.)
   B. Update PLAN.md M3 estimate to 140h
   C. Combination (add 10h tasks, reduce PLAN to 150h)

TDD COMPLIANCE ANALYSIS
=======================

Total Tasks: 284
[RED] Tasks: 82 (29%)
[GREEN] Tasks: 118 (42%)
[REFACTOR] Tasks: 34 (12%)
[COMMIT] Tasks: 28 (10%)
Other: 22 (7%)

TDD Compliance Issues:
- 15 [GREEN] tasks without preceding [RED] task
- 3 [RED] tasks after [GREEN] tasks (reversed)
- 2 [REFACTOR] tasks without implementation

Test/Implementation Ratio: 1:1.44 ✅ (Target: ≥ 1:1.5)

VALIDATION SCORE: 68/100
========================

Task Granularity: ██████░░░░ 65%
TDD Compliance:   ████░░░░░░ 45%  ← Critical
Completeness:     ███████░░░ 75%
Time Estimates:   ██████░░░░ 60%
Dependencies:     ████████░░ 80%

RECOMMENDATION: Address 5 critical issues, especially TDD compliance
```

---

## Interpreting Results

### Exit Codes

- **EXIT CODE 0**: Validation passed, no critical issues
- **EXIT CODE 1**: Critical issues found, must address before proceeding
- **EXIT CODE 2**: Codex error (syntax error in document, etc.)

### Issue Severity Levels

**Critical Issues** (Must Fix):
- Blocks development
- Violates core principles (TDD)
- Creates impossible situations (circular dependencies)
- Missing required components
- Severe time estimate problems

**Improvements** (Should Fix):
- Enhances quality
- Improves clarity
- Reduces risk
- Follows best practices
- Increases confidence

**Recommendations** (Optional):
- Nice-to-have enhancements
- Additional considerations
- Alternative approaches
- Optimization opportunities

### Validation Scores

**Score Ranges**:
- **90-100**: Excellent, ready for execution
- **75-89**: Good, minor improvements recommended
- **60-74**: Adequate, address critical issues
- **Below 60**: Needs significant revision

**Score Components**:
- Each criterion weighted equally by default
- Critical issues reduce score significantly
- Improvements suggest score improvement potential

---

## Addressing Issues

### Step-by-Step Resolution Process

#### 1. Prioritize Issues

**Order of Resolution**:
1. Critical issues (blocking)
2. Structural problems (dependencies, order)
3. Completeness gaps (missing components)
4. Quality improvements (clarity, detail)
5. Optional enhancements

#### 2. Resolve Critical Issues

**For Each Critical Issue**:
1. **Understand**: Read issue description carefully
2. **Locate**: Find exact location in document
3. **Analyze**: Understand root cause
4. **Fix**: Apply recommended change or equivalent solution
5. **Verify**: Check fix resolves issue

#### 3. Apply Improvements

**For Each Improvement**:
1. **Evaluate**: Is this improvement valuable?
2. **Prioritize**: How important vs. effort required?
3. **Implement**: Apply if valuable
4. **Document**: Note change in version history

#### 4. Re-validate

After making changes:
1. Update version number
2. Document changes in "Key Changes" section
3. Run Codex validation again
4. Repeat until EXIT CODE 0

#### 5. Obtain Approval

Once validation passes:
1. Review changes with team
2. Get stakeholder sign-off
3. Mark document as "Validated"
4. Proceed to next phase

### Common Resolution Patterns

#### Missing Components

**Issue**: Architecture component not mapped to milestone

**Resolution**:
1. Identify missing component in architecture doc
2. Determine appropriate milestone (new or existing)
3. Add component to deliverables
4. Create corresponding TODO tasks
5. Update time estimates

#### Time Estimate Mismatches

**Issue**: Task totals don't match milestone estimates

**Resolution**:
1. Recalculate task totals
2. Compare with PLAN.md estimate
3. Options:
   - Add missing tasks (if work was forgotten)
   - Adjust PLAN.md estimate (if overestimated)
   - Split the difference (combination)
4. Document decision rationale

#### TDD Violations

**Issue**: Implementation tasks without test tasks

**Resolution**:
1. For each [GREEN] task without [RED] task:
2. Add [RED] task before it (test first)
3. Estimate test time (typically 50-100% of implementation time)
4. Update milestone subtotals
5. Verify RED → GREEN → REFACTOR → COMMIT order

#### Circular Dependencies

**Issue**: Milestone A depends on B, B depends on A

**Resolution**:
1. Analyze dependency reasons
2. Options:
   - Split one milestone (break cycle)
   - Reorder tasks (change dependency)
   - Merge milestones (remove dependency)
3. Update dependency graph
4. Verify new order is logical

---

## Common Issues & Solutions

### PLAN.md Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Missing security milestone | Oversight during breakdown | Add M2: Security & Quality (P0) |
| Circular dependencies | Incorrect dependency analysis | Reorder milestones or split components |
| Optimistic time estimates | Not accounting for buffer | Add 20-30% buffer, use 3-point estimation |
| Vague test strategy | Generic planning | Specify test types, coverage targets, tools |
| Missing risk mitigation | Incomplete risk analysis | Add concrete, actionable mitigation strategies |
| No critical path | Incomplete dependency analysis | Identify longest dependent chain |

### TODO.md Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Tests after implementation | Not following TDD | Reorder: [RED] before [GREEN] |
| Oversized tasks | Insufficient breakdown | Split into 0.5-4.0h tasks |
| Missing integration tests | Focus on unit tests only | Add [INT] tasks for cross-component validation |
| Time estimate mismatch | Calculation error or missing tasks | Recalculate totals, add missing work |
| Vague task descriptions | Generic task creation | Add specific details, acceptance criteria |
| Missing documentation | Focused on code only | Add [DOC] tasks throughout |

---

## Best Practices

### Before Validation

**Preparation**:
1. Complete all sections of document
2. Run spell check and grammar check
3. Verify all internal references (milestone IDs, etc.)
4. Check math (time calculations, totals)
5. Review against templates

### During Validation

**Execution**:
1. Run validation in quiet environment
2. Save validation output to file for reference
3. Read entire output before making changes
4. Take notes on patterns (repeat issues)
5. Ask for clarification if issues unclear

### After Validation

**Follow-up**:
1. Track resolution of each issue
2. Document decisions made
3. Update version and change log
4. Re-validate after changes
5. Archive validation reports

### Continuous Improvement

**Learning**:
1. Review past validation issues
2. Identify recurring problems
3. Update planning process to prevent issues
4. Share learnings with team
5. Refine templates based on feedback

### Validation Cadence

**Recommended Schedule**:
- PLAN.md v1.0: Initial validation
- PLAN.md v2.0: After addressing issues
- TODO.md v1.0: Initial validation
- TODO.md v2.0: After addressing issues
- Re-validation: After any major changes

---

## Troubleshooting Codex

### Common Codex Errors

#### Error: "Cannot parse document"

**Cause**: Syntax error in markdown (unclosed code block, malformed table)

**Solution**:
1. Check for unclosed ``` code blocks
2. Verify table formatting (pipes aligned)
3. Check for special characters in YAML frontmatter
4. Validate markdown with linter

#### Error: "Model timeout"

**Cause**: Document too large or complex

**Solution**:
1. Split document into sections
2. Validate each section separately
3. Reduce reasoning effort to "low"
4. Simplify complex sections

#### Error: "Insufficient context"

**Cause**: Document references external files not provided

**Solution**:
1. Include referenced content inline (or summarize)
2. Provide external files to Codex
3. Add context in document itself

### Getting Better Results

**Tips for Effective Validation**:
1. **Clear structure**: Use consistent formatting
2. **Complete information**: Don't leave sections empty
3. **Specific details**: Avoid vague descriptions
4. **Proper formatting**: Follow markdown best practices
5. **Reasonable size**: Split very large documents

---

## Example Validation Workflow

### Complete Workflow

```
Phase 3: PLAN.md Validation
├─ 1. Generate PLAN.md v1.0
├─ 2. Run Codex validation
│   └─ cat PLAN.md | codex exec -m gpt-5-codex --config model_reasoning_effort="medium" --sandbox read-only
├─ 3. Review validation output
│   ├─ Note EXIT CODE (0 = pass, 1 = issues)
│   ├─ Read critical issues
│   └─ Review improvements
├─ 4. Address critical issues
│   ├─ Fix issue #1: Add missing security milestone
│   ├─ Fix issue #2: Resolve circular dependency
│   └─ Fix issue #3: Adjust time estimates
├─ 5. Apply valuable improvements
│   ├─ Add buffer time
│   └─ Specify test strategy details
├─ 6. Update version and change log
│   ├─ Version: 1.0 → 2.0
│   └─ Document changes made
├─ 7. Re-validate
│   └─ cat PLAN.md | codex exec -m gpt-5-codex --config model_reasoning_effort="medium" --sandbox read-only
├─ 8. Verify EXIT CODE 0
└─ 9. Obtain user approval

Phase 4: PLAN.md Refinement Complete
Phase 5: TODO.md Generation (using PLAN.md v2.0)

Phase 6: TODO.md Validation
├─ 1. Generate TODO.md v1.0
├─ 2. Run Codex validation
├─ 3. Review validation output
├─ 4. Address critical issues
│   ├─ Add missing test tasks
│   ├─ Fix task order
│   └─ Split oversized tasks
├─ 5. Apply improvements
├─ 6. Update version and change log
├─ 7. Re-validate
├─ 8. Verify EXIT CODE 0
└─ 9. Obtain user approval

Phase 7: TODO.md Refinement Complete
Output: Validated PLAN & TODO ready for execution
```

---

## Conclusion

Codex validation is a powerful tool for ensuring high-quality project plans and task lists. By systematically addressing validation feedback, you create robust, executable plans that lead to successful TDD-driven development.

**Key Takeaways**:
1. Always validate both PLAN.md and TODO.md
2. Address all critical issues before proceeding
3. Apply valuable improvements
4. Re-validate after changes
5. Document all changes in version history
6. Learn from validation feedback
7. Refine planning process over time

**Success Criteria**:
- EXIT CODE 0 (validation passed)
- Zero critical issues
- Validation score ≥ 75
- User approval obtained
- Team alignment achieved

With validated plans and task lists, you're ready for confident, TDD-driven development execution.
