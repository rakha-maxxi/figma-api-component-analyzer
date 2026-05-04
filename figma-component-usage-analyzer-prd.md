# PRD: Figma Component Usage Analyzer for MAI Design Ops

## 1. Overview

This project is a `Design Ops analytics tool` that connects to Figma using a `personal access token` and analyzes file structure to understand:

- component usage
- instance adoption
- repeated native frames or plain elements
- possible detached component behavior
- cross-file component dependency
- large or page-like components
- candidate patterns for UI kit promotion

The output will support a dashboard and reporting workflow for `MAI Stream`, beginning with projects like `MM+` and `FS+`.

This product is intended to help Design Ops move from manual visual audit toward:

- measurable component usage insight
- repeatable detection logic
- evidence-based promotion decisions
- stronger designer and engineer alignment

This system is not meant to replace design judgment. It should provide structured evidence and heuristics that support Design Ops review.

---

## 2. Background

### Current MAI Context

MAI has:

- many projects
- multiple platforms such as mobile, tablet, and web
- many design files inside one project
- mixed maturity of component usage
- repeated local components
- repeated native frames
- cross-file component references
- large components that are closer to template page or feature pattern level

At the moment, much of the analysis is still manual. This is useful, but difficult to scale.

### Design Ops Need

Design Ops needs a way to:

- detect where components are not being used
- detect where designers manually rebuild similar structures
- identify project-level UI kit opportunities
- track design system adoption over time
- compare projects and files using the same logic

---

## 3. Problem Statement

Current Design Ops auditing depends heavily on manual observation. This creates several limitations:

- findings are time-consuming to produce
- large file sets are difficult to review consistently
- duplication is easy to miss
- it is hard to quantify component usage health
- promotion decisions rely on memory and visual comparison
- it is difficult to show evidence to PD Lead or engineer using metrics

There is also no reliable automated signal for:

- how much a file uses real component instances
- how much a file rebuilds repeated native structures
- where local patterns are emerging without being systemized

---

## 4. Product Vision

Create a tool that ingests Figma file structure and produces a usable `Design Ops health view` for MAI:

- what is componentized
- what is not
- what is repeated
- what may be detached
- what is too large
- what should be candidate for project UI kit

The first version should work with `Figma Pro` using a `personal access token`, without requiring Enterprise-only features.

---

## 5. Goals

### Primary Goals

- analyze component usage inside Figma files accessible by the token owner
- detect repeated non-component structures using heuristics
- detect component instances and cross-file component relationships
- generate metrics useful for Design Ops governance
- produce JSON output suitable for a dashboard

### Secondary Goals

- support longitudinal tracking over time
- support comparison across MAI projects
- reduce manual audit overhead
- help connect file evidence with designer and engineer interviews

---

## 6. Non-Goals

- not a replacement for design review
- not a pixel-perfect visual diff engine
- not an official Figma enterprise analytics clone
- not a plugin for editing Figma files
- not a tool that can definitively prove intent
- not a direct code generation system

---

## 7. Key Constraints

### 7.1 Figma Plan Constraint

The system must work on `Figma Pro` using a `personal access token`.

This means:

- access is limited to files the token owner can access
- no dependency on enterprise-only organization analytics features
- rate limits must be respected

### 7.2 Detection Constraint

Some findings are exact, and some are heuristic.

Exact examples:

- `INSTANCE` vs `FRAME`
- cross-file component reference if component metadata exists
- component count
- component set count

Heuristic examples:

- possible detached component
- repeated native frame cluster
- large component that behaves like template/page
- similarity between plain structures

The product must clearly distinguish `exact` signals from `heuristic` signals.

### 7.3 Security Constraint

The personal access token must not be hardcoded in frontend code.

The token should be stored securely in:

- environment variables
- local secret config
- secure backend secret store

---

## 8. Target Users

### Primary User

- `Design Ops`

### Secondary Users

- `PD Lead`
- `Product Designers`
- `Engineers`

### Tertiary Audience

- `Head of Product Designer`
- stream stakeholders who need evidence-based UI kit direction

---

## 9. Core Questions the Product Must Answer

The tool should help answer:

- How much of this file uses actual component instances?
- Which plain/native structures are repeated often?
- Which repeated structures are good candidates for project UI kit?
- Which components are too large to be healthy building blocks?
- Where do files depend on components from other files?
- Which parts of the design system are adopted vs ignored?
- Which files show a higher level of local component rebuilding?

