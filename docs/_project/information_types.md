---
status: new
change_type: expand
changed_on: 2025-11-14
---

# Memory Information Model

This document defines how information is categorized, validated, and maintained inside the cognitive-memory-core. It provides a conceptual foundation for volatility, reliability, validation, and sensor-based verification.

## 1. Information Types

Information stored in memory can be categorized into several types:

* **Static Knowledge**: Rarely changes (architecture, principles, theory).

* **Semi-Static Knowledge**: Changes sometimes (design decisions, configurations).

* **Dynamic Knowledge**: Changes frequently (code status, logs, runtime events).

* **Ephemeral Knowledge**: Short-lived information (weather, timestamps, transient states).

Each type influences how memory handles decay, validation, and access.

## 2. Volatility Levels

Volatility describes how quickly information becomes outdated:

* **low**: stable for months/years.

* **medium**: stable for days/weeks.

* **high**: stable for hours.

* **ephemeral**: stable for minutes or seconds.

Volatility determines:

* decay speed

* required validation frequency

* risk of using stale information

## 3. Reliability Levels

Reliability describes how trustworthy a piece of information is:

* **1.0**: fully verified (code sensor, test agent, external API)

* **0.7–0.99**: likely true, but not recently validated

* **0.4–0.69**: uncertain, human or AI guess

* **<0.4**: speculative, requires confirmation

Reliability influences retrieval ranking and when the system must revalidate data.

## 4. Validation Metadata

Every information block may include validation metadata:

```yaml
validation:
  validated_by: "code_test_agent"  # sensor/agent ID
  validated_at: "2025-11-14T10:00:00Z"  # last validation timestamp
  validity_window: "6h"  # how long the info is considered fresh
  reliability: 0.92  # normalized reliability score
```

### Fields

* **validated_by**: agent or system that confirmed the data.

* **validated_at**: when it was last checked.

* **validity_window**: how long the result is considered valid.

* **reliability**: numeric reliability score based on validation quality.

## 5. Sensors and Agents

Sensors provide validation for specific knowledge categories:

* **code sensor**: test runner verifying code correctness

* **fs sensor**: file watcher validating file modifications

* **runtime sensor**: monitors runtime metrics/events

* **external sensors**: weather APIs, HTTP services, etc.

Agents using sensors must update validation metadata after each check.

## 6. Staleness Detection

A block becomes stale when:

* `now - validated_at > validity_window`, **or**

* `reliability < threshold`, **or**

* `volatility == high` and validation is old

Stale data triggers:

* revalidation request

* downgrade in retrieval priority

## 7. Integration with Decay

Decay uses:

* volatility → determines decay speed

* reliability → influences archival

* validated_at → prevents archiving recently validated blocks

Dynamic and ephemeral data decays fastest.

Static knowledge decays slowest.

## 8. Integration with Reflection & Compression

Reflection:

* ignores or downranks outdated blocks

* can propose new validation relationships ("X depends on Y")

Compression:

* includes reliability metadata when summarizing

* may require fresh validation for high-volatility blocks

## 9. Proposed KnowledgeBlock Schema Extension

Logical (not yet implemented, design-level):

```yaml
id: ...
title: ...
content: ...
type: static | semi-static | dynamic | ephemeral
volatility: low | medium | high | ephemeral
validation:
  validated_at: timestamp
  validated_by: string
  validity_window: duration
  reliability: float (0.0–1.0)
```

## 10. Benefits of This Model

* Prevents the system from using stale data

* Provides AI agents with clarity about trustworthiness

* Enables safe combination of long-term and ephemeral knowledge

* Supports automated revalidation workflows

* Improves context quality and stability

## 11. Examples

### Example 1: Code Status
```
Type: dynamic
Volatility: high
Reliability: 0.3 (code-based, per definition unreliable)
Validation: code_sensor
Validity Window: immediate (changes with every code change)
Handling: Should not be stored as permanent knowledge block
```

### Example 2: Weather Information
```
Type: ephemeral
Volatility: ephemeral
Reliability: 0.85 (sensor-based, depends on API accuracy)
Validation: weather_sensor
Validity Window: 1 hour (weather changes)
Handling: Check sensor before use, don't cache long-term
```

### Example 3: Design Decision
```
Type: static
Volatility: low
Reliability: 0.95 (human-verified)
Validation: human_review
Validity Window: 6 months (review cycle)
Handling: Suitable for knowledge block storage
```

### Example 4: Configuration
```
Type: semi-static
Volatility: medium
Reliability: 0.8 (file-based, may change)
Validation: fs_sensor
Validity Window: 1 week
Handling: Re-validate on file change
```

## 12. Implementation Considerations

### Metadata Extensions

The `KnowledgeBlock` model should be extended to support:

```python
@dataclass
class KnowledgeBlock:
    # ... existing fields ...
    
    # New fields for information types
    information_type: str  # "static" | "semi-static" | "dynamic" | "ephemeral"
    volatility: str  # "low" | "medium" | "high" | "ephemeral"
    validation: Optional[Dict[str, Any]] = None  # validation metadata
    # validation contains:
    #   - validated_by: str
    #   - validated_at: datetime
    #   - validity_window: timedelta or str (e.g., "6h")
    #   - reliability: float (0.0-1.0)
```

### Sensor Integration

The system should support sensor plugins:

- **Code Sensor**: Validates information by checking current code state
- **File System Sensor**: Validates information by checking file modifications
- **Runtime Sensor**: Monitors runtime metrics and events
- **Weather Sensor**: Validates weather-related information via external APIs
- **API Sensor**: Validates information by calling external APIs
- **Human Review Sensor**: Tracks human verification status

### Retrieval Behavior

When retrieving information:

1. Check `validated_at` and `validity_window` - if expired, mark as stale
2. Check `reliability` - warn if reliability is low (< 0.7)
3. Check `volatility` - for high/ephemeral volatility, prefer real-time lookup
4. Check `sensor_dependency` - if sensor available, re-validate
5. For stale data, trigger revalidation request and downgrade retrieval priority

## 13. Future Implementation

This is a **planned feature** for future versions (v0.4.0+):

- [ ] Extend `KnowledgeBlock` model with volatility and validation fields
- [ ] Implement sensor plugin system
- [ ] Add staleness detection in retrieval
- [ ] Update decay policy to use volatility and reliability
- [ ] Integrate validation workflow with reflection and compression
- [ ] Add special handling for ephemeral information (don't store as permanent blocks)

## 14. Related Concepts

- **Decay Policy**: Uses volatility and reliability for archival decisions
- **Compression**: Fast-changing information should not be compressed (too volatile)
- **Reflection**: Should consider reliability when suggesting relationships
- **Retrieval**: Should prioritize fresh, high-reliability information
