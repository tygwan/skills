---
name: n8n-mcp-tools-expert
description: Master guide for using n8n-mcp MCP server tools to build workflows. Covers 40+ tools, node type formats, tool selection priority, validation workflows, and iterative building strategies.
---

# n8n MCP Tools Expert

## Overview

Master guide for using n8n-mcp MCP server tools to build workflows effectively. Covers tool selection, configuration patterns, and best practices for workflow automation.

**Key Insight**: Use `get_node_essentials` over `get_node_info` (91.7% vs 80% success rate).

## NodeType Format Distinction

**Critical**: Different tools require different prefixes.

### Search/Validation Tools

Use `nodes-base.` prefix:

```
nodes-base.slack
nodes-base.googleSheets
nodes-base.httpRequest
```

### Workflow Tools

Use `n8n-nodes-base.` prefix:

```
n8n-nodes-base.slack
n8n-nodes-base.googleSheets
n8n-nodes-base.httpRequest
```

### Quick Reference

| Tool Type | Prefix | Example |
|-----------|--------|---------|
| `search_nodes` | `nodes-base.` | `nodes-base.slack` |
| `get_node_info` | `nodes-base.` | `nodes-base.slack` |
| `get_node_essentials` | `nodes-base.` | `nodes-base.slack` |
| `n8n_create_workflow` | `n8n-nodes-base.` | `n8n-nodes-base.slack` |
| `n8n_update_partial_workflow` | `n8n-nodes-base.` | `n8n-nodes-base.slack` |

## Tool Selection Priority

### Tier 1: Primary Tools (Use First)

| Tool | Success Rate | Response Time | Use Case |
|------|--------------|---------------|----------|
| `search_nodes` | 99.9% | <20ms | Find available nodes |
| `get_node_essentials` | 91.7% | ~50ms | Configuration info (~5KB) |
| `n8n_get_workflow` | 99.5% | ~100ms | Read workflow state |

### Tier 2: Secondary Tools

| Tool | Success Rate | Response Time | Use Case |
|------|--------------|---------------|----------|
| `n8n_update_partial_workflow` | 99.0% | ~200ms | Edit workflows |
| `n8n_validate_workflow` | 98.5% | ~150ms | Validate configurations |
| `get_property_dependencies` | 95% | ~80ms | Conditional field info |

### Tier 3: Reference Tools

| Tool | Success Rate | Payload | Use Case |
|------|--------------|---------|----------|
| `get_node_info` | 80% | ~100KB+ | Complete schema (fallback) |

## Core Tool Reference

### search_nodes

Find available nodes by keyword.

```json
{
  "tool": "search_nodes",
  "params": {
    "query": "slack"
  }
}
```

**Returns**: List of matching node types with descriptions.

### get_node_essentials

Get essential configuration info for a node type.

```json
{
  "tool": "get_node_essentials",
  "params": {
    "nodeType": "nodes-base.slack"
  }
}
```

**Returns**: Required fields, common operations, basic structure (~5KB).

### get_node_info

Get complete node schema (use sparingly).

```json
{
  "tool": "get_node_info",
  "params": {
    "nodeType": "nodes-base.slack"
  }
}
```

**Returns**: Full schema with all options (~100KB+).

### get_property_dependencies

Get conditional field dependencies.

```json
{
  "tool": "get_property_dependencies",
  "params": {
    "nodeType": "nodes-base.slack",
    "operation": "post"
  }
}
```

**Returns**: Fields that depend on other field values.

### n8n_create_workflow

Create a new workflow.

```json
{
  "tool": "n8n_create_workflow",
  "params": {
    "name": "My Workflow",
    "nodes": [...],
    "connections": {...}
  }
}
```

### n8n_get_workflow

Read existing workflow.

```json
{
  "tool": "n8n_get_workflow",
  "params": {
    "workflowId": "123"
  }
}
```

### n8n_update_partial_workflow

Update specific parts of a workflow.

```json
{
  "tool": "n8n_update_partial_workflow",
  "params": {
    "workflowId": "123",
    "nodes": [...],
    "connections": {...}
  }
}
```

### n8n_validate_workflow

Validate workflow configuration.

```json
{
  "tool": "n8n_validate_workflow",
  "params": {
    "workflowId": "123",
    "profile": "runtime"
  }
}
```

