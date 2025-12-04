---
name: n8n-code-javascript
description: Expert guidance for writing JavaScript in n8n Code nodes. Covers execution modes, data access patterns, return formats, and common pitfalls. Essential for n8n workflow automation with custom code.
---

# n8n JavaScript Code Node

## Overview

Complete guide for writing JavaScript in n8n Code nodes. Code nodes execute JavaScript with access to n8n's special variables and built-in helpers.

**Critical Rule**: Always return array of objects with `json` property.

## Execution Modes

### Run Once for All Items (Recommended - 95% of cases)

Processes entire dataset in single execution.

```javascript
// Access all items
const items = $input.all();

// Process and return
return items.map(item => ({
  json: {
    ...item.json,
    processed: true
  }
}));
```

**Use when**:
- Aggregating data across items
- Cross-item comparisons
- Batch transformations

### Run Once for Each Item

Executes separately per item.

```javascript
// Access current item
const item = $input.item;

// Process and return single item
return [{
  json: {
    ...item.json,
    processed: true
  }
}];
```

**Use when**:
- Per-item independence required
- Different logic per item
- Memory optimization needed

## Core Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `$input.all()` | All input items | `const items = $input.all()` |
| `$input.first()` | First input item | `const first = $input.first()` |
| `$input.item` | Current item (each mode) | `const item = $input.item` |
| `$json` | Current item's JSON data | `$json.fieldName` |
| `$node["Name"]` | Reference other nodes | `$node["HTTP"].json` |
| `$env` | Environment variables | `$env.API_KEY` |

## Webhook Data Structure

**Critical**: Webhook data nests under `.body`, not at root level.

```javascript
// WRONG - Common mistake
const name = $json.name;

// CORRECT - Webhook data is nested
const name = $json.body.name;
```

## Return Format Requirements

### Valid Return Formats

```javascript
// Single item
return [{json: {field: "value"}}];

// Multiple items
return [
  {json: {id: 1, name: "First"}},
  {json: {id: 2, name: "Second"}}
];

// From array transformation
return items.map(item => ({json: item.json}));
```

### Invalid Return Formats

```javascript
// WRONG - Missing array wrapper
return {json: {field: "value"}};

// WRONG - Missing json property
return [{field: "value"}];

// WRONG - Plain value
return "result";

// WRONG - Object without structure
return {field: "value"};
```

## Data Access Patterns

### Pattern 1: Batch Operations

```javascript
const items = $input.all();
const total = items.reduce((sum, item) => sum + item.json.amount, 0);

return [{
  json: {
    totalAmount: total,
    itemCount: items.length,
    average: total / items.length
  }
}];
```

### Pattern 2: Filtering

```javascript
const items = $input.all();
const filtered = items.filter(item => item.json.status === 'active');

return filtered.map(item => ({json: item.json}));
```

### Pattern 3: Transformation

```javascript
const items = $input.all();

return items.map(item => ({
  json: {
    fullName: `${item.json.firstName} ${item.json.lastName}`,
    email: item.json.email.toLowerCase(),
    createdAt: new Date().toISOString()
  }
}));
```

### Pattern 4: Aggregation with Grouping

```javascript
const items = $input.all();
const grouped = {};

items.forEach(item => {
  const key = item.json.category;
  if (!grouped[key]) {
    grouped[key] = [];
  }
  grouped[key].push(item.json);
});

return Object.entries(grouped).map(([category, items]) => ({
  json: {
    category,
    count: items.length,
    items
  }
}));
```

### Pattern 5: Node Reference

```javascript
// Access data from another node
const httpData = $node["HTTP Request"].json;
const webhookData = $node["Webhook"].json.body;

return [{
  json: {
    fromHttp: httpData.result,
    fromWebhook: webhookData.userId
  }
}];
```

## Built-in Helpers

### HTTP Requests

```javascript
const response = await $helpers.httpRequest({
  method: 'GET',
  url: 'https://api.example.com/data',
  headers: {
    'Authorization': `Bearer ${$env.API_TOKEN}`
  }
});

return [{json: response}];
```

### Date Operations (Luxon)

```javascript
const { DateTime } = require('luxon');

const now = DateTime.now();
const formatted = now.toFormat('yyyy-MM-dd');
const tomorrow = now.plus({days: 1});

return [{
  json: {
    today: formatted,
    tomorrow: tomorrow.toISO()
  }
}];
```

### JSON Path Queries

```javascript
const data = $input.first().json;
const result = $jmespath(data, 'items[*].name');

return [{json: {names: result}}];
```

## Common Mistakes & Fixes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Missing return | No output produced | Always return array of objects |
| Wrong wrapper | `{json: data}` not in array | Wrap in `[{json: data}]` |
| Webhook access | `$json.field` fails | Use `$json.body.field` |
| Null reference | Undefined property access | Add null checks with `?.` |
| Expression syntax | Using `{{}}` in Code node | Remove brackets, use plain JS |

## Null Safety

```javascript
// Safe property access
const name = $json.body?.user?.name ?? 'Unknown';

// Safe array access
const items = $json.body?.items ?? [];

// Safe with default
const count = $json.body?.count || 0;
```

## Best Practices

### DO
- Always return proper array format
- Use `$input.all()` for batch processing
- Access webhook data via `.body`
- Add null checks for optional fields
- Use built-in helpers when available

### DON'T
- Return unwrapped objects
- Forget the `json` property wrapper
- Use expression syntax `{{}}` in Code nodes
- Assume data structure without checking
- Skip error handling for external calls

## Error Handling

```javascript
try {
  const items = $input.all();

  // Process items
  const results = items.map(item => {
    if (!item.json.required_field) {
      throw new Error(`Missing required field in item`);
    }
    return {json: {processed: item.json.required_field}};
  });

  return results;
} catch (error) {
  // Return error information
  return [{
    json: {
      error: true,
      message: error.message,
      timestamp: new Date().toISOString()
    }
  }];
}
```

## Quick Reference

```javascript
// Template for "Run Once for All Items"
const items = $input.all();

// Your processing logic here
const processed = items.map(item => ({
  json: {
    // Transform item.json as needed
    ...item.json,
    processed: true
  }
}));

return processed;
```

## Related Skills

- `n8n-code-python`: Python Code node guide
- `n8n-expression-syntax`: Expression syntax reference
- `n8n-validation-expert`: Validation and error fixing