---

## 10. Product Scope

The project will include:

1. `Figma ingestion service`
2. `Node tree parser`
3. `Heuristic analyzer`
4. `Metrics generator`
5. `Storage layer`
6. `API layer`
7. `Dashboard or report output`

---

## 11. Functional Requirements

### 11.1 File Ingestion

The system must:

- fetch Figma file JSON using a file key
- optionally fetch selected nodes only
- support single-file analysis first
- later support multiple-file/project analysis

Required input:

- `personal_access_token`
- `file_key`

Optional input:

- `node_ids`
- `project_name`
- `platform`
- `analysis_label`

### 11.2 Tree Parsing

The system must recursively parse:

- `COMPONENT`
- `COMPONENT_SET`
- `INSTANCE`
- `FRAME`
- `GROUP`
- `TEXT`
- `RECTANGLE`
- `ELLIPSE`
- `VECTOR`
- `SECTION`

The parser should retain:

- node id
- node name
- node type
- parent
- children
- layout mode
- sizing mode
- spacing
- padding
- corner radius
- fills
- strokes
- text style
- component id if instance

### 11.2.1 Node Classification Proposal

The analyzer must not treat all nodes equally. It should classify nodes into `design-system-relevant roles` before calculating metrics.

#### A. `COMPONENT`

Definition:

- a publishable or reusable master component node defined in Figma

Design Ops interpretation:

- this is a source-of-truth reusable unit
- should be counted as part of the reusable inventory
- should also be checked for size and complexity

Count toward:

- `total_components`
- `large_component_count` if it crosses thresholds

Do not count toward:

- `native_candidate_count`

#### B. `COMPONENT_SET`

Definition:

- a variant wrapper that groups related component variants

Design Ops interpretation:

- this is not direct usage
- it is a container for reusable component states or sizes
- useful for inventory and variant governance, but should not inflate usage metrics

Count toward:

- `total_component_sets`

Do not count toward:

- `instance_usage_rate`
- `component_vs_native_ratio`

#### C. `INSTANCE`

Definition:

- a real usage of a reusable component in a design file

Design Ops interpretation:

- strongest signal of design-system adoption
- should be the main numerator in component usage metrics

Count toward:

- `total_instances`
- `instance_usage_rate`
- `cross_file_component_dependency_count` when source component lives outside the active file

#### D. `FRAME`

Definition:

- a layout or grouping container used directly in the file

Design Ops interpretation:

- may represent page structure, section structure, or a manually-built pseudo-component
- this is the primary place where repeated native patterns are likely to appear

Count toward:

- `total_frames`
- `native_candidate_count` if eligible
- `plain_repeated_block_count` if clustered with similar frames
- `possible_detached_pattern_count` if it resembles known reusable anatomy

#### E. `GROUP`

Definition:

- a visual grouping of nodes without full layout semantics

Design Ops interpretation:

- often a weaker, more ad hoc structural unit than `FRAME`
- still important, because designers sometimes build reusable-looking structures as groups

Count toward:

- `total_groups`
- `native_candidate_count` if eligible
- `plain_repeated_block_count` if clustered with similar groups

#### F. Non-structural Node Types

Types such as:

- `TEXT`
- `RECTANGLE`
- `ELLIPSE`
- `VECTOR`

Design Ops interpretation:

- these are building blocks inside structures
- should contribute to signatures and anatomy detection
- should not be treated as reusable candidate blocks by themselves

#### G. Eligibility Rules for Native Candidate Analysis

Not every `FRAME` or `GROUP` should be treated as a candidate repeated block.

The analyzer should only include a node in `native_candidate_count` if it satisfies all or most of these rules:

- depth is above a minimum threshold
- has at least `2` meaningful child nodes
- is not obviously a full-page root frame
- is not a pure decorative wrapper
- is not already a `COMPONENT` or `INSTANCE`
- contains at least one semantic structure signal:
  - text + icon
  - label + value
  - title + subtitle
  - header + body
  - leading content + trailing action

#### H. Root-Level Exclusions

The analyzer should exclude root app canvases or top-level screens from native repetition metrics unless explicitly analyzing `page template` patterns.

Examples to exclude by default:

- full mobile screen root
- full tablet screen root
- top-level page canvas

