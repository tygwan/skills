---
name: n8n-expression-syntax
description: Comprehensive guide for writing correct n8n expressions in workflows. Covers expression format, core variables, webhook data structure, common patterns, and validation rules.
---

# n8n Expression Syntax

## Overview

Complete guide for writing correct n8n expressions in workflow node fields. Expressions allow dynamic data access and transformation within n8n workflows.

**Critical Rule**: Webhook data is under `.body`, not at root level.

## Expression Format

### Basic Syntax

All expressions use double curly braces:

```
{{ expression }}
```

### Examples

```
{{ $json.fieldName }}
{{ $json.body.userName }}
{{ $node["HTTP Request"].json.data }}
{{ $now.toFormat("yyyy-MM-dd") }}
```

## Core Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `$json` | Current item's JSON data | `{{ $json.name }}` |
| `$node["Name"]` | Access other node's output | `{{ $node["Webhook"].json }}` |
| `$now` | Current DateTime (Luxon) | `{{ $now.toISO() }}` |
| `$today` | Today at midnight | `{{ $today.toFormat("yyyy-MM-dd") }}` |
| `$env` | Environment variables | `{{ $env.API_KEY }}` |
| `$input` | Input data methods | `{{ $input.first().json }}` |
| `$runIndex` | Current execution index | `{{ $runIndex }}` |
| `$itemIndex` | Current item index | `{{ $itemIndex }}` |

## Webhook Data Structure

**Critical**: Webhook data nests under `.body` property.

### Correct Access

```
{{ $json.body.name }}
{{ $json.body.email }}
{{ $json.body.user.id }}
```

### Common Mistake

```
// WRONG - data is not at root
{{ $json.name }}

// CORRECT - access via body
{{ $json.body.name }}
```

### Full Webhook Structure

```json
{
  "headers": { "content-type": "application/json" },
  "params": {},
  "query": { "id": "123" },
  "body": {
    "name": "John",
    "email": "john@example.com"
  }
}
```

Access patterns:
- Body data: `{{ $json.body.name }}`
- Query params: `{{ $json.query.id }}`
- Headers: `{{ $json.headers["content-type"] }}`

## Common Patterns

### Nested Field Access

```
{{ $json.body.user.profile.name }}
{{ $json.data.items[0].id }}
{{ $json.response.results[0].value }}
```

### Node References

```
// Access HTTP Request node output
{{ $node["HTTP Request"].json.data }}

// Access Webhook node body
{{ $node["Webhook"].json.body.userId }}

// Access Set node output
{{ $node["Set"].json.processedValue }}
```

### Variable Combination

```
// Concatenation
{{ $json.body.firstName + " " + $json.body.lastName }}

// Template literal
{{ `Hello, ${$json.body.name}!` }}

// With fallback
{{ $json.body.nickname || $json.body.name || "Guest" }}
```

### Date Formatting

```
// Current date formatted
{{ $now.toFormat("yyyy-MM-dd") }}

// Current time
{{ $now.toFormat("HH:mm:ss") }}

// Full datetime
{{ $now.toFormat("yyyy-MM-dd HH:mm:ss") }}

// ISO format
{{ $now.toISO() }}

// Custom format
{{ $now.toFormat("MMMM dd, yyyy") }}
```

### Date Manipulation

```
// Tomorrow
{{ $now.plus({days: 1}).toFormat("yyyy-MM-dd") }}

// Last week
{{ $now.minus({weeks: 1}).toISO() }}

// Start of month
{{ $now.startOf("month").toFormat("yyyy-MM-dd") }}

// End of day
{{ $now.endOf("day").toISO() }}
```

### String Methods

```
// Lowercase
{{ $json.body.email.toLowerCase() }}

// Uppercase
{{ $json.body.name.toUpperCase() }}

// Trim whitespace
{{ $json.body.input.trim() }}

// Replace
{{ $json.body.text.replace("old", "new") }}

// Split
{{ $json.body.tags.split(",") }}
```

### Array Operations

```
// First item
{{ $json.body.items[0] }}

// Last item
{{ $json.body.items[$json.body.items.length - 1] }}

// Array length
{{ $json.body.items.length }}

// Join array
{{ $json.body.tags.join(", ") }}
```

### Conditional Expressions

```
// Ternary operator
{{ $json.body.status === "active" ? "Yes" : "No" }}

// Null coalescing
{{ $json.body.nickname ?? $json.body.name ?? "Anonymous" }}

// OR fallback
{{ $json.body.value || "default" }}

// Boolean check
{{ $json.body.isEnabled ? "Enabled" : "Disabled" }}
```

