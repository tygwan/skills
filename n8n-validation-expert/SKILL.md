---
name: n8n-validation-expert
description: Expert guide for interpreting and fixing n8n validation errors. Covers error severity levels, validation profiles, common error types, auto-sanitization, false positives, and recovery strategies.
---

# n8n Validation Expert

## Overview

Expert guidance on interpreting and fixing n8n validation errors. Validation is iterative, typically requiring 2-3 cycles.

**Key Stats**:
- Average analysis time: 23 seconds
- Average fix time: 58 seconds
- Typical cycles: 2-3

## Validation Philosophy

### Core Principles

1. **Read error messages completely** - Details matter
2. **Fix iteratively** - One issue at a time
3. **Trust automation** - Auto-sanitization handles structural fixes
4. **Validate frequently** - After every change

### Validation Loop

```
┌─────────────┐
│   Change    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validate   │
└──────┬──────┘
       │
  ┌────┴────┐
  │ Valid?  │
  └────┬────┘
  No   │   Yes
  │    └────► Done
  ▼
┌─────────────┐
│ Analyze     │
│ Errors      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Fix      │
└──────┬──────┘
       │
       └──────► (back to Validate)
```

## Error Severity Levels

### Errors (Must Fix)

**Blocks execution** - Workflow will not run.

```
❌ ERROR: Missing required field "channel" in Slack node
❌ ERROR: Invalid expression syntax in Code node
❌ ERROR: Node "HTTP Request" has invalid URL
```

**Action**: Fix immediately before proceeding.

### Warnings (Should Fix)

**Doesn't block** - Workflow runs but may have issues.

```
⚠️ WARNING: No error handling configured for HTTP Request
⚠️ WARNING: Deprecated parameter used in Set node
⚠️ WARNING: Large payload may cause performance issues
```

**Action**: Fix for production workflows.

### Suggestions (Optional)

**Improvements** - Best practice recommendations.

```
💡 SUGGESTION: Consider adding retry logic
💡 SUGGESTION: Use credentials instead of inline secrets
💡 SUGGESTION: Add timeout configuration
```

**Action**: Consider for robust workflows.

## Validation Profiles

### minimal

Quick checks, most permissive.

```json
{
  "profile": "minimal"
}
```

**Use for**: Quick iterations, draft workflows.

### runtime (Recommended)

Balanced validation, catches most issues.

```json
{
  "profile": "runtime"
}
```

**Use for**: Pre-deployment validation.

### ai-friendly

Reduces false positives from AI-generated configurations.

```json
{
  "profile": "ai-friendly"
}
```

**Use for**: MCP-generated workflows.

### strict

Maximum safety for production.

```json
{
  "profile": "strict"
}
```

**Use for**: Production deployments, security-critical workflows.

## Common Error Types

### missing_required

**Error**: Required field not provided.

```
ERROR: missing_required
Field: channel
Node: Slack
Message: Required field "channel" is missing
```

**Fix**:
```json
{
  "parameters": {
    "channel": "#general"  // Add required field
  }
}
```

### invalid_value

**Error**: Field value not acceptable.

```
ERROR: invalid_value
Field: httpMethod
Node: Webhook
Message: Value "PATCH" is not valid. Expected: GET, POST, PUT, DELETE
```

**Fix**:
```json
{
  "parameters": {
    "httpMethod": "POST"  // Use valid value
  }
}
```

### type_mismatch

**Error**: Wrong data type.

```
ERROR: type_mismatch
Field: limit
Node: HTTP Request
Message: Expected number, got string
```

**Fix**:
```json
{
  "parameters": {
    "limit": 100  // Use number, not "100"
  }
}
```

### invalid_expression

**Error**: Expression syntax error.

```
ERROR: invalid_expression
Field: text
Node: Slack
Message: Invalid expression syntax: unclosed bracket
```

**Fix**:
```json
{
  "parameters": {
    "text": "={{ $json.body.message }}"  // Fix syntax
  }
}
```

### invalid_reference

**Error**: Reference to non-existent node.

```
ERROR: invalid_reference
Node: Code
Message: Referenced node "HTTP Request" not found
```

**Fix**: Verify node names match exactly, including spaces.

### missing_credentials

**Error**: Required credentials not configured.

```
ERROR: missing_credentials
Node: Slack
Message: Node requires credentials but none configured
```

**Fix**:
```json
{
  "credentials": {
    "slackApi": {
      "id": "credential-id",
      "name": "Slack API"
    }
  }
}
```