These nodes should still be tracked separately for template-level analysis.

### 11.3 Exact Usage Analysis

The system must calculate:

- total instance count
- total component count
- total component set count
- total frame/group count
- instance usage ratio
- count of cross-file component usage

### 11.4 Heuristic Repetition Analysis

The system must detect repeated non-component patterns by building signatures from:

- child type order
- child naming patterns
- text layer count
- layout direction
- spacing/padding tokens or raw values
- presence of icon + label + value structures
- structure depth
- optional chevron or action region

The output should group likely repeated native structures into clusters.

### 11.5 Possible Detached Pattern Detection

The system should flag nodes that:

- strongly resemble known component patterns
- are plain `FRAME` or `GROUP`
- appear multiple times
- do not use an existing matching `INSTANCE`

This should be labeled as:

- `possible_detached_or_rebuilt_pattern`

The system must not present this as certainty.

### 11.6 Large Component Detection

The system should flag components that exceed configurable thresholds such as:

- child count
- depth of nested layers
- number of text regions
- number of semantic sections
- fixed screen-like dimensions

This helps identify:

- page-like components
- template-level components
- feature-specific mega-components

### 11.7 Candidate Promotion Detection

The system should mark repeated patterns that may deserve promotion when they meet rules like:

- repeated 2+ times
- structurally similar
- semantically stable enough
- not already represented as component instance

Candidate labels:

- `candidate_atomic`
- `candidate_compound`
- `candidate_scaffold`
- `candidate_pattern`

### 11.8 Metrics Export

The system must output machine-readable results as:

- JSON

Optional:

- CSV
- Markdown summary

---

## 12. Non-Functional Requirements

### Performance

- analyze one file in a usable amount of time
- avoid unnecessary repeat calls through caching

### Reliability

- handle temporary Figma API failures
- retry on rate-limited requests using backoff

### Transparency

- every metric should be explainable
- heuristic findings should include confidence or evidence notes

### Maintainability

- clear separation between Figma ingestion, parsing, heuristics, and reporting

---

## 13. User Stories

1. As Design Ops, I want to analyze one MM+ or FS+ file and get a breakdown of component usage so I can reduce manual counting.
2. As Design Ops, I want to see repeated native frames so I can identify UI kit opportunities.
3. As Design Ops, I want to flag large page-like components so I can discourage over-componentization.
4. As Design Ops, I want to compare files across one project so I can spot local rebuilding patterns.
5. As PD Lead, I want summary metrics and candidate recommendations so I can align improvement priorities.
6. As engineer, I want repeated UI patterns identified more clearly so I can discuss shared implementation opportunities.

---

## 14. Proposed Metrics

### 14.1 Core Metrics

- `total_nodes`
- `total_components`
- `total_component_sets`
- `total_instances`
- `total_frames`
- `total_groups`
- `instance_usage_ratio`
- `component_to_frame_ratio`

### 14.2 Design Ops Health Metrics

- `repeated_native_cluster_count`
- `possible_detached_pattern_count`
- `cross_file_component_dependency_count`
- `large_component_count`
- `pattern_candidate_count`
- `ui_kit_adoption_score`

### 14.3 Candidate Metrics

- `top_repeated_plain_patterns`
- `top_rebuilt_card_patterns`
- `top_rebuilt_section_patterns`
- `top_rebuilt_control_patterns`

### 14.4 Optional Derived Scores

- `component_maturity_score`
- `reuse_consistency_score`
- `pattern_fragmentation_score`

These scores should be carefully documented because they are abstracted indicators, not native Figma values.

### 14.5 Metric Definitions Proposal

The metrics below should be explicitly defined in the implementation so the dashboard stays explainable and stable over time.

#### `instance_usage_rate`

Purpose:

- show how much reusable component usage exists relative to all reusable-eligible structures

Proposed formula:

```text
instance_usage_rate = total_instances / (total_instances + native_candidate_count)
```

Where:

- `total_instances` = count of `INSTANCE` nodes in analysis scope
- `native_candidate_count` = count of eligible `FRAME` and `GROUP` nodes that look like reusable structures but are not component instances

Why this denominator:

- using all nodes would make the metric meaningless
- using only reusable-eligible structures makes the rate more relevant to Design Ops

Interpretation:

- high = stronger adoption of reusable instances
- low = more manual/native building behavior

