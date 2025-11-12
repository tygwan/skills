# TDD Principles for MVP Planning

This document outlines Test-Driven Development principles specifically in the context of MVP planning and task execution.

---

## Core TDD Philosophy

**Test-Driven Development is not testing. It is a design and development methodology.**

### The Three Laws of TDD

1. **Write no production code** except to pass a failing test
2. **Write no more of a test** than is sufficient to fail
3. **Write no more production code** than is sufficient to pass the test

### The RED-GREEN-REFACTOR Cycle

```
┌──────────────────────────────────────────┐
│  RED → GREEN → REFACTOR → COMMIT → RED  │
└──────────────────────────────────────────┘

RED:
  - Write a failing test
  - Test must fail for the right reason
  - Run test and confirm failure

GREEN:
  - Write minimum code to pass
  - No extra features
  - Just enough to turn red to green

REFACTOR:
  - Improve code structure
  - Keep tests green
  - Extract patterns
  - Improve names

COMMIT:
  - Commit working code
  - Write clear message
  - Push to repository
```

---

## Why TDD for MVP Planning?

### Benefits for Project Planning

1. **Clarity of Requirements**
   - Tests force precise requirement definition
   - Ambiguous requirements surface early
   - Acceptance criteria become testable

2. **Incremental Development**
   - Small, verifiable steps
   - Continuous validation
   - Visible progress

3. **Risk Reduction**
   - Issues found immediately
   - No "big bang" integration
   - Regression prevention

4. **Team Alignment**
   - Tests document expected behavior
   - Shared understanding of "done"
   - Objective quality metrics

5. **Sustainable Pace**
   - Regular sense of achievement
   - Prevents burnout
   - Maintains quality under pressure

---

## TDD in Task Breakdown

### Task Structure Pattern

Every feature follows this pattern:

```
Feature: User Authentication

1. [RED] Write test for successful login (1.0h)
   - Test authenticates valid user
   - Test returns auth token
   - Test fails because feature doesn't exist

2. [GREEN] Implement basic login (1.5h)
   - Minimum code to pass test
   - Validates credentials
   - Returns token

3. [RED] Write test for invalid credentials (0.5h)
   - Test rejects wrong password
   - Test returns appropriate error
   - Test fails because error handling missing

4. [GREEN] Handle invalid credentials (0.5h)
   - Add error handling
   - Return error message
   - Pass the test

5. [RED] Write test for missing fields (0.5h)
   - Test validates required fields
   - Test fails because validation missing

6. [GREEN] Add field validation (0.5h)
   - Validate required fields
   - Pass the test

7. [REFACTOR] Extract validation logic (0.5h)
   - Create reusable validator
   - Keep all tests green
   - Improve code structure

8. [COMMIT] Commit: "feat(auth): add user login" (0.5h)
   - All tests passing
   - Clear commit message
   - Push to repository
```

### Granularity Guidelines

**Too Large** (Split it):
```
❌ Implement authentication system (8h)
   - Too many responsibilities
   - Can't complete in one day
   - Hard to test atomically
```

**Too Small** (Merge it):
```
❌ Import bcrypt library (0.1h)
❌ Create password hash function (0.1h)
❌ Write test for password hash (0.1h)

✅ Implement password hashing with tests (1.0h)
   - Import library, write test, implement
   - Complete mini TDD cycle
   - Atomic, testable unit
```

**Just Right**:
```
✅ Write test for user registration (1.0h)
✅ Implement user registration (1.5h)
✅ Write test for duplicate email (0.5h)
✅ Handle duplicate email error (0.5h)
```

---

## Test Types in MVP Planning

### Unit Tests (60-70% of tests)

**Purpose**: Test individual functions/methods in isolation

**Characteristics**:
- Fast execution (< 1ms per test)
- No external dependencies
- Focused on single responsibility
- Most numerous test type

**Example Task**:
```
- [ ] Write test for email validation (0.5h) [RED]
- [ ] Implement email validator (0.5h) [GREEN]
```

**Good Unit Test**:
```typescript
test('validates correct email format', () => {
  expect(validateEmail('user@example.com')).toBe(true);
  expect(validateEmail('invalid-email')).toBe(false);
  expect(validateEmail('')).toBe(false);
});
```

### Integration Tests (20-30% of tests)

**Purpose**: Test interactions between components

**Characteristics**:
- Slower than unit tests (10-100ms)
- May use test database
- Validates component collaboration
- Fewer than unit tests

**Example Task**:
```
- [ ] Write integration test for login flow (1.5h) [INT]
  - Tests auth service + database + token service
  - Validates end-to-end authentication
```

