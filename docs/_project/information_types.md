---
status: new
change_type: expand
changed_on: 2025-11-14
---

# Information Types and Reliability Model

## Overview

This document describes a conceptual model for handling different types of information in the memory system, based on their change rate, reliability, and validation requirements.

## Core Concepts

### 1. Information Types by Change Rate

Information can be categorized by how quickly it changes:

- **Fast-changing information**: 
  - Code status (build status, test results, deployment state)
  - Real-time sensor data (weather, system metrics)
  - Ephemeral state (current user sessions, active processes)
  - **Handling**: These should be handled differently - not stored as permanent knowledge blocks, but rather as transient state or with explicit expiration

- **Slow-changing information**:
  - Documentation
  - Design decisions
  - Historical facts
  - **Handling**: These are suitable for traditional knowledge blocks

### 2. Reliability and Trustworthiness

Information has a **reliability level** that depends on its source:

- **Code-based information**: 
  - **Per definition not reliable** - code changes, so information derived from code is inherently unstable
  - Examples: "This function does X" (may be outdated if code changed)
  - **Implication**: Code-derived knowledge should be marked as unreliable and require frequent re-validation

- **Sensor-based information**:
  - Depends on sensor accuracy and freshness
  - Examples: "Is it raining now?" - requires checking a weather sensor
  - **Implication**: Has a validation date and depends on sensor availability

- **Human-verified information**:
  - Higher reliability but may still become outdated
  - Examples: Design documents, approved specifications
  - **Implication**: Can be trusted but should have review dates

### 3. Validation and Freshness

Information has:

- **Validation date**: When the information was last verified
- **Expiration date**: When the information becomes stale
- **Sensor dependency**: What sensor or source validates this information
  - Example: "code_sensor" - validates by checking current code state
  - Example: "weather_sensor" - validates by checking weather API
  - Example: "human_review" - validates by human verification

### 4. Examples

#### Example 1: Code Status
```
Type: fast-changing
Reliability: low (code-based, per definition unreliable)
Validation: code_sensor
Expiration: immediate (changes with every code change)
Handling: Should not be stored as permanent knowledge block
```

#### Example 2: Weather Information
```
Type: fast-changing
Reliability: medium (sensor-based)
Validation: weather_sensor
Expiration: 1 hour (weather changes)
Handling: Check sensor before use, don't cache long-term
```

#### Example 3: Design Decision
```
Type: slow-changing
Reliability: high (human-verified)
Validation: human_review
Expiration: 6 months (review cycle)
Handling: Suitable for knowledge block storage
```

## Implementation Considerations

### Metadata Extensions

The `KnowledgeBlock` model should be extended to support:

```python
@dataclass
class KnowledgeBlock:
    # ... existing fields ...
    
    # New fields for information types
    information_type: str  # "fast-changing" | "slow-changing"
    reliability: float  # 0.0 to 1.0
    validation_date: Optional[datetime]
    expiration_date: Optional[datetime]
    sensor_dependency: Optional[str]  # "code_sensor", "weather_sensor", etc.
    requires_revalidation: bool
```

### Sensor Integration

The system should support sensor plugins:

- **Code Sensor**: Validates information by checking current code state
- **Weather Sensor**: Validates weather-related information
- **API Sensor**: Validates information by calling external APIs
- **Human Review Sensor**: Tracks human verification status

### Retrieval Behavior

When retrieving information:

1. Check `expiration_date` - if expired, mark as stale
2. Check `sensor_dependency` - if sensor available, re-validate
3. Check `reliability` - warn if reliability is low
4. For fast-changing information, prefer real-time lookup over cached blocks

## Future Implementation

This is a **planned feature** for future versions (v0.4.0+):

- [ ] Extend `KnowledgeBlock` model with reliability fields
- [ ] Implement sensor plugin system
- [ ] Add validation workflow
- [ ] Update retrieval to respect reliability and expiration
- [ ] Add special handling for fast-changing information

## Related Concepts

- **Decay Policy**: Can use reliability and expiration for archival decisions
- **Compression**: Fast-changing information should not be compressed (too volatile)
- **Reflection**: Should consider reliability when suggesting relationships