### invalid_connection

**Error**: Connection configuration invalid.

```
ERROR: invalid_connection
From: Webhook
To: NonExistentNode
Message: Target node does not exist
```

**Fix**: Verify connection target exists and name matches.

## Error Interpretation Guide

### Reading Error Messages

```
ERROR: missing_required
├── Type: What kind of error
├── Field: Which field has the issue
├── Node: Which node is affected
├── Message: Human-readable description
└── Suggestion: How to fix (sometimes)
```

### Error Priority

1. **Structural errors** (missing nodes, broken connections)
2. **Required field errors** (missing_required)
3. **Type errors** (type_mismatch)
4. **Expression errors** (invalid_expression)
5. **Reference errors** (invalid_reference)
6. **Warnings and suggestions**

## Auto-Sanitization

### What It Handles

Auto-sanitization automatically fixes certain structural issues on workflow update.

| Issue | Auto-Fixed |
|-------|------------|
| Binary operator structure | ✅ |
| Unary operator format | ✅ |
| IF/Switch metadata | ✅ |
| Node position normalization | ✅ |
| Connection format | ✅ |

### What It Doesn't Handle

| Issue | Manual Fix Required |
|-------|---------------------|
| Missing required fields | ✅ |
| Invalid values | ✅ |
| Expression syntax | ✅ |
| Credential configuration | ✅ |
| Logic errors | ✅ |

### Trust Auto-Sanitization

Don't manually fix structural issues - let auto-sanitization handle them:

```json
// Don't worry about exact operator structure
// Auto-sanitization will normalize this:
{
  "conditions": {
    "boolean": [...]
  }
}
```

## False Positives

### Acceptable Warnings

Some warnings are acceptable in specific contexts:

| Warning | When Acceptable |
|---------|-----------------|
| Missing error handling | Simple/test workflows |
| No retry logic | Non-critical operations |
| Deprecated parameter | Working, no alternative |
| Performance warning | Known acceptable load |

### Handling False Positives

1. **Read warning carefully** - Understand the concern
2. **Assess context** - Is it relevant to your use case?
3. **Document decision** - Note why it's acceptable
4. **Use appropriate profile** - `ai-friendly` reduces false positives

## Recovery Strategies

### When Validation Fails Repeatedly

1. **Reset to last working state**
   ```
   n8n_get_workflow(workflowId) → save backup
   ```

2. **Simplify configuration**
   - Remove optional fields
   - Use defaults
   - Validate minimal version

3. **Check tool output**
   - Use `get_node_essentials` to verify requirements
   - Check `get_property_dependencies` for conditional fields

4. **Rebuild incrementally**
   - Add one feature at a time
   - Validate after each addition

### Error-Specific Recovery

| Error Type | Recovery Strategy |
|------------|-------------------|
| missing_required | Check essentials for field list |
| invalid_value | Check essentials for valid values |
| invalid_expression | Simplify expression, test in UI |
| type_mismatch | Verify expected type in schema |
| invalid_reference | List all nodes, verify names |

## Best Practices

### DO
- Read full error messages
- Fix one error at a time
- Validate after each fix
- Trust auto-sanitization
- Use appropriate profile
- Document accepted warnings

### DON'T
- Ignore error details
- Fix multiple issues at once
- Skip validation steps
- Manually fix auto-sanitized issues
- Use strict profile for drafts
- Treat all warnings as blockers

## Quick Fixes Table

| Error | Quick Fix |
|-------|-----------|
| Missing channel | Add `"channel": "#channel-name"` |
| Missing text | Add `"text": "={{ $json.body.message }}"` |
| Invalid URL | Ensure URL starts with http:// or https:// |
| Missing credentials | Add credentials block with id and name |
| Expression error | Wrap with `={{ }}`, check syntax |
| Type mismatch | Convert string to number or vice versa |

## Validation Checklist

Before deployment:

- [ ] All errors resolved
- [ ] Warnings reviewed and addressed/documented
- [ ] Credentials configured
- [ ] Expressions tested with sample data
- [ ] Connections verified
- [ ] Error handling in place
- [ ] Tested with `runtime` profile
- [ ] Production review with `strict` profile

## Related Skills

- `n8n-node-configuration`: Node setup guide
- `n8n-mcp-tools-expert`: Tool usage patterns
- `n8n-expression-syntax`: Expression reference