#### `plain_repeated_block_count`

Purpose:

- count how many repeated non-component structure clusters exist in the file

Proposed formula:

```text
plain_repeated_block_count = count(distinct repeated_native_clusters)
```

A repeated native cluster is a set of `FRAME` or `GROUP` nodes that:

- are not `INSTANCE`
- share the same or very similar structural signature
- occur at least `2` times

Interpretation:

- high = many manually repeated structures
- low = fewer repeated non-component patterns

#### `possible_detached_pattern_count`

Purpose:

- estimate how many nodes may represent rebuilt or detached-like structures instead of real component usage

Proposed formula:

```text
possible_detached_pattern_count = count(native nodes matched to known reusable anatomy with confidence >= threshold)
```

Signal inputs may include:

- strong similarity to known component signature
- repeated occurrence
- same semantic role as existing component
- manual frame/group instead of instance

Important note:

- this is heuristic only
- should always be labeled as `possible`

#### `large_component_count`

Purpose:

- count reusable components that are likely too large, too complex, or too page-like for healthy system usage

Proposed formula:

```text
large_component_count = count(components where complexity_score >= large_threshold)
```

Suggested complexity inputs:

- child count
- max depth
- number of text nodes
- number of semantic sections
- fixed large dimensions
- presence of multiple unrelated zones

Suggested MVP thresholds:

- child count > `12`
- or depth > `5`
- or semantic section count > `3`

Interpretation:

- high = many master components are acting like templates or page chunks

#### `cross_file_component_dependency_count`

Purpose:

- show how often a file depends on components defined outside the current file

Proposed formula:

```text
cross_file_component_dependency_count = count(instances whose source file key != active file key)
```

Interpretation:

- high = strong dependency on other files
- may be healthy shared library usage
- may also indicate fragmented ownership if unmanaged

#### `component_vs_native_ratio`

Purpose:

- show relative balance between reusable instance usage and manual reusable-looking structures

Proposed formula:

```text
component_vs_native_ratio = total_instances / max(native_candidate_count, 1)
```

Alternative display:

```text
component_vs_native_ratio_display = "120 : 45"
```

Interpretation:

- above `1.0` = more instance usage than native candidate structures
- below `1.0` = more native candidate structures than instance usage

#### `top_repeated_non_component_patterns`

Purpose:

- surface the most repeated native structures for Design Ops review

Proposed output shape:

```json
[
  {
    "pattern_name": "summary card cluster",
    "occurrence_count": 8,
    "node_type": "FRAME",
    "signature_summary": "title + two stat pairs + footer meta",
    "confidence": "medium",
    "candidate_level": "compound"
  }
]
```

Ranking logic:

- sort by `occurrence_count` descending
- then by `confidence`
- then by structural simplicity or promotion readiness

### 14.6 Supporting Counts

To make the core metrics trustworthy, the analyzer should also expose the raw counts that feed them:

- `total_instances`
- `total_components`
- `total_component_sets`
- `total_frames`
- `total_groups`
- `native_candidate_count`
- `repeated_native_cluster_count`
- `exact_cross_file_instance_count`

### 14.7 Metric Scope Rules

Each analysis run must declare the metric scope:

- `file_scope`
- `selected_node_scope`
- `page_scope`

This matters because the same file can produce very different numbers depending on whether the analyzer looks at:

- the full design file
- one feature page
- one section only

The dashboard should always display scope alongside metric values.

### 14.8 Refactor-Oriented Metrics Proposal

The current raw counts are useful, but they are not yet strong enough to guide refactor decisions by themselves.

To make the analyzer more valuable for Design Ops, Product Designers, and engineers, the dashboard should prioritize `refactor-oriented metrics` that answer:

- what is the cleanup burden?
- what is the standardization opportunity?
- what is likely worth turning into shared component first?
- where is the biggest design-to-code inconsistency risk?

#### `reuse_gap_score`

Purpose:

- show how far a file is from expected reusable-instance adoption

Proposed formula:

```text
reuse_gap_score = 1 - instance_usage_rate
```

Display:

- percentage
- higher means bigger gap

Interpretation:

- `0.00 - 0.20` = healthy
- `0.21 - 0.40` = moderate gap
- `0.41+` = high refactor opportunity

#### `duplication_load_score`

Purpose:

- estimate how much repeated manual structure exists in the file

