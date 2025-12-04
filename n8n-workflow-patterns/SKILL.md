---
name: n8n-workflow-patterns
description: Proven architectural patterns for building n8n workflows. Covers 5 essential patterns - Webhook Processing, HTTP API Integration, Database Operations, AI Agent Workflows, and Scheduled Tasks.
---

# n8n Workflow Patterns

## Overview

Proven architectural patterns for building n8n workflows. Start with the simplest suitable pattern and add complexity as needed.

**Core Patterns**:
1. Webhook Processing (35% of workflows)
2. HTTP API Integration
3. Database Operations
4. AI Agent Workflows
5. Scheduled Tasks (28% of workflows)

## Pattern 1: Webhook Processing

**Use Case**: Receive HTTP requests → Process → Output

**Frequency**: 35% of workflows

### Basic Structure

```
Webhook → Process → Output
```

### Implementation

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "name": "Webhook",
      "parameters": {
        "httpMethod": "POST",
        "path": "process-data",
        "responseMode": "onReceived"
      },
      "position": [250, 300]
    },
    {
      "type": "n8n-nodes-base.code",
      "name": "Process",
      "parameters": {
        "mode": "runOnceForAllItems",
        "jsCode": "const data = $input.first().json.body;\nreturn [{json: {processed: data, timestamp: new Date().toISOString()}}];"
      },
      "position": [450, 300]
    },
    {
      "type": "n8n-nodes-base.slack",
      "name": "Notify",
      "parameters": {
        "resource": "message",
        "operation": "post",
        "channel": "#notifications",
        "text": "={{ $json.processed.message }}"
      },
      "position": [650, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Process", "type": "main", "index": 0}]]
    },
    "Process": {
      "main": [[{"node": "Notify", "type": "main", "index": 0}]]
    }
  }
}
```

### Variations

**With Validation**:
```
Webhook → Validate → IF Valid → Process → Output
                   → IF Invalid → Error Response
```

**With Response**:
```
Webhook → Process → Respond to Webhook
```

### Key Considerations

- Access data via `$json.body`
- Set appropriate `responseMode`
- Add validation for incoming data
- Handle errors gracefully

## Pattern 2: HTTP API Integration

**Use Case**: Fetch from REST APIs → Transform → Store/Use

### Basic Structure

```
Trigger → HTTP Request → Transform → Output
```

### Implementation

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "name": "Schedule",
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hoursInterval": 1}]
        }
      },
      "position": [250, 300]
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Fetch Data",
      "parameters": {
        "method": "GET",
        "url": "https://api.example.com/data",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "httpHeaderAuth"
      },
      "position": [450, 300]
    },
    {
      "type": "n8n-nodes-base.code",
      "name": "Transform",
      "parameters": {
        "mode": "runOnceForAllItems",
        "jsCode": "const data = $input.first().json;\nreturn data.items.map(item => ({json: {id: item.id, name: item.name}}));"
      },
      "position": [650, 300]
    },
    {
      "type": "n8n-nodes-base.googleSheets",
      "name": "Save",
      "parameters": {
        "resource": "sheet",
        "operation": "appendOrUpdate",
        "documentId": {"__rl": true, "value": "sheet-id", "mode": "id"},
        "sheetName": {"__rl": true, "value": "Data", "mode": "name"}
      },
      "position": [850, 300]
    }
  ],
  "connections": {
    "Schedule": {
      "main": [[{"node": "Fetch Data", "type": "main", "index": 0}]]
    },
    "Fetch Data": {
      "main": [[{"node": "Transform", "type": "main", "index": 0}]]
    },
    "Transform": {
      "main": [[{"node": "Save", "type": "main", "index": 0}]]
    }
  }
}
```

### Variations

**With Pagination**:
```
Trigger → Fetch Page → Has More? → Yes → Fetch Next
                     → No → Combine → Process
```

**With Error Handling**:
```
Trigger → HTTP Request → IF Success → Process
                       → IF Error → Retry/Alert
```

### Key Considerations

- Configure authentication properly
- Handle rate limits
- Implement pagination for large datasets
- Add retry logic for failures

## Pattern 3: Database Operations

**Use Case**: Read/Write/Sync database data

### Basic Structure

```
Trigger → Query → Process → Update
```

### Implementation

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "name": "Webhook",
      "parameters": {
        "httpMethod": "POST",
        "path": "sync-user"
      },
      "position": [250, 300]
    },
    {
      "type": "n8n-nodes-base.postgres",
      "name": "Get User",
      "parameters": {
        "operation": "select",
        "schema": "public",
        "table": "users",
        "where": {
          "values": [
            {
              "column": "id",
              "value": "={{ $json.body.userId }}"
            }
          ]
        },
        "limit": 1
      },
      "position": [450, 300]
    },
    {
      "type": "n8n-nodes-base.if",
      "name": "User Exists?",
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.id }}",
              "operation": "isNotEmpty"
            }
          ]
        }
      },
      "position": [650, 300]
    },
    {
      "type": "n8n-nodes-base.postgres",
      "name": "Update User",
      "parameters": {
        "operation": "update",
        "schema": "public",
        "table": "users",
        "where": {
          "values": [{"column": "id", "value": "={{ $json.id }}"}]
        }
      },
      "position": [850, 250]
    },
    {
      "type": "n8n-nodes-base.postgres",
      "name": "Insert User",
      "parameters": {
        "operation": "insert",
        "schema": "public",
        "table": "users"
      },
      "position": [850, 350]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Get User", "type": "main", "index": 0}]]
    },
    "Get User": {
      "main": [[{"node": "User Exists?", "type": "main", "index": 0}]]
    },
    "User Exists?": {
      "main": [
        [{"node": "Update User", "type": "main", "index": 0}],
        [{"node": "Insert User", "type": "main", "index": 0}]
      ]
    }
  }
}
```

### Variations

**Batch Sync**:
```
Schedule → Fetch Source → Compare → Create/Update/Delete
```

**Transaction Pattern**:
```
Start → Operations → Success → Commit
                   → Failure → Rollback
