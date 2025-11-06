# Documentation Markdown Rules

> **For detailed documentation architecture and strategy, see:** `.cursor/docs_guidelines/doc_architecture.md` and `.cursor/docs_guidelines/docs_guidelines.md`

## 📝 File Naming Convention

### **Required Format:**

```
role_YYYYMMDD_shortdesc.md
```

- `role` = document role (see roles below)
- `YYYYMMDD` = creation date
- `shortdesc` = kebab-case description (≤ 4 words)

### **Document Roles:**

- **spec** - Contract or system/API definition
- **plan** - Roadmaps, milestones, and future steps outline (strategic planning - NOT individual actionable tasks)
- **task** - Actionable checklist items
- **goal** - High-level objectives or desired outcomes
- **analysis** - Examination, comparison, or diagnosis
- **guide** - How-to instructions or procedural notes
- **history** - Change logs and evolution records

### **Examples:**

```
spec_20251015_api_definition.md
plan_20251101_text-box-auto-sizing.md
task_20251020_user-authentication.md
guide_20251015_deployment.md
analysis_20251010_performance.md
```

## 📋 Required Metadata Header

### **Every markdown file MUST start with:**

```markdown
---
role: plan              # spec | plan | task | goal | analysis | guide | history
status: draft           # draft | current | deprecated
updated: 2025-11-01
origin: ai/designer     # human | ai/planner | ai/worker | ai/designer | script
---
```

### **Metadata Fields:**

- **role** - Document role from list above (required)
- **status** - Document status (required)
- **updated** - Last modification date in YYYY-MM-DD format (required)
- **origin** - Who/what created the document (required)

## 🏗️ Document Structure

### **Required Header Structure:**

```markdown
# Document Title

## Overview

Brief description of what this document covers

## Section 1

Content here

## Section 2

Content here
```

### **Header Hierarchy:**

- **#** - Document title (only one per document)
- **##** - Main sections
- **###** - Subsections
- **####** - Sub-subsections

## 💻 Code Block Standards

### **Always specify language:**

```python
def example():
    pass
```

```bash
echo "command"
```

```yaml
key: value
```

### **Supported Languages:**

`bash`, `python`, `javascript`, `json`, `yaml`, `markdown`, `text`, `sql`, `html`, `css`, `typescript`, `typescriptreact`

## 🔗 Link Standards

### **Internal Links:**

```markdown
[Link Text](../folder/file.md)
[Link Text](#section-name)
```

### **External Links:**

```markdown
[Link Text](https://example.com)
```

### **Requirements:**

- **All internal links MUST work** - No broken references
- **Use relative paths** - For internal documentation

## 🖼️ Image Standards

```markdown
![Alt Text](path/to/image.png)
```

### **Requirements:**

- **Alt text is REQUIRED** - For accessibility
- **Use descriptive alt text** - Not just "image" or "screenshot"

## 📊 Table Standards

```markdown
| Column 1 | Column 2 |
| -------- | -------- |
| Data 1   | Data 2   |
```

## 🚫 Common Mistakes to Avoid

### **Naming:**

- ❌ `my-document.md` (no role prefix)
- ❌ `plan document.md` (spaces in filename)
- ❌ `PLAN_20251101.md` (wrong case)
- ✅ `plan_20251101_text-box-sizing.md`

### **Metadata:**

- ❌ Missing metadata header
- ❌ Wrong date format (use YYYY-MM-DD)
- ❌ Missing required fields

### **Formatting:**

- ❌ Inconsistent header hierarchy
- ❌ Missing code block language
- ❌ Broken internal links
- ❌ Images without alt text

## 🔄 When Updating Documents

1. **Update `updated` date** - In metadata header
2. **Update `status`** - If status changes (draft → current)
3. **Keep metadata valid** - All required fields present

## 📁 File Location Rules

### **Unclassified Documents**

When creating a document that doesn't clearly fit into an existing classified location, use:

- **Location**: `_AGENT_WORKSPACE/z_unclassified_docs/`
- **Purpose**: Temporary storage for documents that need classification
- **Naming**: Must still follow `role_YYYYMMDD_shortdesc.md` format

### **Examples of Unclassified Documents:**

- Analysis reports that need review
- Diagnostic outputs
- Temporary documentation
- Documents awaiting proper classification

### **After Classification:**

Once a document's proper location is determined, it should be moved to the appropriate directory and potentially renamed if needed.

## 🎯 Enforcement

### **These rules are MANDATORY for all agents:**

- **All new documents** - Must follow naming and metadata format
- **Unclear classification** - Place in `_AGENT_WORKSPACE/z_unclassified_docs/`
- **All updates** - Must maintain compliance
- **Refer to docs_guidelines/** - For detailed architecture and strategy