Proposed formula:

```text
duplication_load_score =
  (
    repeated_native_occurrences
    - repeated_native_cluster_count
  ) / max(native_candidate_count, 1)
```

Where:

- `repeated_native_occurrences` = total number of nodes inside repeated native clusters
- subtracting `cluster_count` removes one baseline copy per cluster

Interpretation:

- high = many duplicate rebuilds beyond the first occurrence
- low = repeated native patterns exist, but duplication burden is still limited

#### `component_fragmentation_index`

Purpose:

- show how fragmented the reusable story is across `instances`, `native rebuilds`, and `local-only structures`

Proposed formula:

```text
component_fragmentation_index =
  (
    native_candidate_count
    + possible_detached_pattern_count
    + cross_file_component_dependency_count * dependency_weight
  ) / max(total_instances + native_candidate_count, 1)
```

Interpretation:

- higher = more fragmented system behavior
- useful for comparing files or projects over time

#### `promotion_opportunity_score`

Purpose:

- rank candidate patterns by how worthwhile they are to promote into project UI kit

Proposed formula per cluster:

```text
promotion_opportunity_score =
  occurrence_weight * normalized_occurrence_count
  + stability_weight * structural_stability_score
  + spread_weight * cross_page_spread_score
  + cost_weight * implementation_savings_score
  - complexity_penalty * pattern_complexity_score
```

Suggested use:

- calculate per repeated cluster
- sort descending
- show only top candidates

This is much more useful than showing all repeated clusters equally.

#### `implementation_alignment_score`

Purpose:

- estimate how cleanly a repeated design pattern could map to shared engineering implementation

Signal inputs:

- structural stability
- slot clarity
- low business-specific content coupling
- low variant explosion
- consistent metric anatomy

Interpretation:

- high = strong candidate for shared code component
- low = probably still local/pattern-level only

#### `template_risk_score`

Purpose:

- highlight when a file relies on giant page-like or section-like master components that may slow reuse

Signal inputs:

- large component count
- average complexity of components
- ratio of large components to total components

Interpretation:

- high = reusable inventory may be too top-heavy

### 14.9 Candidate Quality Filters

The dashboard should not surface every repeated structure as a meaningful promotion candidate.

To avoid noisy outputs like:

- `Repeated Text Pattern`
- `Repeated Content Pattern`
- `Repeated Frame 7045 Pattern`

the analyzer should apply `candidate quality filters`.

#### Exclude or Downgrade These by Default

- pure text-only repetitions
- decorative wrappers
- spacer frames
- frames with one meaningful child only
- pure background/image holders
- generic unnamed wrappers like `Frame 1234` unless semantic evidence exists

#### Candidate Eligibility Rules

A repeated native cluster should only appear in the main `Promotion Candidates` view if it has:

- at least `2` semantic regions
- meaningful text or control anatomy
- low decorative-only ratio
- repeated use count above threshold
- stable structure score above threshold

Otherwise it should stay in:

- `Raw Duplicates`
- or `Low-Value Repetition`

This keeps the main dashboard focused on actionable findings.

### 14.10 Semantic Candidate Naming Proposal

The current repeated-pattern names should not rely only on node names.

Instead, the analyzer should infer a semantic label from anatomy.

Examples:

- `Metric Pair`
- `Entity Summary Card`
- `Section Header with Action`
- `Filter Chip Group`
- `Product Summary Row`
- `Bottom Action Bar`
- `List Item with Chevron`
- `Dialog Header`

Fallback only when semantic inference fails:

- `Unnamed Compound Pattern`
- `Unnamed Scaffold Pattern`

This will make the dashboard much more credible and usable in discussion.

### 14.11 Candidate Level Inference Proposal

The analyzer should not label most repeated patterns as `Atomic` by default.

It should infer candidate level from structure:

#### `candidate_atomic`

Use when:

- single semantic control or display unit
- examples:
  - chip
  - badge
  - icon + label
  - metric pair

#### `candidate_compound`

Use when:

- 2-4 semantic regions
- examples:
  - section header
  - list item with meta
  - product summary card
  - key-value block

#### `candidate_scaffold`

Use when:

- provides structure with open content region or slot-like behavior
- examples:
  - card shell
  - section shell
  - header shell
  - modal shell

#### `candidate_pattern`

Use when:

