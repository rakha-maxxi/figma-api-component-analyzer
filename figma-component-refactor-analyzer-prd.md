# PRD: Figma Component Refactor Analyzer

## 1. Overview

This product is a `Figma API-based analyzer` for `Design Ops` and `Product Design` teams.

Its purpose is to inspect Figma file structure and answer a focused set of questions:

- where are real component instances being used?
- where are designers still relying on native frames or groups?
- which components are too large, too section-like, or too page-like?
- which components should be decomposed or refactored?
- what short refactor recommendation should be suggested for each finding?

This is not a generic analytics product. It is a `component health and refactor recommendation tool`.

The first target use case is MAI files such as:

- `MM+`
- `FS+`
- other MAI project files with many pages and mixed component maturity

---

## 2. Product Goal

The main goal is to identify:

1. `component usage`
2. `oversized components`
3. `repeated native structures`
4. `refactor opportunities`

The analyzer should not only show counts. It should also produce a short recommendation, for example:

- `Section-like component detected. Consider refactoring into scaffold with slots.`
- `Repeated metric block found. Candidate for compound component.`
- `Large content-specific card detected. Keep pattern local and extract card shell + stat pair.`
- `Repeated native frame resembles reusable section header. Consider promoting to project UI kit.`

---

## 3. Problem Statement

In MAI, many files contain:

- local components
- native frames used repeatedly
- large components that are closer to sections or templates
- inconsistent component usage across files

Manual audit helps, but it is hard to scale.

The current need is not only to know `how many instances exist`, but also:

- which structures are over-componentized
- which structures are under-componentized
- which structures are good refactor candidates

There is a gap between raw Figma structure and Design Ops action.

This product exists to bridge that gap.

---

## 4. Target Users

### Primary User

- `Design Ops`

### Secondary Users

- `PD Lead`
- `Product Designers`
- `Engineers`

---

## 5. Success Criteria

The product is successful if it can:

- analyze one Figma file using the Figma API
- identify real component usage with good accuracy
- flag oversized or section-like components
- surface repeated native structures
- generate short, understandable refactor recommendations
- produce output that helps Design Ops decide:
  - keep local
  - promote to project UI kit
  - decompose
  - leave as pattern/reference

---

## 6. Non-Goals

- not a Figma editing plugin
- not a visual pixel comparison tool
- not a full design system management platform
- not a generic “AI dashboard” product
- not a guaranteed perfect detached-component detector

---

## 7. Core Questions

The analyzer must answer:

- How much is this file using real components?
- Which components are too large to be healthy reusable building blocks?
- Which repeated native structures should become UI kit components?
- Which existing components should be decomposed into slots, shells, or smaller compounds?
- Which structures should stay local because they are still pattern-level?

---

## 8. Figma API Scope

The system should work with:

- `personal access token`
- `file key`

The implementation should use Figma REST API file endpoints, especially:

- `GET /v1/files/:key`
- optionally `GET /v1/files/:key/nodes`

The token owner must already have access to the file.

This PRD assumes use on `Figma Pro` with normal REST API access, not enterprise-only org analytics.

---

## 9. Input

### Required Input

- `figma_personal_access_token`
- `file_key`

### Optional Input

- `project_name`
- `platform`
- `analysis_scope`
- `page_name`
- `node_ids`

---

## 10. Output

The analyzer should output structured data with:

- file summary
- usage metrics
- detected oversized components
- repeated native structures
- candidate reusable patterns
- short refactor recommendations

Output formats:

- `JSON` required
- `Markdown summary` optional
- `CSV` optional

---

## 11. Node Types to Analyze

The analyzer should classify and treat these node types differently:

### `COMPONENT`

- master reusable component
- important for reusable inventory
- must be checked for complexity and size

### `COMPONENT_SET`

- variant container
- useful for inventory, not direct usage

### `INSTANCE`

- real usage of a reusable component
- strongest sign of component adoption

### `FRAME`

- likely place where native repeated structures or pseudo-components appear
- important for section-level and layout-level detection

### `GROUP`

- weaker structural wrapper
- still relevant for repeated manual patterns

### Supporting Types

- `TEXT`
- `RECTANGLE`
- `ELLIPSE`
- `VECTOR`
- `SECTION`

These support structural analysis but are not top-level reusable candidates by themselves.

---

## 12. Primary Detection Domains

### 12.1 Component Usage Detection

The analyzer must detect:

- total `INSTANCE` nodes
- total `COMPONENT` nodes
- total `COMPONENT_SET` nodes
- real usage of components in analysis scope