**Good Integration Test**:
```typescript
test('login flow authenticates user and returns token', async () => {
  // Setup: Create test user in database
  const user = await createTestUser({ email, password });

  // Execute: Login
  const result = await authService.login(email, password);

  // Verify: Token returned and valid
  expect(result.token).toBeDefined();
  expect(await verifyToken(result.token)).toEqual({ userId: user.id });
});
```

### End-to-End Tests (5-10% of tests)

**Purpose**: Test complete user workflows

**Characteristics**:
- Slow (seconds per test)
- Uses real/staging environment
- Simulates actual user behavior
- Fewest but highest value

**Example Task**:
```
- [ ] Write E2E test for signup and login flow (3.0h) [E2E]
  - Tests complete user journey
  - From signup through authenticated action
```

**Good E2E Test**:
```typescript
test('new user can signup, verify email, and login', async () => {
  // Signup
  await page.goto('/signup');
  await page.fill('[name=email]', testEmail);
  await page.fill('[name=password]', testPassword);
  await page.click('button[type=submit]');

  // Verify email (mock)
  const verifyLink = await getVerificationLink(testEmail);
  await page.goto(verifyLink);

  // Login
  await page.goto('/login');
  await page.fill('[name=email]', testEmail);
  await page.fill('[name=password]', testPassword);
  await page.click('button[type=submit]');

  // Verify logged in
  await expect(page.locator('[data-testid=user-menu]')).toBeVisible();
});
```

### Test Pyramid

```
      /\
     /  \    E2E (5-10%)
    /────\   Few, slow, high-value
   /      \
  /────────\ Integration (20-30%)
 /          \ Moderate number, medium speed
/────────────\
\            / Unit (60-70%)
 \──────────/  Many, fast, focused
```

**Task Distribution Should Reflect Pyramid**:
- More unit test tasks than integration test tasks
- More integration test tasks than E2E test tasks
- Balance: confidence vs. speed

---

## TDD Anti-Patterns to Avoid

### 1. Testing After Implementation

**Wrong**:
```
❌ - [ ] Implement user login (2.0h) [GREEN]
❌ - [ ] Write tests for login (1.0h) [RED]
```

**Why Wrong**:
- Tests will pass immediately (proves nothing)
- Biased by implementation details
- Misses edge cases

**Right**:
```
✅ - [ ] Write test for user login (1.0h) [RED]
✅ - [ ] Implement user login (1.5h) [GREEN]
```

### 2. Over-Mocking

**Wrong**:
```typescript
❌ test('processes payment', async () => {
  const mockStripe = jest.fn().mockResolvedValue({ success: true });
  const mockDatabase = jest.fn().mockResolvedValue({ id: 123 });
  const mockEmail = jest.fn();

  await paymentService.process(mockStripe, mockDatabase, mockEmail);

  expect(mockStripe).toHaveBeenCalled();
  expect(mockDatabase).toHaveBeenCalled();
  expect(mockEmail).toHaveBeenCalled();
});
```

**Why Wrong**:
- Tests mocks, not real code
- Doesn't validate actual behavior
- Brittle (changes with implementation)

**Right**:
```typescript
✅ test('processes payment and sends confirmation', async () => {
  const testUser = await createTestUser();

  const result = await paymentService.process({
    userId: testUser.id,
    amount: 1000,
    paymentMethod: 'pm_test_card'
  });

  expect(result.success).toBe(true);
  expect(result.transactionId).toBeDefined();

  const emailSent = await checkTestEmail(testUser.email);
  expect(emailSent.subject).toContain('Payment Confirmation');
});
```

### 3. Skipping Refactor

**Wrong**:
```
✅ - [ ] Write test for feature A (1.0h) [RED]
✅ - [ ] Implement feature A (1.5h) [GREEN]
❌ - [ ] Write test for feature B (1.0h) [RED]  ← Skip refactor
```

**Why Wrong**:
- Technical debt accumulates
- Code becomes harder to test
- Slows future development

**Right**:
```
✅ - [ ] Write test for feature A (1.0h) [RED]
✅ - [ ] Implement feature A (1.5h) [GREEN]
✅ - [ ] Refactor feature A (0.5h) [REFACTOR]
✅ - [ ] Write test for feature B (1.0h) [RED]
```

### 4. Testing Implementation Details

**Wrong**:
```typescript
❌ test('login calls database.findUser', async () => {
  const spy = jest.spyOn(database, 'findUser');
  await authService.login(email, password);
  expect(spy).toHaveBeenCalledWith({ email });
});
```

**Why Wrong**:
- Tests HOW not WHAT
- Breaks when refactoring
- Doesn't test actual behavior

**Right**:
```typescript
✅ test('login returns token for valid credentials', async () => {
  await createTestUser({ email, password });

  const result = await authService.login(email, password);

  expect(result.token).toBeDefined();
  expect(await verifyToken(result.token)).toMatchObject({
    email: email
  });
});
```