### Number Operations

```
// Math operations
{{ $json.body.price * $json.body.quantity }}

// Rounding
{{ Math.round($json.body.value) }}

// Fixed decimals
{{ $json.body.amount.toFixed(2) }}

// Parse string to number
{{ parseInt($json.body.count) }}
{{ parseFloat($json.body.price) }}
```

## When NOT to Use Expressions

### Code Nodes

In Code nodes, use plain JavaScript:

```javascript
// WRONG - expression syntax in Code node
const name = {{ $json.body.name }};

// CORRECT - plain JavaScript
const name = $json.body.name;
```

### Webhook Path

Webhook paths are static:

```
// WRONG
/webhook/{{ $env.PATH }}

// CORRECT
/webhook/my-endpoint
```

### Credential Fields

Credentials don't support expressions:

```
// Use environment variables or static values
API_KEY: static-key-value
```

## Validation Rules

### 1. Balanced Braces

```
// CORRECT
{{ $json.body.name }}

// WRONG - unbalanced
{ $json.body.name }}
{{ $json.body.name }
```

### 2. Valid JavaScript

```
// CORRECT - valid JS expression
{{ $json.body.items.filter(i => i.active) }}

// WRONG - invalid syntax
{{ $json.body.items.filter(i -> i.active) }}
```

### 3. Proper Property Access

```
// CORRECT
{{ $json.body["field-name"] }}
{{ $json.body.fieldName }}

// WRONG - invalid property access
{{ $json.body.field-name }}
```

### 4. Closed Strings

```
// CORRECT
{{ $json.body.type === "active" }}

// WRONG - unclosed string
{{ $json.body.type === "active }}
```

## Common Mistakes & Fixes

| Mistake | Incorrect | Correct |
|---------|-----------|---------|
| Root access | `{{ $json.name }}` | `{{ $json.body.name }}` |
| Missing braces | `$json.body.name` | `{{ $json.body.name }}` |
| Wrong quotes | `{{ $json.body['name"] }}` | `{{ $json.body["name"] }}` |
| Invalid operator | `{{ $json.body.x AND $json.body.y }}` | `{{ $json.body.x && $json.body.y }}` |
| Undefined access | `{{ $json.body.user.name }}` | `{{ $json.body.user?.name }}` |

## Debugging Expressions

### Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| "Cannot read property of undefined" | Accessing nested undefined | Add optional chaining `?.` |
| "Unexpected token" | Syntax error | Check brackets and quotes |
| "is not defined" | Wrong variable name | Verify variable exists |
| "Expected expression" | Empty or invalid | Add valid expression |

### Safe Access Pattern

```
// Safe nested access
{{ $json.body?.user?.profile?.name ?? "Unknown" }}

// Check before access
{{ $json.body && $json.body.user ? $json.body.user.name : "N/A" }}
```

## Expression Helpers

### Available Methods

- `$if(condition, trueValue, falseValue)` - Conditional
- `$jmespath(data, query)` - JMESPath query
- `$min(array)` / `$max(array)` - Min/max values
- `$average(array)` - Average value

### DateTime (Luxon)

```
{{ $now }}                          // Current DateTime
{{ $now.toISO() }}                  // ISO string
{{ $now.toFormat("yyyy-MM-dd") }}   // Custom format
{{ $now.plus({days: 7}) }}          // Add time
{{ $now.minus({hours: 2}) }}        // Subtract time
{{ $now.startOf("day") }}           // Start of period
{{ $now.endOf("month") }}           // End of period
```

## Best Practices

### DO
- Always access webhook data via `.body`
- Use optional chaining `?.` for nested access
- Provide fallback values with `??` or `||`
- Test expressions with sample data
- Keep expressions simple and readable

### DON'T
- Use expression syntax `{{}}` in Code nodes
- Assume data structure without verification
- Chain too many operations (use Code node instead)
- Forget to close quotes and brackets
- Access array indices without checking length

## Quick Reference

```
// Webhook body access
{{ $json.body.fieldName }}

// Node reference
{{ $node["NodeName"].json.field }}

// Date formatting
{{ $now.toFormat("yyyy-MM-dd") }}

// Conditional
{{ $json.body.active ? "Yes" : "No" }}

// Fallback
{{ $json.body.name ?? "Unknown" }}

// String method
{{ $json.body.email.toLowerCase() }}
```

## Related Skills

- `n8n-code-javascript`: JavaScript Code node guide
- `n8n-code-python`: Python Code node guide
- `n8n-validation-expert`: Validation and error fixing