**Profiles**:
- `minimal`: Quick checks
- `runtime`: Balanced (recommended)
- `ai-friendly`: Reduces false positives
- `strict`: Maximum safety

## Workflow Building Process

### Iterative Building Strategy

Build workflows incrementally, not all at once.

**Average time between edits**: ~56 seconds

### Standard Process

1. **Identify nodes needed**
   ```
   search_nodes → find relevant node types
   ```

2. **Get configuration info**
   ```
   get_node_essentials → understand required fields
   ```

3. **Create initial workflow**
   ```
   n8n_create_workflow → create with basic structure
   ```

4. **Validate**
   ```
   n8n_validate_workflow → check for errors
   ```

5. **Fix errors iteratively**
   ```
   n8n_update_partial_workflow → fix issues
   n8n_validate_workflow → re-validate
   repeat until valid
   ```

### Validation Loop

```
┌─────────────────┐
│ Create/Update   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Validate      │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Errors? │
    └────┬────┘
    Yes  │  No
    │    └──────► Done
    ▼
┌─────────────────┐
│  Fix Errors     │
└────────┬────────┘
         │
         └──────────┘ (back to Validate)
```

## Node Configuration Patterns

### Webhook Node

```json
{
  "type": "n8n-nodes-base.webhook",
  "name": "Webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "my-endpoint",
    "responseMode": "onReceived"
  },
  "position": [250, 300]
}
```

### HTTP Request Node

```json
{
  "type": "n8n-nodes-base.httpRequest",
  "name": "HTTP Request",
  "parameters": {
    "method": "GET",
    "url": "https://api.example.com/data",
    "authentication": "none"
  },
  "position": [450, 300]
}
```

### Slack Node

```json
{
  "type": "n8n-nodes-base.slack",
  "name": "Slack",
  "parameters": {
    "resource": "message",
    "operation": "post",
    "channel": "#general",
    "text": "={{ $json.body.message }}"
  },
  "position": [650, 300]
}
```

### Code Node

```json
{
  "type": "n8n-nodes-base.code",
  "name": "Code",
  "parameters": {
    "mode": "runOnceForAllItems",
    "jsCode": "return $input.all().map(item => ({json: item.json}));"
  },
  "position": [450, 300]
}
```

### IF Node

```json
{
  "type": "n8n-nodes-base.if",
  "name": "IF",
  "parameters": {
    "conditions": {
      "boolean": [
        {
          "value1": "={{ $json.body.status }}",
          "operation": "equals",
          "value2": "active"
        }
      ]
    }
  },
  "position": [450, 300]
}
```

## Connection Patterns

### Basic Connection

```json
{
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "Code",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### IF Node Branches

```json
{
  "connections": {
    "IF": {
      "main": [
        [
          {
            "node": "True Branch",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "False Branch",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## Common Issues & Solutions

### Issue: Node Not Found

```
Error: Node type not found
```

**Fix**: Use `search_nodes` to find correct node name.

### Issue: Missing Required Field

```
Error: Required field missing
```

**Fix**: Use `get_node_essentials` to see required fields.

### Issue: Invalid Expression

```
Error: Expression syntax error
```

**Fix**: Check expression format, ensure `={{ }}` wrapper.

### Issue: Connection Error

```
Error: Invalid connection
```

**Fix**: Verify node names match exactly in connections.

## Best Practices

### DO
- Use `get_node_essentials` first (smaller, faster)
- Build workflows iteratively
- Validate after each change
- Use correct prefix for each tool type
- Fix errors one at a time

### DON'T
- Use `get_node_info` unless necessary
- Build entire workflow in one call
- Skip validation steps
- Mix node type prefixes
- Ignore validation warnings

## Performance Tips

| Action | Time | Recommendation |
|--------|------|----------------|
| Search nodes | <20ms | Use freely |
| Get essentials | ~50ms | Primary info source |
| Get full info | ~500ms+ | Use sparingly |
| Validate | ~150ms | After each change |
| Update | ~200ms | Iterate small changes |

## Related Skills

- `n8n-node-configuration`: Node configuration details
- `n8n-validation-expert`: Error interpretation and fixing
- `n8n-workflow-patterns`: Common workflow patterns