### 12.2 Oversized Component Detection

The analyzer must detect components that are too large, such as:

- section-like blocks
- template-like blocks
- page-like blocks
- feature-specific mega-components

These usually have:

- many child layers
- multiple semantic regions
- large dimensions
- mixed concerns
- many text regions
- too much content specificity

### 12.3 Repeated Native Structure Detection

The analyzer must detect:

- repeated `FRAME` or `GROUP` structures
- repeated UI anatomy built without instances
- likely candidates for UI kit promotion

### 12.4 Refactor Recommendation Detection

The analyzer must turn structural findings into actionable recommendations.

Examples:

- `decompose into section shell + slot-based content`
- `extract text pairing into compound component`
- `keep as local pattern; not stable enough for UI kit`
- `promote repeated native card to project UI kit`
- `reduce component scope; current component is too page-specific`

---

## 13. Product Logic

### 13.1 Component Usage Metric

The analyzer should calculate:

```text
component_usage_rate = total_instances / (total_instances + native_candidate_count)
```

Where:

- `total_instances` = count of `INSTANCE` nodes
- `native_candidate_count` = eligible `FRAME` and `GROUP` nodes that look reusable but are not using instances

Purpose:

- measure reusable component adoption against likely reusable manual structures

### 13.2 Large Component Detection Logic

Each `COMPONENT` should receive a `complexity score`.

Suggested signals:

- child count
- max nested depth
- text node count
- semantic region count
- size relative to screen
- number of optional subareas

Suggested initial thresholds:

- `child_count > 12`
- or `depth > 5`
- or `semantic_regions > 3`
- or `width/height strongly resembles section or page block`

If thresholds are exceeded, the component should be classified as one of:

- `large_component`
- `section_like_component`
- `template_like_component`
- `page_like_component`

### 13.3 Native Repetition Detection Logic

The analyzer should create structural signatures for eligible `FRAME` and `GROUP` nodes based on:

- child node types
- child ordering
- layout mode
- spacing and padding
- title/subtitle/value anatomy
- presence of icon, label, chevron, button, etc.
- overall depth and region count

If similar signatures repeat `2+ times`, group them into a repeated native cluster.

### 13.4 Candidate Component Level Inference

The analyzer should infer likely target level:

- `atomic`
- `compound`
- `scaffold`
- `pattern`

Inference proposal:

#### `atomic`

- one small semantic unit
- example:
  - chip
  - badge
  - icon + label

#### `compound`

- 2-4 related semantic parts
- example:
  - text pairing
  - stat pair
  - section header
  - list item with trailing action

#### `scaffold`

- structural wrapper with slot-like content area
- example:
  - section shell
  - card shell
  - dialog shell
  - header shell

#### `pattern`

- larger feature composition
- example:
  - dashboard hero
  - activity summary block
  - feature comparison section

---

## 14. Refactor Recommendation Engine

This is the most important part of the product.

The analyzer should not stop at detection. It should map findings to short recommendations.

### 14.1 Recommendation Types

#### A. `Decompose to Scaffold`

Use when:

- component is too large
- structure has multiple semantic regions
- component behaves like section/template

Recommendation examples:

- `Refactor into section shell with title, action, and content slots.`
- `Refactor into card scaffold and move content-specific blocks to local composition.`

#### B. `Extract Compound`

Use when:

- repeated native structure is stable and mid-sized
- repeated block appears across pages/files

Recommendation examples:

- `Extract as text pairing compound component.`
- `Extract as summary stat row component.`

#### C. `Promote to Project UI Kit`

Use when:

- repeated native pattern appears often
- anatomy is stable
- useful across multiple files in same project

Recommendation example:

- `Promote to project UI kit as reusable product summary card.`

#### D. `Keep Local`

Use when:

- repeated block is still exploratory
- business-specific content is too strong
- structure varies too much

Recommendation example:

- `Keep local for now; pattern still too feature-specific for shared UI kit.`

#### E. `Downgrade from Component to Pattern`

Use when:

- existing component is too large and too specific
- current component should not remain master reusable component

Recommendation example:

- `Treat this as pattern/reference instead of reusable component; extract shell and compounds separately.`

### 14.2 Recommendation Output Shape

Each recommendation should contain:

- `finding_type`
- `target_node_id`
- `target_node_name`
- `confidence`
- `recommendation_type`
- `recommendation_text`
- `reason_summary`

Example:

```json
{
  "finding_type": "section_like_component",
  "target_node_id": "123:456",
  "target_node_name": "Sales Overview Section",
  "confidence": "high",
  "recommendation_type": "decompose_to_scaffold",
  "recommendation_text": "Refactor into section shell with title, action, and content slots.",
  "reason_summary": "Component has 18 children, 4 semantic regions, and behaves more like a section than a reusable UI unit."
}
```

---

## 15. Main Metrics

The main metrics should be practical and explainable.

### `component_usage_rate`

What it means:

- how much reusable component adoption exists relative to reusable-looking native structures

### `large_component_count`

What it means:

- how many master components are too large or too section-like

### `section_like_component_count`

What it means:

- how many components appear to be reusable sections rather than smaller building blocks

### `repeated_native_cluster_count`

What it means:

- how many duplicated non-component structural groups exist

### `promotion_candidate_count`

What it means:

- how many repeated native structures look strong enough for UI kit review

### `refactor_candidate_count`

What it means:

- how many existing large components deserve decomposition or scope reduction

---

## 16. Suggested Dashboard Sections

The UI should prioritize action, not just count.

### A. Overview

- component usage rate
- large component count
- repeated native cluster count
- refactor candidate count

### B. Large Components

List oversized components with:

- node name
- type
- size/complexity
- section-like or template-like label
- short refactor recommendation

### C. Repeated Native Candidates

List repeated native clusters with:

- semantic name
- occurrence count
- likely target level
- recommendation

### D. Recommendations

A short prioritized feed such as:

- `Refactor 3 section-like components into scaffolds`
- `Promote 5 repeated summary blocks into compounds`
- `Keep 2 dashboard patterns local`

---

## 17. UX Principle

The analyzer should feel like a `Design Ops review assistant`, not a flashy AI dashboard.

The user should quickly understand:

- what is being overused or underused
- what is too big
- what should be decomposed
- what should be promoted
- what should stay local

The metrics should support decisions, not impress people with abstract scoring.

---

## 18. API Design

### `POST /analyze-file`

Request:

```json
{
  "file_key": "abc123",
  "project_name": "FS+",
  "platform": "Mobile"
}
```

Response:

```json
{
  "analysis_id": "analysis_001",
  "summary": {
    "component_usage_rate": 0.43,
    "large_component_count": 4,
    "section_like_component_count": 3,
    "repeated_native_cluster_count": 17,
    "promotion_candidate_count": 6,
    "refactor_candidate_count": 5
  }
}
```

### `GET /analysis/{id}`

Returns full analysis results.

### `GET /analysis/{id}/large-components`

Returns oversized component findings and recommendations.

### `GET /analysis/{id}/promotion-candidates`

Returns repeated native structures and likely target component level.

### `GET /analysis/{id}/recommendations`

Returns prioritized short recommendations.

---

## 19. Suggested Technical Stack

### Backend

- `Python`
- `FastAPI`
- `httpx` or `requests`
- `Pydantic`

### Storage

- `SQLite` for MVP
- optional `PostgreSQL` later

### Output Layer

- JSON first
- dashboard second

---

## 20. Security

The personal access token must:

- stay in backend only
- be stored in environment variable or secure config
- never be exposed in frontend code

---

## 21. Risks

### False Positives

- analyzer may classify some frames as reusable candidates when they are not

### False Negatives

- analyzer may miss some repeated patterns

### Over-Simplified Recommendations

- recommendation engine may be too generic if semantic naming is weak

### Rate Limits

- too many file requests may hit Figma API limits

Mitigation:

- caching
- backoff
- one-file-at-a-time MVP

---

## 22. MVP Scope

The MVP should support:

- analyze one file
- classify node types
- compute component usage rate
- detect large/section-like components
- detect repeated native structures
- return short recommendation text

Out of scope for MVP:

- cross-project trend analytics
- screenshot comparison
- automatic Figma write-back
- full design system governance workflow

---

## 23. Example End-to-End Output

Example summary:

- `Component usage rate is 43%.`
- `4 large components detected.`
- `3 of them are section-like.`
- `17 repeated native clusters found.`
- `6 promotion candidates identified.`

Example recommendations:

- `Refactor Sales Overview Section into section shell with title, action, and content slots.`
- `Extract repeated text pairing block into compound component.`
- `Promote repeated filter chip group into project UI kit.`
- `Keep dashboard hero local; decompose header shell and stat cards only.`

---

## 24. Next Step After PRD

Build the analyzer in this order:

1. Figma file fetcher
2. node parser
3. large component classifier
4. repeated native signature clustering
5. recommendation generator
6. JSON report

That order keeps the product aligned with the main goal: `component refactor intelligence`, not generic analytics.