```

### Key Considerations

- Use parameterized queries
- Handle NULL values properly
- Implement idempotency
- Consider transaction boundaries

## Pattern 4: AI Agent Workflows

**Use Case**: AI agents with tools and memory

### Basic Structure

```
Input → AI Agent → Tools → Response
```

### Implementation

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "name": "Chat Input",
      "parameters": {
        "httpMethod": "POST",
        "path": "chat"
      },
      "position": [250, 300]
    },
    {
      "type": "@n8n/n8n-nodes-langchain.agent",
      "name": "AI Agent",
      "parameters": {
        "text": "={{ $json.body.message }}",
        "options": {
          "systemMessage": "You are a helpful assistant."
        }
      },
      "position": [450, 300]
    },
    {
      "type": "n8n-nodes-base.respondToWebhook",
      "name": "Respond",
      "parameters": {
        "respondWith": "text",
        "responseBody": "={{ $json.output }}"
      },
      "position": [650, 300]
    }
  ],
  "connections": {
    "Chat Input": {
      "main": [[{"node": "AI Agent", "type": "main", "index": 0}]]
    },
    "AI Agent": {
      "main": [[{"node": "Respond", "type": "main", "index": 0}]]
    }
  }
}
```

### With Tools

```
Input → AI Agent ←→ HTTP Tool
                ←→ Database Tool
                ←→ Code Tool
       → Response
```

### Key Considerations

- Configure appropriate model
- Define clear system prompts
- Implement tool functions
- Handle token limits
- Add memory for context

## Pattern 5: Scheduled Tasks

**Use Case**: Recurring automation workflows

**Frequency**: 28% of workflows

### Basic Structure

```
Schedule Trigger → Task → Complete
```

### Implementation

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "name": "Daily 9 AM",
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 9 * * *"
            }
          ]
        }
      },
      "position": [250, 300]
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Fetch Reports",
      "parameters": {
        "method": "GET",
        "url": "https://api.example.com/daily-report"
      },
      "position": [450, 300]
    },
    {
      "type": "n8n-nodes-base.code",
      "name": "Format Report",
      "parameters": {
        "mode": "runOnceForAllItems",
        "jsCode": "const data = $input.first().json;\nconst summary = `Daily Report:\\n- Total: ${data.total}\\n- New: ${data.new}`;\nreturn [{json: {summary}}];"
      },
      "position": [650, 300]
    },
    {
      "type": "n8n-nodes-base.slack",
      "name": "Send Report",
      "parameters": {
        "resource": "message",
        "operation": "post",
        "channel": "#reports",
        "text": "={{ $json.summary }}"
      },
      "position": [850, 300]
    }
  ],
  "connections": {
    "Daily 9 AM": {
      "main": [[{"node": "Fetch Reports", "type": "main", "index": 0}]]
    },
    "Fetch Reports": {
      "main": [[{"node": "Format Report", "type": "main", "index": 0}]]
    },
    "Format Report": {
      "main": [[{"node": "Send Report", "type": "main", "index": 0}]]
    }
  }
}
```

### Schedule Options

| Type | Example | Use Case |
|------|---------|----------|
| Interval | Every 5 minutes | Polling |
| Cron | `0 9 * * *` | Daily tasks |
| Specific days | Mon-Fri | Business hours |

### Key Considerations

- Consider timezone
- Handle overlapping executions
- Implement error notifications
- Add retry logic for failures

## Pattern Selection Guide

| Need | Pattern | Complexity |
|------|---------|------------|
| Receive external data | Webhook Processing | Low |
| Fetch external data | HTTP API Integration | Medium |
| Sync/store data | Database Operations | Medium |
| AI assistance | AI Agent Workflows | High |
| Recurring tasks | Scheduled Tasks | Low |

## Error Handling Patterns

### Basic Error Handling

```
Main Flow → Success → Continue
          → Error → Alert → Stop
```

### Retry Pattern

```
Operation → Success → Continue
          → Error → Retry (3x) → Alert
```

### Fallback Pattern

```
Primary API → Success → Continue
            → Error → Fallback API → Continue
```

## Implementation Checklist

### Planning
- [ ] Identify workflow pattern
- [ ] List required nodes
- [ ] Plan error handling
- [ ] Define success criteria

### Implementation
- [ ] Create trigger node
- [ ] Add processing nodes
- [ ] Configure connections
- [ ] Set up credentials

### Validation
- [ ] Validate workflow
- [ ] Test with sample data
- [ ] Verify error handling
- [ ] Check edge cases

### Deployment
- [ ] Enable workflow
- [ ] Monitor first runs
- [ ] Set up alerts
- [ ] Document workflow

## Best Practices

### DO
- Start with simplest pattern
- Add error handling
- Use meaningful node names
- Test with real data
- Monitor workflow health

### DON'T
- Over-engineer initially
- Skip error handling
- Use generic node names
- Deploy without testing
- Ignore monitoring

## Related Skills

- `n8n-node-configuration`: Node setup details
- `n8n-validation-expert`: Error handling
- `n8n-code-javascript`: Custom processing
- `n8n-expression-syntax`: Data access
