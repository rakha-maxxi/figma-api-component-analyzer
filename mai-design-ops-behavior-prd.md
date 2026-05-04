# PRD: MAI Design Ops Behavior and Component Governance Dashboard

## 1. Overview

This document defines the context, problem space, and product requirements for a lightweight internal dashboard or documentation tool that helps `Design Ops` understand `Product Designer behavior`, `component usage patterns`, and `promotion opportunities` inside `MAI Stream`.

The goal is not only to audit Figma files, but also to understand:

- why designers create local or side components
- when designers reuse existing UI kit or master components
- what slows down adoption of the design system
- what should be promoted from local component into project UI kit
- how Design Ops can support exploration without reducing delivery speed

This can later be implemented as:

- a dashboard
- a structured documentation hub
- an audit + interview tracker
- a local web tool
- a Notion or spreadsheet structure

---

## 2. Background Context

### MAI Stream Reality

MAI has:

- multiple projects and platforms
- many Figma files inside one project
- teams working under MVP and delivery pressure
- mixed component maturity
- local components, native frames, master components, and partial UI kit usage

Product Designers often move quickly and create:

- local components
- large content-specific components
- page-specific layouts
- duplicated structures

This is not necessarily a problem of capability. It is often a workflow adaptation to delivery urgency.

### Design Ops Challenge

Design Ops needs to decide:

- what should stay local
- what should become project UI kit
- what should remain exploratory
- what should be standardized into reusable anatomy

To do this well, Design Ops needs both:

- `file-based findings`
- `behavioral context from Product Designers`

---

## 3. Problem Statement

Current MAI Design Ops understanding is stronger on visual/file audit than on team behavior.

Without capturing designer behavior, there is a risk that:

- Design Ops proposes components that do not match real workflow
- UI kit grows in a way that is theoretically neat but poorly adopted
- local component creation is judged without understanding why it happens
- engineers receive unstable or inconsistent component directions

The missing layer is a clear view of:

- how designers work under time pressure
- when they choose local components
- what they reuse
- what blocks them from using the design system
- what repeated structures would actually help them move faster

---

## 4. Product Goals

### Primary Goals

- document Product Designer behavior related to design system usage
- capture why local components are created
- identify recurring component and pattern needs
- connect behavior findings with component governance decisions
- help Design Ops decide what to promote into UI kit

### Secondary Goals

- create shared understanding across Design Ops, PD Lead, and Product Designers
- support future dashboard/reporting
- reduce subjective decision-making in component promotion
- improve design system adoption through empathy with workflow

---

## 5. Non-Goals

- not a performance review tool
- not a compliance-only scorecard
- not a replacement for Figma file audit
- not a task management board
- not a final design system library itself

---

## 6. Core Design Ops Principles

The dashboard or documentation should reflect these principles:

### 6.1 Decompose First

When a repeated large component appears, Design Ops should first identify:

- stable small parts
- reusable anatomy
- repeated structural patterns

before promoting the full large component into UI kit.

### 6.2 Local First for Exploration

Designers may create:

- native layouts
- side components
- local components

when they are still exploring or solving a feature-specific need.

This is allowed and expected.

### 6.3 Promote When Proven

A local component should be promoted into project UI kit when it shows:

- repeated use across files
- stable structure
- same job or purpose
- clear value for both designer and engineer

### 6.4 Standardize Stable Parts

Design Ops should provide:

- tokens
- atoms
- compounds
- slot/scaffold components

so designers can move quickly without rebuilding the same stable parts every time.

---

## 7. What Design Ops Needs to Learn From PD Behavior

The system should help gather answers to these questions:

- How do Product Designers start a new feature?
- When do they choose existing components?
- When do they create local components?
- What makes existing components hard to use?
- Which patterns are repeatedly rebuilt?
- What kind of scaffold or reusable structure would help them most?
- Where does the current UI kit create friction?
- How does urgency affect their design choices?

---

## 8. User Types

### Primary User

- `Design Ops`

### Secondary Users

- `PD Lead`
- `Product Designers`
- `Engineers` as reference audience for reusable pattern alignment

---

## 9. Main Use Cases

1. Design Ops wants to interview or survey Product Designers about their component usage behavior.
2. Design Ops wants to connect behavior patterns with audit findings from Figma files.
3. Design Ops wants to identify which local patterns should remain local and which should be promoted.
4. PD Lead wants to understand workflow pain points behind inconsistent component usage.
5. Design Ops wants to produce a more realistic UI kit roadmap based on both behavior and file evidence.

---

## 10. Behavioral Questionnaire Scope

The system should support documenting answers in 5 themes.

### 10.1 Workflow Context

Questions:

- What kind of feature or task do you work on most often?
- When starting a new feature, what is your first working step?
- Which part of the design process takes the most time?

### 10.2 Component Usage Behavior

Questions:

- When do you usually use an existing component?
- When do you decide to create a local component?
- What usually stops you from reusing an existing component?
- Do you search for an existing component first or build directly?

### 10.3 Pain Points

Questions:

- What is hardest about using the current UI kit/master?
- Are there components that exist but feel difficult to use?
- What patterns do you often rebuild manually?
- Which components do you wish already existed?

### 10.4 Exploration vs System

Questions:

- When exploring a new layout, what flexibility do you need most?
- What kind of UI kit support would help you move faster?
- Would scaffold or slot-based components help your workflow?

### 10.5 Promotion Opportunity

Questions:

- Are there local components you have reused many times?
- Which local patterns deserve promotion to UI kit?
- Which 3 reusable components or scaffolds would help most right now?

---

## 11. Data Model

### 11.1 Designer Profile

```json
{
  "id": "designer-001",
  "name": "Designer Name",
  "stream": "MAI",
  "project": "FS+",
  "platform": "Mobile",
  "role": "Product Designer"
}
```

### 11.2 Behavior Response

```json
{
  "id": "behavior-001",
  "designerId": "designer-001",
  "project": "FS+",
  "platform": "Mobile",
  "date": "2026-04-28",
  "workflowSummary": "",
  "componentUsageSummary": "",
  "painPoints": [],
  "repeatedPatterns": [],
  "desiredSupport": [],
  "promotionCandidates": [],
  "notes": ""
}
```

### 11.3 Governance Candidate

```json
{
  "id": "candidate-001",
  "name": "Section Header with Action",
  "project": "FS+",
  "level": "compound",
  "source": "local repeated pattern",
  "evidence": [
    "file-a",
    "file-b"
  ],
  "status": "candidate",
  "recommendation": "promote to project ui kit",
  "reason": "Repeated in multiple files with stable anatomy"
}
```

---

## 12. Proposed Information Architecture

The dashboard or system should have these areas:

### 12.1 Overview

Shows:

- total projects audited
- total designer interviews or responses
- top repeated pain points
- top promotion candidates
- top local component reasons

### 12.2 Designer Behavior View

Shows:

- designer name
- project/platform
- workflow summary
- component behavior summary
- key pain points
- preferred support

### 12.3 Pattern Opportunity View

Shows:

- repeated pattern name
- where it appears
- whether it is local, side, or reused
- current maturity
- recommendation

### 12.4 Governance Board

Shows:

- local only
- candidate for promotion
- approved for project UI kit
- legacy
- deprecated

### 12.5 Audit Linkage

Connect behavior data to visual audit findings:

- file finding
- designer context
- recommendation
- owner

---

## 13. Suggested Categories and Fields

### Behavior Categories

- `Reuse First`
- `Build First`
- `Local Component Heavy`
- `UI Kit Assisted`
- `Exploration Heavy`
- `Speed Driven`
- `Pattern Aware`

### Pain Point Categories

- `Component hard to find`
- `Component hard to edit`
- `Component too rigid`
- `Missing reusable structure`
- `Too much local duplication`
- `Naming confusion`
- `Documentation gap`
- `Workflow pressure`

### Promotion Decision Status

- `keep local`
- `candidate`
- `needs discussion`
- `promote to project ui kit`
- `promote to shared system`
- `legacy only`

---

## 14. Product Requirements

### 14.1 Must Have

- capture designer behavior notes
- store answers by project and platform
- capture pain points and repeated patterns
- connect behavior with component recommendations
- identify promotion candidates
- support structured summary view

### 14.2 Should Have

- filter by project, platform, and designer
- search by pattern/component name
- count repeated pain points
- group promotion candidates by level
- show linked file findings

### 14.3 Nice to Have

- export to JSON
- export to Markdown summary
- export to presentation-ready table
- compare projects like `MM+` vs `FS+`

---

## 15. Output Views Design Ops Would Need

### 15.1 For Discussion With PD Lead

Need concise summary:

- top workflow blockers
- repeated local component behavior
- promotion opportunities
- support recommendations

### 15.2 For Discussion With Product Designers

Need practical summary:

- repeated pain points
- reusable scaffolds to build next
- existing components that can help

### 15.3 For Engineering Alignment

Need structured summary:

- repeated UI anatomy
- stable patterns worth shared implementation
- areas still exploratory

---

## 16. Example Recommendations the System Should Support

Examples:

- `Provide section scaffold with token-based spacing variants`
- `Promote text pairing into project UI kit`
- `Keep dashboard hero local, extract stat pair and header shell`
- `Promote filter segmented control into FS+ UI kit`
- `Document local pattern as candidate, not approved component yet`

---

## 17. Success Criteria

This effort is successful if:

- Design Ops can explain not only what is inconsistent, but why it happens
- Product Designers feel the system supports rather than blocks their work
- promotion decisions become clearer and less subjective
- new UI kit proposals are better aligned to real workflow
- repeated local patterns are surfaced more intentionally

---

## 18. Recommended First Implementation

The fastest MVP can be any of these:

- `HTML/CSS/JS local dashboard`
- `Notion database`
- `Google Sheet with linked audit records`
- extension of the existing MAI audit tracker

Recommended sections for MVP:

- designer profile
- behavior questionnaire responses
- repeated patterns
- component pain points
- promotion candidate tracker
- recommendation notes

---

## 19. Suggested Prompt for Building the Dashboard

Use this prompt in another AI or implementation context:

> Build a lightweight internal dashboard for MAI Design Ops that captures Product Designer behavior, component usage patterns, pain points, repeated local components, and promotion candidates for project UI kit. The dashboard should support designer profiles, questionnaire responses, repeated pattern tracking, and a governance board that classifies items as keep local, candidate, needs discussion, promote to project UI kit, or legacy. The goal is to connect file audit findings with real PD workflow so Design Ops can propose more realistic reusable components and scaffolds.

---

## 20. Key Framing Statement

This system exists because design system work is not only about building components.

It is also about understanding:

- how components are born
- why designers avoid or reuse them
- when local patterns deserve promotion
- how to support exploration without losing consistency

That is the Design Ops context this dashboard should preserve.