- feature-level composition of multiple compounds
- examples:
  - dashboard summary strip
  - comparison section
  - activity summary block

This inference should be based on:

- child region count
- open slot behavior
- composition depth
- semantic diversity

### 14.12 Recommended Dashboard Cards

For the main dashboard, replace or complement the current cards with:

- `Reuse Gap`
  - how far the file is from healthy component adoption
- `Duplication Load`
  - how much manual rebuild volume exists
- `Promotion Opportunities`
  - how many strong candidates are worth review
- `Fragmentation Index`
  - how mixed the file is across instance/native/rebuilt behavior
- `Template Risk`
  - whether reusable inventory is too top-heavy
- `Engineering Alignment`
  - how implementation-friendly the top candidates are

These will feel much more strategic than raw counts alone.

---

## 15. Detection Model

### 15.1 Exact Detection

Derived from raw Figma data:

- node type
- instance component link
- component set relationship
- file component mapping

### 15.2 Heuristic Detection

Derived from Design Ops rules:

- structural similarity
- semantic similarity
- proximity to known component anatomy
- repeated local layouts

### 15.3 Confidence System

Each heuristic finding should carry:

- `low`
- `medium`
- `high`

Possible fields:

- `confidence_score`
- `evidence_summary`

---

## 16. Technical Architecture

### 16.1 Suggested Stack

- `Python`
- `FastAPI` for API layer
- `requests` or `httpx` for Figma API calls
- `Pydantic` for schemas
- `SQLite` for local first storage
- optional `PostgreSQL` later
- optional `Redis` for caching later

### 16.2 Architecture Layers

1. `Figma client`
2. `File parser`
3. `Signature builder`
4. `Heuristic analyzer`
5. `Metrics engine`
6. `Persistence layer`
7. `API layer`
8. `Dashboard frontend`

### 16.3 Suggested Folder Structure

```text
src/
  api/
  clients/
  parsers/
  analyzers/
  heuristics/
  metrics/
  models/
  storage/
  reports/
```

---

## 17. API Design

### 17.1 Proposed Internal Endpoints

#### `POST /analyze/file`

Request:

```json
{
  "file_key": "abc123",
  "project": "MM+",
  "platform": "Tablet",
  "label": "MM+ dashboard file"
}
```

Response:

```json
{
  "analysis_id": "analysis_001",
  "status": "completed",
  "summary": {
    "total_instances": 120,
    "instance_usage_ratio": 0.41,
    "repeated_native_cluster_count": 18,
    "possible_detached_pattern_count": 7,
    "large_component_count": 4
  }
}
```

#### `GET /analysis/{analysis_id}`

Returns full analysis details.

#### `GET /analysis/{analysis_id}/clusters`

Returns repeated native pattern clusters.

#### `GET /analysis/{analysis_id}/candidates`

Returns promotion candidates.

#### `GET /projects/{project}/summary`

Returns project-level rollup.

---

## 18. Data Model

### 18.1 Analysis Run

```json
{
  "id": "analysis_001",
  "project": "FS+",
  "platform": "Mobile",
  "file_key": "abc123",
  "file_name": "FS+ Dashboard",
  "created_at": "2026-04-28T10:00:00Z",
  "status": "completed"
}
```

### 18.2 Node Record

```json
{
  "node_id": "123:456",
  "name": "Summary Card",
  "type": "FRAME",
  "parent_id": "111:222",
  "depth": 4,
  "component_id": null,
  "signature_id": "sig_001"
}
```

### 18.3 Pattern Cluster

```json
{
  "cluster_id": "cluster_001",
  "signature_id": "sig_001",
  "occurrence_count": 5,
  "pattern_type": "candidate_compound",
  "confidence": "medium",
  "evidence_summary": "Repeated frame with title, subtitle, metric pair, trailing chevron",
  "node_ids": ["1:1", "1:2", "1:3"]
}
```

### 18.4 Metric Snapshot

```json
{
  "analysis_id": "analysis_001",
  "instance_usage_ratio": 0.41,
  "repeated_native_cluster_count": 18,
  "possible_detached_pattern_count": 7,
  "cross_file_component_dependency_count": 12
}
```

---

## 19. Dashboard Requirements

The dashboard should surface:

### Overview

- file name
- project
- platform
- analysis date
- top health metrics

### Findings

