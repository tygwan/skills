---
name: n8n-node-configuration
description: Expert guide for operation-aware n8n node configuration. Covers progressive disclosure, property dependencies, configuration workflows, and common node patterns with 91.7% success rate methodology.
---

# n8n Node Configuration

## Overview

Operation-aware node configuration guide using progressive disclosure methodology. Start minimal, add complexity as needed.

**Key Stat**: 91.7% success rate with essentials-based configuration.

## Configuration Philosophy

### Progressive Disclosure

1. Start with minimum required fields
2. Add optional fields only when needed
3. Validate after each addition
4. Use dependencies to discover conditional fields

### Configuration Priority

```
Required Fields → Common Options → Advanced Settings → Edge Cases
```

## Standard Configuration Workflow

### 8-Step Process

1. **Identify node type**
   ```
   search_nodes("slack") → nodes-base.slack
   ```

2. **Get essentials**
   ```
   get_node_essentials("nodes-base.slack")
   ```

3. **Identify operation**
   ```
   resource: "message", operation: "post"
   ```

4. **Configure required fields**
   ```
   channel, text (required for post operation)
   ```

5. **Validate**
   ```
   n8n_validate_workflow(workflowId)
   ```

6. **Fix errors if any**
   ```
   n8n_update_partial_workflow(...)
   ```

7. **Add optional fields**
   ```
   attachments, blocks (if needed)
   ```

8. **Final validation**
   ```
   n8n_validate_workflow(workflowId)
   ```

## Tool Selection Guide

| Tool | Coverage | Speed | Use When |
|------|----------|-------|----------|
| `get_node_essentials` | 90% | Fastest | First choice, most cases |
| `get_property_dependencies` | Conditional | Fast | Stuck on conditional fields |
| `get_node_info` | 100% | Slowest | Need complete schema |

## Operations Determine Fields

### Concept

Different operations require different fields, even for the same node.

### Example: Slack Node

**Post Message Operation**:
```json
{
  "resource": "message",
  "operation": "post",
  "channel": "#general",      // Required
  "text": "Hello!"            // Required
}
```

**Update Message Operation**:
```json
{
  "resource": "message",
  "operation": "update",
  "channel": "#general",      // Required
  "ts": "1234567890.123456",  // Required (message timestamp)
  "text": "Updated text"      // Required
}
```

**Get Message Operation**:
```json
{
  "resource": "message",
  "operation": "get",
  "channel": "#general",      // Required
  "ts": "1234567890.123456"   // Required
}
```

## Property Dependencies

### How displayOptions Work

Fields appear/hide based on other field values.

```json
{
  "displayOptions": {
    "show": {
      "operation": ["post"]
    }
  }
}
```

This field only shows when `operation` is `post`.

### Dependency Types

| Type | Description | Example |
|------|-------------|---------|
| Boolean Toggle | Show based on true/false | `showAdvanced: true` |
| Operation Switch | Show based on operation | `operation: "post"` |
| Resource Type | Show based on resource | `resource: "message"` |
| Multiple Conditions | Show when all match | `resource: "message" AND operation: "post"` |

### Discovering Dependencies

```
get_property_dependencies("nodes-base.slack", "post")
```

Returns fields that depend on the "post" operation.

## Common Node Patterns

### Resource/Operation Nodes

**Structure**: Resource → Operation → Parameters

**Examples**: Slack, Google Sheets, Notion, Airtable

```json
{
  "type": "n8n-nodes-base.slack",
  "parameters": {
    "resource": "message",
    "operation": "post",
    "channel": "#general",
    "text": "Hello!"
  }
}
```

### HTTP-Based Nodes

**Structure**: Method → URL → Options

**Examples**: HTTP Request, Webhook

```json
{
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "GET",
    "url": "https://api.example.com/data",
    "authentication": "none",
    "options": {}
  }
}
```

**POST with Body**:
```json
{
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://api.example.com/data",
    "authentication": "none",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "key",
          "value": "={{ $json.body.value }}"
        }
      ]
    }
  }
}
```

### Database Nodes

**Structure**: Operation → Table → Fields

**Examples**: Postgres, MySQL, MongoDB

```json
{
  "type": "n8n-nodes-base.postgres",
  "parameters": {
    "operation": "select",
    "schema": "public",
    "table": "users",
    "limit": 100
  }
}
```

### Conditional Logic Nodes

**Structure**: Conditions → Branches

**Examples**: IF, Switch

```json
{
  "type": "n8n-nodes-base.if",
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
  }
}
```

