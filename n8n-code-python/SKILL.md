---
name: n8n-code-python
description: Expert guidance for writing Python in n8n Code nodes. Covers when to use Python vs JavaScript, standard library usage, data patterns, and common pitfalls. JavaScript is recommended for 95% of cases.
---

# n8n Python Code Node

## Overview

Guide for writing Python in n8n Code nodes. **Important**: JavaScript should be your first choice for 95% of cases. Use Python only when specific Python features are needed.

**Critical Rule**: Always return `[{"json": {...}}]` format.

## When to Use Python

### Use Python For
- Complex regex operations
- Advanced date/time manipulation
- Hash generation and validation
- Statistical calculations
- Complex string processing

### Use JavaScript Instead For
- Simple data transformation
- Basic filtering and mapping
- JSON manipulation
- Most webhook processing
- General workflow logic

## Available Standard Libraries

Python in n8n supports standard library only:

| Library | Use Case | Example |
|---------|----------|---------|
| `datetime` | Date/time operations | `datetime.now()` |
| `re` | Regular expressions | `re.match(pattern, text)` |
| `json` | JSON parsing | `json.loads(string)` |
| `hashlib` | Hashing | `hashlib.sha256()` |
| `math` | Mathematical operations | `math.sqrt(x)` |
| `collections` | Data structures | `Counter, defaultdict` |
| `itertools` | Iteration tools | `groupby, chain` |

### NOT Available

```python
# These will NOT work - no external libraries
import requests    # NOT available
import pandas      # NOT available
import numpy       # NOT available
import beautifulsoup4  # NOT available
```

## Return Format Requirements

### Valid Return Format

```python
# Single item
return [{"json": {"field": "value"}}]

# Multiple items
return [
    {"json": {"id": 1, "name": "First"}},
    {"json": {"id": 2, "name": "Second"}}
]
```

### Invalid Return Formats

```python
# WRONG - Missing list wrapper
return {"json": {"field": "value"}}

# WRONG - Missing json key
return [{"field": "value"}]

# WRONG - Plain value
return "result"
```

## Data Access

### Access Input Data

```python
# All items (Run Once for All Items mode)
items = _input.all()

# First item
first = _input.first()

# Current item (Run Once for Each Item mode)
item = _input.item
```

### Webhook Data Structure

**Critical**: Webhook data nests under `["body"]`.

```python
# WRONG
name = _input.first().json["name"]

# CORRECT
name = _input.first().json["body"]["name"]
```

### Safe Dictionary Access

```python
# Use .get() for safe access with defaults
data = _input.first().json
name = data.get("body", {}).get("name", "Unknown")
count = data.get("body", {}).get("count", 0)
```

## Common Patterns

### Pattern 1: Data Transformation

```python
items = _input.all()

result = []
for item in items:
    data = item.json
    result.append({
        "json": {
            "fullName": f"{data.get('firstName', '')} {data.get('lastName', '')}".strip(),
            "email": data.get("email", "").lower(),
            "processed": True
        }
    })

return result
```

### Pattern 2: Filtering

```python
items = _input.all()

filtered = [
    {"json": item.json}
    for item in items
    if item.json.get("status") == "active"
]

return filtered if filtered else [{"json": {"message": "No active items"}}]
```

### Pattern 3: Aggregation

```python
items = _input.all()

total = sum(item.json.get("amount", 0) for item in items)
count = len(items)

return [{
    "json": {
        "totalAmount": total,
        "itemCount": count,
        "average": total / count if count > 0 else 0
    }
}]
```

### Pattern 4: Regex Processing

```python
import re

items = _input.all()
pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

result = []
for item in items:
    text = item.json.get("body", {}).get("text", "")
    emails = re.findall(pattern, text)
    result.append({
        "json": {
            "originalText": text,
            "extractedEmails": emails,
            "emailCount": len(emails)
        }
    })

return result
```

### Pattern 5: Date/Time Operations

```python
from datetime import datetime, timedelta

items = _input.all()

result = []
for item in items:
    date_str = item.json.get("body", {}).get("date", "")

    if date_str:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        result.append({
            "json": {
                "original": date_str,
                "formatted": dt.strftime("%Y-%m-%d"),
                "dayOfWeek": dt.strftime("%A"),
                "nextWeek": (dt + timedelta(days=7)).isoformat()
            }
        })

return result if result else [{"json": {"error": "No dates processed"}}]
```

### Pattern 6: Hash Generation

```python
import hashlib
import json as json_lib

items = _input.all()

result = []
for item in items:
    data = item.json.get("body", {})

    # Create deterministic hash
    data_str = json_lib.dumps(data, sort_keys=True)
    hash_value = hashlib.sha256(data_str.encode()).hexdigest()

    result.append({
        "json": {
            "data": data,
            "hash": hash_value,
            "hashShort": hash_value[:8]
        }
    })

return result
```

### Pattern 7: Statistical Analysis

```python
import math
from collections import Counter

items = _input.all()
values = [item.json.get("value", 0) for item in items]

if values:
    n = len(values)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n
    std_dev = math.sqrt(variance)

    return [{
        "json": {
            "count": n,
            "sum": sum(values),
            "mean": mean,
            "min": min(values),
            "max": max(values),
            "stdDev": std_dev,
            "mode": Counter(values).most_common(1)[0][0] if values else None
        }
    }]

return [{"json": {"error": "No values to analyze"}}]
```

### Pattern 8: Grouping

```python
from collections import defaultdict

items = _input.all()
grouped = defaultdict(list)

for item in items:
    key = item.json.get("category", "uncategorized")
    grouped[key].append(item.json)

return [
    {
        "json": {
            "category": category,
            "count": len(items),
            "items": items
        }
    }
    for category, items in grouped.items()
]
```

## Common Mistakes & Fixes

| Mistake | Problem | Fix |
|---------|---------|-----|
| External imports | `import pandas` fails | Use standard library only |
| Wrong return format | Missing list/json wrapper | Return `[{"json": {...}}]` |
| Direct key access | `data["key"]` raises KeyError | Use `data.get("key", default)` |
| Webhook nesting | `json["field"]` fails | Use `json["body"]["field"]` |
| Empty return | Returns `None` | Always return valid list |

## Error Handling

```python
try:
    items = _input.all()

    result = []
    for item in items:
        data = item.json.get("body", {})

        # Validate required fields
        if not data.get("required_field"):
            raise ValueError("Missing required_field")

        result.append({
            "json": {
                "processed": data["required_field"]
            }
        })

    return result

except Exception as e:
    return [{
        "json": {
            "error": True,
            "message": str(e),
            "type": type(e).__name__
        }
    }]
```

## Best Practices

### DO
- Use `.get()` for safe dictionary access
- Always return proper list format
- Handle empty inputs gracefully
- Use standard library functions
- Add appropriate error handling

### DON'T
- Import external libraries (requests, pandas, etc.)
- Access dictionary keys directly without checking
- Return plain values or improperly formatted data
- Assume webhook data is at root level
- Leave functions without return statements

## Quick Reference Template

```python
# Template for Python Code Node
items = _input.all()

result = []
for item in items:
    data = item.json.get("body", item.json)  # Handle webhook and non-webhook

    # Your processing logic here
    processed = {
        "original": data,
        "processed": True
    }

    result.append({"json": processed})

return result if result else [{"json": {"message": "No items processed"}}]
```

## Related Skills

- `n8n-code-javascript`: JavaScript Code node guide (preferred)
- `n8n-expression-syntax`: Expression syntax reference
- `n8n-validation-expert`: Validation and error fixing
