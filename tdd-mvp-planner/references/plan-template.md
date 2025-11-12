# PLAN.md Template

This template provides the standard structure for creating strategic implementation plans following TDD methodology.

---

```markdown
# {Project Name} - Implementation Plan (TDD-Driven)

## Version: 1.0
**Last Updated**: YYYY-MM-DD
**Review Status**: Draft | Under Review | Validated
**Target Timeline**: X weeks (MVP), Y weeks (with buffer)
**Scope**: Production-ready core system

---

## Overview

[Brief project description and objectives - 2-3 paragraphs]

**Development Philosophy**: Red → Green → Refactor

Core TDD principles for this project:
- Write failing tests first
- Implement minimum code to pass
- Refactor only when green
- Commit only when all tests pass

**Key Principles**:
- [Project-specific principle 1]
- [Project-specific principle 2]
- [Project-specific principle 3]

**Success Criteria**:
- [Measurable success metric 1]
- [Measurable success metric 2]
- [Measurable success metric 3]

---

## Dependency Graph

```
[ASCII dependency graph showing milestone relationships]

Example:
M0 (Setup)
  ↓
M1 (Foundation) ← Critical Path Start
  ↓
M2 (Security) ← Critical Path
  ↓
M3 (Feature A) ← Critical Path
  ↓
M4 (Feature B)
  ↓
M5 (Integration) ← Critical Path End
  ↓
M6 (Deployment)