### 5. Unclear Test Names

**Wrong**:
```
❌ test('test1', ...)
❌ test('works', ...)
❌ test('login', ...)
```

**Right**:
```
✅ test('rejects login with invalid password', ...)
✅ test('creates user with valid data', ...)
✅ test('returns 404 for non-existent resource', ...)
```

---

## Test Coverage Guidelines

### Coverage Targets by Component Type

**Critical Components** (95-100%):
- Authentication/authorization
- Payment processing
- Data validation
- Security features
- Encryption/decryption

**Core Business Logic** (85-95%):
- Feature implementations
- Business rules
- Data transformations
- API endpoints

**Infrastructure** (80-90%):
- Database utilities
- Configuration
- Logging
- Error handling

**UI Components** (60-75%):
- React components
- Form validation
- User interactions

**Configuration/Setup** (Not required):
- Config files
- Build scripts
- Environment setup

### Coverage Metrics in Tasks

Include explicit coverage targets:

```
### M2: Authentication System (40h)
**Test Coverage Target**: 95%+ unit, 90%+ integration

- [ ] Write tests for user registration (1.5h) [RED]
- [ ] Implement user registration (2.0h) [GREEN]
- [ ] Write tests for edge cases (1.0h) [RED]
- [ ] Handle edge cases (1.0h) [GREEN]
- [ ] Verify coverage meets 95% target (0.5h) [INT]
```

---

## Quality Gates for TDD Tasks

### Before Marking [RED] Task Complete

- [ ] Test written and failing
- [ ] Test fails for expected reason (feature missing, not error)
- [ ] Test failure message is clear
- [ ] Test is focused (one behavior)
- [ ] Test name describes behavior

### Before Marking [GREEN] Task Complete

- [ ] Test now passes
- [ ] Only minimum code written
- [ ] No extra features added
- [ ] All existing tests still pass
- [ ] Code is readable

### Before Marking [REFACTOR] Task Complete

- [ ] Code structure improved
- [ ] Duplication removed
- [ ] Names improved
- [ ] All tests still passing
- [ ] No new behavior added

### Before Marking [COMMIT] Task Complete

- [ ] All tests passing
- [ ] Code reviewed (if pair/team)
- [ ] Commit message follows convention
- [ ] Branch up to date with main
- [ ] CI pipeline passing (if applicable)

---

## TDD Task Templates

### Basic Feature Implementation

```
Component: [Name] (Xh)

1. [RED] Write test for happy path (1.0h)
   - Test: [specific behavior]
   - Expected: Test fails (feature missing)

2. [GREEN] Implement basic functionality (1.5h)
   - Implement: [minimum to pass]
   - Expected: Test passes

3. [RED] Write test for edge case (0.5h)
   - Test: [specific edge case]
   - Expected: Test fails

4. [GREEN] Handle edge case (0.5h)
   - Implement: [edge case handling]
   - Expected: Test passes

5. [RED] Write test for error scenario (0.5h)
   - Test: [error condition]
   - Expected: Test fails

6. [GREEN] Implement error handling (0.5h)
   - Implement: [error handling]
   - Expected: Test passes

7. [REFACTOR] Extract common logic (0.5h)
   - Refactor: [improvement]
   - Expected: All tests still pass

8. [INT] Write integration test (1.0h)
   - Test: [integration scenario]
   - Expected: Integration validated

9. [DOC] Document component (1.0h)
   - Document: API and usage

10. [COMMIT] Commit feature (0.5h)
    - Commit: "feat(module): add [feature]"

Total: Xh
```

### Bug Fix Pattern

```
Bug Fix: [Description] (Yh)

1. [RED] Write test reproducing bug (1.0h)
   - Test: [reproduces bug]
   - Expected: Test fails (bug exists)

2. [GREEN] Fix bug (1.5h)
   - Fix: [root cause]
   - Expected: Test passes

3. [RED] Write regression tests (0.5h)
   - Test: [related edge cases]
   - Expected: All pass (bug truly fixed)

4. [REFACTOR] Improve fix (0.5h)
   - Refactor: [if needed]
   - Expected: All tests pass

5. [DOC] Document fix (0.5h)
   - Document: Bug cause and solution

6. [COMMIT] Commit fix (0.5h)
   - Commit: "fix(module): resolve [bug]"

Total: Yh
```

### Security Feature Pattern