- repeated native patterns
- possible detached patterns
- large components
- cross-file dependency map

### Candidates

- likely UI kit promotion opportunities
- grouped by component level

### Trend View

- adoption over time
- repeated native count over time
- large component count over time

---

## 20. UI and Reporting Output

The product should support at least these outputs:

- raw JSON for machine use
- summary table for Design Ops
- candidate list for PD Lead discussion
- dashboard cards for health overview

Optional later:

- clickable cluster preview list
- screenshot snapshots
- node-link back to Figma URL

---

## 21. Security and Token Handling

The system must:

- store Figma token securely
- never expose token in frontend
- allow token replacement without code rewrite
- avoid writing token to logs

Recommended:

- `.env` for local
- secrets manager for deployed use

---

## 22. Rate Limits and API Strategy

The tool must account for Figma API rate limits.

This means:

- batch work when possible
- cache file responses
- avoid refetching unchanged files unnecessarily
- back off on `429 Too Many Requests`

Recommended strategies:

- local cache keyed by file id and timestamp
- retry with exponential backoff
- queue analysis jobs
- run large analyses asynchronously

---

## 23. Risks

### 23.1 Heuristic False Positives

Two plain structures may look similar but serve different jobs.

Mitigation:

- confidence scoring
- evidence explanation
- manual review step

### 23.2 Heuristic False Negatives

Some repeated patterns may escape detection.

Mitigation:

- iterative tuning of signatures
- allow analyst feedback

### 23.3 Rate Limit Friction

Large analysis jobs may slow down or get blocked temporarily.

Mitigation:

- caching
- backoff
- analysis queue

### 23.4 Token Access Limitation

The tool only sees what the token owner can access.

Mitigation:

- use correct seat and file access
- document analysis scope clearly

---

## 24. Assumptions

- token owner has access to target MAI files
- Pro plan and seat are sufficient for file-level REST API access
- initial implementation is internal only
- Design Ops is okay with heuristic rather than perfect detection

---

## 25. Success Criteria

The MVP is successful if:

- one MM+ or FS+ file can be analyzed from API input to JSON output
- component instance usage can be quantified
- repeated plain/native clusters can be surfaced
- at least some candidate promotion patterns can be identified automatically
- Design Ops finds the results useful enough to reduce manual audit effort

### Phase 2 success:

- multiple files can be compared
- dashboard trends are visible
- promotion candidate discussion becomes easier with evidence

---

## 26. MVP Scope

### In Scope

- single-file analysis
- exact node counts
- repeated plain frame clustering
- possible detached pattern heuristic
- large component heuristic
- JSON output

### Out of Scope for MVP

- full visual similarity matching
- image-based screenshot comparison
- organization-wide analytics
- plugin-based inline Figma annotations

---

## 27. Roadmap

### Phase 1: Local Analyzer

- personal access token
- one file input
- parser and metrics
- JSON report

### Phase 2: Internal API

- FastAPI endpoints
- persistent storage
- project summaries

### Phase 3: Dashboard

- visual dashboard
- trend charts
- candidate review view

### Phase 4: Design Ops Workflow Integration

- link manual findings
- combine with PD and engineer interview evidence
- support governance recommendation output

---

## 28. Integration With Design Ops Workflow

This analyzer should not stand alone. It should feed into:

- manual audit review
- PD interview insight
- engineer workflow insight
- UI kit promotion discussion

The right model is:

- `API analyzer provides evidence`
- `Design Ops provides judgment`

---

## 29. Example Decision Support

The product should support recommendations like:

- `Repeated native summary cards detected across 4 files; candidate for project UI kit compound`
- `Large page-like header component detected; recommend decomposition before promotion`
- `Cross-file dependency high; recommend review of shared ownership`
- `Low instance usage ratio in feature file; likely high native rebuild behavior`

---

## 30. Open Questions

- What threshold defines a large component in MAI context?
- How many repeated occurrences are enough for candidate promotion?
- Should candidate scoring differ for mobile, tablet, and web?
- Should analysis compare against a known UI kit inventory?
- Should local component detection be treated separately from repeated native frame detection?

---

## 31. Recommended Next Step

Build the MVP in Python first with:

- one file analyzer
- exact counts
- repeated plain structure signature clustering
- JSON output

Then validate the output against one manually audited file from `MM+` or `FS+` to tune the heuristics before building the dashboard.