Parallel opportunities:
- M3 and M4 can proceed in parallel after M2
```

**Critical Path**: M0 → M1 → M2 → M3 → M5 → M6
**Estimated Duration**: X weeks (critical path) + Y weeks (buffer)

---

## Milestones

### M0: Project Setup (Optional)
**Priority**: P1
**Duration**:
- Optimistic: X days
- Realistic: Y days
- Pessimistic: Z days
- **Expected**: W days

**Goal**: [Clear, measurable objective]

**Test-First Approach**:
1. Set up testing framework and verify with sample test
2. Configure CI/CD pipeline with passing test gate
3. Establish code quality tools with automated checks
4. Create development environment documentation

**Deliverables**:
- [ ] Development environment configured and documented
- [ ] CI/CD pipeline operational with test gates
- [ ] Code quality tools integrated (linter, formatter, type checker)
- [ ] Git workflow established and documented
- [ ] Team onboarding documentation complete

**Test Coverage Target**: N/A (infrastructure setup)

**Dependencies**: None

**Risks**:
- [Risk 1]: [Impact description] → Mitigation: [Strategy]
- [Risk 2]: [Impact description] → Mitigation: [Strategy]

**Success Validation**:
- [ ] All team members can run project locally
- [ ] CI/CD pipeline executes successfully
- [ ] Code quality checks pass on sample code

---

### M1: Foundation & Core Infrastructure (P0)
**Priority**: P0 (Critical)
**Duration**:
- Optimistic: X days
- Realistic: Y days
- Pessimistic: Z days
- **Expected**: W days

**Goal**: [Clear, measurable objective focused on foundation]

**Test-First Approach**:
1. Write tests for error handling framework
2. Implement error handling to pass tests
3. Write tests for configuration management
4. Implement configuration system
5. Write tests for logging system
6. Implement logging infrastructure
7. Refactor common patterns
8. Write integration tests for infrastructure

**Deliverables**:
- [ ] Error handling framework with custom exceptions
- [ ] Configuration management system (env-based)
- [ ] Logging infrastructure with structured logging
- [ ] Common utilities (string, date, validation helpers)
- [ ] Test infrastructure (helpers, fixtures, mocks)
- [ ] Database connection management (if applicable)
- [ ] API client framework (if applicable)

**Test Coverage Target**: 90%+ unit tests for all utilities

**Dependencies**: M0 (Project Setup)

**Risks**:
- Technology choice lock-in: High impact → Mitigation: Use abstractions and interfaces
- Performance bottlenecks: Medium impact → Mitigation: Benchmark critical paths early
- Team unfamiliarity: Medium impact → Mitigation: Pair programming sessions

**Success Validation**:
- [ ] All utility functions have passing tests
- [ ] Error scenarios handled gracefully
- [ ] Logging produces structured, searchable output
- [ ] Configuration loads correctly across environments

---

### M2: Security & Quality (P0)
**Priority**: P0 (Critical)
**Duration**:
- Optimistic: X days
- Realistic: Y days
- Pessimistic: Z days
- **Expected**: W days

**Goal**: [Security-focused measurable objective]

**Test-First Approach**:
1. Write tests for authentication flow (happy path)
2. Implement basic authentication
3. Write tests for authentication edge cases
4. Handle authentication errors
5. Write tests for authorization rules
6. Implement authorization logic
7. Write tests for input validation
8. Implement validation layer
9. Write security test suite
10. Refactor security patterns

**Deliverables**:
- [ ] Authentication system (JWT/session-based)
- [ ] Authorization middleware with role-based access
- [ ] Input validation layer
- [ ] Security headers and CORS configuration
- [ ] Rate limiting implementation
- [ ] Security test suite (OWASP coverage)
- [ ] Secrets management integration

**Test Coverage Target**: 95%+ for security code, 100% for critical auth paths

**Dependencies**: M1 (Foundation)

**Risks**:
- Security vulnerabilities: Critical impact → Mitigation: Security audit, penetration testing
- Authentication complexity: High impact → Mitigation: Use proven libraries, document flows
- Compliance requirements: High impact → Mitigation: Early review with stakeholders

**Success Validation**:
- [ ] Authentication flow works end-to-end
- [ ] Authorization correctly restricts access
- [ ] All inputs validated before processing
- [ ] Security tests pass (no critical vulnerabilities)
- [ ] Rate limiting prevents abuse

---

### M3: [Feature Name] (P0/P1/P2)
**Priority**: P0 | P1 | P2
**Duration**:
- Optimistic: X days
- Realistic: Y days
- Pessimistic: Z days
- **Expected**: W days

**Goal**: [Feature-specific measurable objective]

**Test-First Approach**:
1. Write tests for [component A] happy path
2. Implement [component A] basic functionality
3. Write tests for [component A] edge cases
4. Handle [component A] edge cases
5. Write tests for [component B] integration
6. Implement [component B]
7. Write integration tests for feature
8. Refactor feature implementation
9. Write E2E tests for user scenarios

**Deliverables**:
- [ ] [Specific deliverable 1]
- [ ] [Specific deliverable 2]
- [ ] [Specific deliverable 3]
- [ ] Unit tests for all components
- [ ] Integration tests for feature
- [ ] E2E tests for user workflows
- [ ] API documentation (if applicable)
- [ ] User documentation

**Test Coverage Target**: X%+ unit, Y%+ integration, Z critical E2E paths

**Dependencies**: M1, M2, [other milestones]

**Risks**:
- [Feature-specific risk 1]: Impact → Mitigation
- [Feature-specific risk 2]: Impact → Mitigation

**Success Validation**:
- [ ] All acceptance criteria met
- [ ] Tests pass across all levels
- [ ] Performance meets requirements
- [ ] Documentation complete

---

[Repeat M3 pattern for additional feature milestones M4, M5, etc.]

---

### MN: Integration & E2E Testing
**Priority**: P1
**Duration**:
- Optimistic: X days
- Realistic: Y days
- Pessimistic: Z days
- **Expected**: W days

**Goal**: Validate system-wide integration and user workflows

**Test-First Approach**:
1. Write E2E tests for critical user journeys
2. Run E2E tests and identify integration issues
3. Fix integration issues while maintaining test coverage
4. Write performance test scenarios
5. Run performance tests and establish baselines
6. Optimize bottlenecks
7. Write load test scenarios
8. Validate system behavior under load

**Deliverables**:
- [ ] E2E test suite covering critical paths
- [ ] Integration test suite for cross-component interactions
- [ ] Performance test suite with baselines
- [ ] Load testing results and analysis
- [ ] Bug fixes from integration testing
- [ ] Performance optimization report

**Test Coverage Target**: 100% critical user journeys, performance baselines established

**Dependencies**: All feature milestones (M3-M[N-1])

**Risks**:
- Integration issues: High impact → Mitigation: Incremental integration testing
- Performance issues: High impact → Mitigation: Early performance testing, optimization budget
- Environment differences: Medium impact → Mitigation: Infrastructure as code, consistent environments

**Success Validation**:
- [ ] All E2E tests pass consistently
- [ ] Performance meets requirements
- [ ] System handles expected load
- [ ] No critical integration issues

---

### M(N+1): Deployment & Operations
**Priority**: P1-P2
**Duration**:
- Optimistic: X days
- Realistic: Y days
- Pessimistic: Z days
- **Expected**: W days

**Goal**: Production-ready deployment and operational readiness

**Test-First Approach**:
1. Write deployment validation tests
2. Automate deployment process
3. Write monitoring health check tests
4. Implement monitoring and alerting
5. Write backup/restore validation tests
6. Implement backup and recovery
7. Write operational runbook tests
8. Document operational procedures

**Deliverables**:
- [ ] Deployment automation (CI/CD to production)
- [ ] Monitoring and alerting configured
- [ ] Logging aggregation and analysis
- [ ] Backup and recovery procedures
- [ ] Operational runbooks
- [ ] Incident response procedures
- [ ] Capacity planning documentation
- [ ] Production environment validated

**Test Coverage Target**: All operational procedures validated

**Dependencies**: MN (Integration & E2E Testing)

**Risks**:
- Deployment failures: Critical impact → Mitigation: Blue-green deployment, rollback procedures
- Monitoring gaps: High impact → Mitigation: Comprehensive monitoring checklist
- Production incidents: High impact → Mitigation: Incident response plan, on-call rotation

**Success Validation**:
- [ ] Successful production deployment
- [ ] Monitoring alerts functional
- [ ] Backup/restore tested successfully
- [ ] Team trained on operational procedures

---

## Risk Analysis

### Technical Risks

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| [Technical risk 1] | High/Medium/Low | High/Medium/Low | [Specific mitigation actions] |
| [Technical risk 2] | High/Medium/Low | High/Medium/Low | [Specific mitigation actions] |
| Technology learning curve | Medium | High | Pair programming, code reviews, documentation |
| Integration complexity | High | Medium | Incremental integration, continuous testing |
| Performance bottlenecks | Medium | Medium | Early performance testing, optimization budget |

### Schedule Risks

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| [Schedule risk 1] | High/Medium/Low | High/Medium/Low | [Specific mitigation actions] |
| [Schedule risk 2] | High/Medium/Low | High/Medium/Low | [Specific mitigation actions] |
| Scope creep | High | High | Clear requirements, change control process |
| Dependencies delay | High | Medium | Buffer time, parallel work streams |
| Underestimated complexity | Medium | High | 20-30% buffer, weekly estimate reviews |

### Resource Risks

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| [Resource risk 1] | High/Medium/Low | High/Medium/Low | [Specific mitigation actions] |
| [Resource risk 2] | High/Medium/Low | High/Medium/Low | [Specific mitigation actions] |
| Team member unavailability | High | Medium | Knowledge sharing, documentation |
| Skill gaps | Medium | Medium | Training, pair programming, mentoring |
| Tool/infrastructure issues | Medium | Low | Backup tools, vendor support agreements |

---

## Timeline & Resources

**Total Duration**: X weeks (realistic estimate)
**Buffer Allocation**: Y weeks (Z% buffer)
**Team Size**: N developers
**Total Estimated Hours**: ~W hours

### Milestone Schedule

| Milestone | Duration | Start | End | Team | Hours | Priority |
|-----------|----------|-------|-----|------|-------|----------|
| M0 | 1w | Week 1 | Week 1 | 2d | 80h | P1 |
| M1 | 2w | Week 2 | Week 3 | 2d | 160h | P0 |
| M2 | 2w | Week 4 | Week 5 | 2d | 160h | P0 |
| M3 | 3w | Week 6 | Week 8 | 2d | 240h | P0 |
| ... | ... | ... | ... | ... | ... | ... |

**Critical Path Duration**: X weeks
**Total with Buffer**: Y weeks
**Target Completion**: [Date]

### Resource Allocation

**Development Team**:
- Senior Developer: [Name/Role] - Full time
- Developer: [Name/Role] - Full time
- [Additional roles as needed]

**Support Roles**:
- DevOps Engineer: [Time allocation]
- Designer: [Time allocation]
- Product Owner: [Time allocation]

**Key Assumptions**:
- Team available full-time on project
- No major holidays or team absences
- Infrastructure and tools available when needed
- Requirements stable (controlled change process)

---

## Quality Gates

### Per-Milestone Gates

**Must pass before milestone completion**:
- [ ] All tests passing (unit, integration, E2E as applicable)
- [ ] Code review completed
- [ ] Test coverage meets target
- [ ] Documentation updated
- [ ] Security scan passed (if applicable)
- [ ] Performance benchmarks met (if applicable)

### Project-Level Gates

**Must pass before production deployment**:
- [ ] All P0 and P1 milestones complete
- [ ] Overall test coverage ≥ X%
- [ ] No critical security vulnerabilities
- [ ] Performance requirements validated
- [ ] Operational readiness verified
- [ ] Production deployment rehearsed
- [ ] Rollback procedures tested

---

## Success Metrics

**Development Metrics**:
- Test coverage: Target X%+
- Build success rate: Target 95%+
- Code review turnaround: Target <24h
- Bug escape rate: Target <5%

**Project Metrics**:
- Schedule adherence: Target ±10%
- Budget adherence: Target ±10%
- Quality: Zero critical bugs in production
- Performance: Meet all SLA requirements

**Team Metrics**:
- Team satisfaction: Target 4+/5
- Code quality score: Target A/B
- Knowledge sharing: Regular sessions
- Documentation completeness: 100% of deliverables

---

## Notes

### Assumptions
- [List all key assumptions made during planning]
- [Include technical, resource, and timeline assumptions]
- [Document dependency assumptions]

### Constraints
- [Document all project constraints]
- [Technical limitations]
- [Resource constraints]
- [Timeline constraints]

### Decision Log
- [Record key technical decisions]
- [Include rationale and alternatives considered]
- [Document decision makers]

---

## Approval

**Plan Prepared By**: [Name]
**Review Date**: [Date]
**Approved By**: [Name/Role]
**Approval Date**: [Date]

**Stakeholder Sign-off**:
- [ ] Technical Lead
- [ ] Product Owner
- [ ] Team Members
- [ ] Additional Stakeholders

---
```

## Usage Notes

### Adapting the Template

1. **Project-Specific Sections**: Customize Overview, Principles, and Success Criteria
2. **Milestone Count**: Adjust number based on project size (typical: 5-12 milestones)
3. **Dependencies**: Modify dependency graph to match architecture
4. **Risks**: Add domain-specific risks (regulatory, market, technical)
5. **Resources**: Adjust team composition and timeline

### Common Variations

**Small Projects** (1-3 months):
- Combine M0 with M1
- Simplify risk analysis
- Reduce milestone count (4-6)

**Large Projects** (6+ months):
- Add intermediate checkpoints
- More detailed risk analysis
- Additional milestone breakdown
- Separate deployment phases

**Team Size Adjustments**:
- Solo: Simplify documentation, focus on execution
- 2-3: Standard template works well
- 5+: Add coordination overhead, more detailed resource allocation

### Validation Tips

Before submitting to Codex:
- Verify all dependencies are logical
- Check time estimates are realistic (not optimistic)
- Ensure TDD approach specified for each milestone
- Confirm all architecture components mapped
- Validate risk mitigation strategies are actionable