```
Security Feature: [Name] (Zh)

1. [SEC] Write security test for attack (1.0h)
   - Test: [attack scenario]
   - Expected: Test fails (vulnerability)

2. [GREEN] Implement protection (2.0h)
   - Implement: [security measure]
   - Expected: Test passes

3. [SEC] Write additional attack tests (1.5h)
   - Test: [various attack vectors]
   - Expected: All pass

4. [RED] Write test for false positives (0.5h)
   - Test: [legitimate use blocked]
   - Expected: Reveals false positive

5. [GREEN] Tune security logic (1.0h)
   - Tune: [reduce false positives]
   - Expected: Balance security/usability

6. [REFACTOR] Extract security patterns (1.0h)
   - Refactor: [reusable security code]

7. [DOC] Document security approach (1.5h)
   - Document: Threats, mitigations, usage

8. [COMMIT] Commit security feature (0.5h)
   - Commit: "sec(module): add [protection]"

Total: Zh
```

---

## TDD Success Metrics

### Task-Level Metrics

**Per Task**:
- Test written before code: Yes/No
- Test failed correctly: Yes/No
- Minimal code written: Yes/No
- Tests passing: Yes/No
- Code refactored: Yes/No

### Milestone-Level Metrics

**Per Milestone**:
- Test coverage achieved: X%
- Tests passing: Y / Y
- Bugs found in testing: N
- Bugs found in production: Target 0

### Project-Level Metrics

**Overall**:
- Total test coverage: Target ≥ 85%
- Test execution time: Target < 5 minutes
- CI build success rate: Target ≥ 95%
- Bug escape rate: Target < 5%
- Technical debt ratio: Target < 10%

---

## Common TDD Questions

### "When should I write integration tests vs. unit tests?"

**Unit tests** when:
- Testing pure functions
- Testing single class/module
- Can mock dependencies easily
- Need fast feedback

**Integration tests** when:
- Testing database interactions
- Testing API endpoints
- Testing cross-component flows
- Need confidence in integration

### "How much mocking is too much?"

**Guidelines**:
- Mock external services (APIs, payments)
- Mock slow operations (file I/O, network)
- Don't mock domain logic
- Don't mock everything (test real code)
- If > 50% mocks, consider integration test

### "What if the test is hard to write?"

**Hard tests signal design problems**:
- Too many dependencies → Use dependency injection
- Complex setup → Simplify interfaces
- Unclear behavior → Clarify requirements
- Hard to mock → Improve abstraction

**Solution**: Let tests drive better design

### "Should I test private methods?"

**No.**

Test public behavior only. Private methods are tested indirectly through public API.

If private method needs testing, consider:
- Extract to separate testable unit
- Make it public (if genuinely reusable)
- Refactor design

### "How do I know my tests are good?"

**Good tests are**:
- Fast (< 1s total suite)
- Independent (no order dependency)
- Repeatable (same result every time)
- Self-validating (pass/fail, no manual check)
- Timely (written before code)

**Test your tests**:
- Break code → tests should fail
- Fix code → tests should pass
- Refactor → tests should still pass

---

## TDD Tools & Best Practices

### Test Naming Conventions

```
test('should [expected behavior] when [condition]')

Examples:
✅ test('should return 404 when resource not found')
✅ test('should validate email format')
✅ test('should reject login with invalid password')
✅ test('should create user with valid data')
```

### Test Organization

```
describe('[Component/Feature]', () => {

  describe('[Method/Function]', () => {

    it('should [behavior] when [condition]', () => {
      // Arrange: Set up test data
      // Act: Execute code under test
      // Assert: Verify results
    });

  });

});
```

### Commit Message Conventions

```
[type]([scope]): [short description]

Types:
- feat: New feature
- fix: Bug fix
- test: Add/update tests
- refactor: Code restructuring
- docs: Documentation
- chore: Maintenance

Examples:
✅ feat(auth): add JWT authentication
✅ fix(validation): handle empty email
✅ test(auth): add edge case tests
✅ refactor(auth): extract validation logic
```

---

## Resources

### Further Reading

- **Kent Beck** - "Test Driven Development: By Example"
- **Martin Fowler** - "Refactoring: Improving the Design of Existing Code"
- **Robert C. Martin** - "Clean Code" & "The Clean Coder"

### TDD Katas for Practice

- String Calculator Kata
- Bowling Game Kata
- Prime Factors Kata
- Roman Numerals Kata

### Testing Frameworks

**JavaScript/TypeScript**:
- Jest
- Mocha + Chai
- Vitest

**Python**:
- pytest
- unittest

**Java**:
- JUnit
- TestNG

**C#**:
- NUnit
- xUnit

---

## Conclusion

**TDD is a discipline, not a burden.**

When properly integrated into project planning:
- Requirements become clearer
- Development becomes faster
- Quality improves dramatically
- Teams gain confidence
- MVPs ship successfully

**Remember**: The goal is not 100% coverage. The goal is confidence that your code works as intended, delivered through systematic, test-first development.