### Switch Node

```json
{
  "type": "n8n-nodes-base.switch",
  "parameters": {
    "dataType": "string",
    "value1": "={{ $json.body.type }}",
    "rules": {
      "rules": [
        {
          "value2": "email",
          "output": 0
        },
        {
          "value2": "sms",
          "output": 1
        }
      ]
    }
  }
}
```

## Detailed Configuration Examples

### Slack: Post Message

```json
{
  "type": "n8n-nodes-base.slack",
  "name": "Slack",
  "parameters": {
    "resource": "message",
    "operation": "post",
    "channel": "#notifications",
    "text": "={{ $json.body.message }}",
    "otherOptions": {
      "includeLinkToWorkflow": false
    }
  },
  "credentials": {
    "slackApi": {
      "id": "1",
      "name": "Slack API"
    }
  },
  "position": [650, 300]
}
```

### HTTP Request: GET with Auth

```json
{
  "type": "n8n-nodes-base.httpRequest",
  "name": "HTTP Request",
  "parameters": {
    "method": "GET",
    "url": "https://api.example.com/users",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "httpHeaderAuth",
    "sendQuery": true,
    "queryParameters": {
      "parameters": [
        {
          "name": "limit",
          "value": "100"
        }
      ]
    }
  },
  "credentials": {
    "httpHeaderAuth": {
      "id": "2",
      "name": "API Key"
    }
  },
  "position": [450, 300]
}
```

### HTTP Request: POST JSON

```json
{
  "type": "n8n-nodes-base.httpRequest",
  "name": "HTTP Request",
  "parameters": {
    "method": "POST",
    "url": "https://api.example.com/data",
    "authentication": "none",
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={{ JSON.stringify($json.body) }}"
  },
  "position": [450, 300]
}
```

### Google Sheets: Append Row

```json
{
  "type": "n8n-nodes-base.googleSheets",
  "name": "Google Sheets",
  "parameters": {
    "resource": "sheet",
    "operation": "appendOrUpdate",
    "documentId": {
      "__rl": true,
      "value": "spreadsheet-id",
      "mode": "id"
    },
    "sheetName": {
      "__rl": true,
      "value": "Sheet1",
      "mode": "name"
    },
    "columns": {
      "mappingMode": "autoMapInputData",
      "value": {}
    }
  },
  "credentials": {
    "googleSheetsOAuth2Api": {
      "id": "3",
      "name": "Google Sheets"
    }
  },
  "position": [650, 300]
}
```

### IF Node: Multiple Conditions

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
        },
        {
          "value1": "={{ $json.body.amount }}",
          "operation": "largerEqual",
          "value2": "100"
        }
      ],
      "combineOperation": "all"
    }
  },
  "position": [450, 300]
}
```

## Validation Cycles

### Expected Iterations

| Complexity | Cycles | Time |
|------------|--------|------|
| Simple node | 1-2 | 30-60s |
| Moderate | 2-3 | 60-120s |
| Complex | 3-5 | 2-5min |

### Iteration Strategy

```
1. Configure required fields only
2. Validate → Fix errors
3. Add one optional feature
4. Validate → Fix errors
5. Repeat until complete
```

## Best Practices

### DO
- Start with `get_node_essentials`
- Configure required fields first
- Validate after each change
- Respect operation context
- Use dependencies when stuck
- Trust auto-sanitization

### DON'T
- Over-configure upfront
- Skip validation
- Ignore operation-specific requirements
- Configure optional fields without need
- Assume fields from similar nodes

## Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Wrong operation fields | Validation fails | Check operation requirements |
| Missing credentials | Runtime error | Add credential reference |
| Invalid expression | Execution fails | Use `={{ }}` wrapper |
| Wrong resource/operation combo | Silent failure | Verify combination exists |

## Quick Reference

### Minimum Configuration

```json
{
  "type": "n8n-nodes-base.{nodeType}",
  "name": "Node Name",
  "parameters": {
    // Required fields only
  },
  "position": [x, y]
}
```

### With Credentials

```json
{
  "type": "n8n-nodes-base.{nodeType}",
  "name": "Node Name",
  "parameters": { ... },
  "credentials": {
    "credentialType": {
      "id": "credentialId",
      "name": "Credential Name"
    }
  },
  "position": [x, y]
}
```

## Related Skills

- `n8n-mcp-tools-expert`: MCP tool usage
- `n8n-validation-expert`: Error interpretation
- `n8n-workflow-patterns`: Workflow design patterns
