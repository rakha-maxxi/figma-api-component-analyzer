# PRD: MAI Design Audit Tracker

## 1. Overview

This product is a lightweight static web tool built with `HTML`, `CSS`, and `JavaScript` to help Design Ops document, review, and track UI audit findings across MAI Figma files.

The tool is intended to replace scattered manual notes with a more structured, reusable, and searchable audit format.

Primary use case:

- document audits for MAI files such as `MM+`
- map reused components, local-only components, missing components, and inconsistencies
- track extraction opportunities from plain elements into reusable UI kit or design system components
- monitor follow-up status for each finding

This tool should run locally in the browser without backend dependency.

---

## 2. Problem Statement

Current audit documentation is manual and fragmented. Findings are written in freeform notes, which makes it harder to:

- compare one MAI file to another
- keep the audit format consistent
- search previous findings
- track repeated issues across projects
- identify which UI elements should become tokens, atomic components, compound components, or patterns
- communicate findings clearly to PD Lead, Product Designers, and engineers

The current process also makes it harder to distinguish:

- reused component vs local component
- reusable pattern vs one-off layout
- audit finding vs action recommendation

---

## 3. Goals

### Primary Goals

- make MAI audit documentation structured and repeatable
- reduce time needed to write and review audit findings
- help Design Ops identify extraction opportunities faster
- make findings easier to share with PD Lead and Product Designers

### Secondary Goals

- create a simple internal audit archive
- support comparison between `Master/UI Kit`, feature files, and cross-file component usage
- create a reusable format for future streams beyond `MM+`

---

## 4. Non-Goals

- not a Figma plugin
- not a live sync tool with Figma API
- not a design system library manager
- not a task management replacement
- not a visual diff tool

---

## 5. Target Users

### Primary User

- `Design Ops` reviewing MAI files and documenting design system findings

### Secondary Users

- `PD Lead` reviewing summary and priorities
- `Product Designers` checking what to improve in their files
- `Engineers` understanding component readiness and reuse opportunities

---

## 6. Product Scope

The tool should support documenting audits at 3 levels:

1. `File-level audit`
2. `Finding-level detail`
3. `Recommendation and follow-up`

---

## 7. Core User Stories

1. As a Design Ops reviewer, I want to create an audit entry for one Figma file so I can centralize my findings.
2. As a Design Ops reviewer, I want to classify findings by type so I can separate reuse, inconsistency, and extraction opportunities.
3. As a Design Ops reviewer, I want to attach Figma links to each finding so I can jump back to the exact frame or node.
4. As a Design Ops reviewer, I want to label findings by severity and priority so I can focus on the most important improvements first.
5. As a Design Ops reviewer, I want to mark whether a UI element should stay local, become a UI kit component, or become a design system component.
6. As a PD Lead, I want to see a concise summary by file so I can understand the biggest issues quickly.
7. As a Product Designer, I want to filter findings by component type or status so I can focus on my next action.
8. As a Design Ops reviewer, I want to export and import the audit data so I can reuse it without backend support.

---

## 8. Feature Requirements

### 8.1 Audit Dashboard

The homepage should show a list of audits with:

- file name
- stream or platform
- owner / reviewer
- audit date
- total findings
- open findings
- high-priority findings
- current status

Suggested actions:

- `Create New Audit`
- `Open Audit`
- `Edit`
- `Delete`
- `Export JSON`

### 8.2 Audit Detail Page

Each audit record should contain:

- audit title
- stream
- platform
- file name
- figma file link
- reviewer name
- audit date
- short context / summary

Sections inside the detail page:

- overview summary
- findings list
- extraction opportunities
- action recommendations

### 8.3 Findings Management

Each finding should support these fields:

- `title`
- `description`
- `category`
- `sub-category`
- `component level`
- `source type`
- `recommendation`
- `priority`
- `severity`
- `status`
- `figma link`
- `node reference`
- `notes`

#### Finding Category

Examples:

- `local component`
- `cross-file component usage`
- `master/ui kit usage`
- `plain element extraction opportunity`
- `inconsistency`
- `missing reuse`
- `deep clicking/usability issue`
- `legacy pattern`

#### Component Level

Examples:

- `token`
- `atomic`
- `compound`
- `pattern`
- `template`
- `page-level`

#### Recommendation Type

Examples:

- `keep local`
- `extract to ui kit`
- `extract to design system`
- `merge with existing component`
- `refactor nested properties`
- `replace with existing component`
- `no action yet`

### 8.4 Filters and Search

The tool should allow filtering findings by:

- platform
- file
- category
- component level
- recommendation
- status
- priority

The tool should also support keyword search.

### 8.5 Summary Blocks

Each audit should automatically generate summary numbers:

- total findings
- findings by category
- findings by component level
- extraction opportunities count
- inconsistencies count
- items ready for UI kit extraction
- items ready for design system extraction

### 8.6 Figma Link Support

Each finding can include:

- full Figma URL
- optional node ID
- short label for the linked frame

The link should open in a new tab.

### 8.7 Import / Export

Since this tool is static, it should store data in:

- `localStorage` for quick local usage

And support:

- `Export JSON`
- `Import JSON`

Optional future support:

- export summary to `Markdown`
- export findings table to `CSV`

---

## 9. Suggested Information Architecture

### Main Views

1. `Dashboard`
2. `Audit Detail`
3. `Create / Edit Audit`
4. `Create / Edit Finding`

### Navigation

- top header
- left sidebar optional on desktop
- mobile-friendly stacked layout

---

## 10. UX Requirements

### General

- simple and lightweight
- easy to scan
- usable for long-form documentation
- optimized for desktop first
- responsive enough for tablet

### Interaction Principles

- make audit creation fast
- minimize repeated typing
- allow structured note-taking
- allow visual status distinction

### Suggested UI Patterns

- cards for audit list
- table or grouped list for findings
- badge/chip system for categories and status
- collapsible sections for large findings
- sticky action bar for save/export

---

## 11. Data Model

### Audit Object

```json
{
  "id": "audit-mmplus-fa-001",
  "title": "MM+ Aktivitas Promosi FA Audit",
  "stream": "MAI",
  "platform": "Tablet",
  "fileName": "[MM+] Aktivitas Promosi FA",
  "figmaFileUrl": "",
  "reviewer": "Rakha",
  "auditDate": "2026-04-27",
  "summary": "Audit for identifying local components, reused patterns, extraction opportunities, and UI kit alignment.",
  "status": "in_review",
  "findings": []
}
```

### Finding Object

```json
{
  "id": "finding-001",
  "title": "Bottom action bar repeated in multiple flows",
  "description": "The same sticky bottom CTA layout is used 3+ times with different content and action purpose.",
  "category": "plain element extraction opportunity",
  "subCategory": "bottom action bar",
  "componentLevel": "compound",
  "sourceType": "feature file",
  "recommendation": "extract to ui kit",
  "priority": "high",
  "severity": "medium",
  "status": "open",
  "figmaUrl": "",
  "nodeReference": "4793:31212",
  "notes": "Use slots or variants for left/right action combinations."
}
```

---

## 12. Functional Requirements

### Must Have

- create audit
- edit audit
- delete audit
- add findings
- edit findings
- delete findings
- filter findings
- search findings
- summary metrics
- localStorage persistence
- JSON import/export

### Should Have

- duplicate finding
- group findings by category
- collapse/expand detail
- quick status update
- copy Figma link button

### Nice to Have

- markdown export
- CSV export
- dark mode
- reusable preset library for finding categories

---

## 13. Suggested Pages and Components for Implementation

### `index.html`

Should contain:

- app shell
- dashboard section
- audit detail panel
- modal or drawer for forms

### `styles.css`

Should contain:

- design tokens via CSS variables
- layout styles
- card styles
- table/list styles
- chip/badge styles
- form styles
- modal styles
- responsive behavior

### `app.js`

Should handle:

- state management
- localStorage read/write
- render dashboard
- render audit detail
- render findings
- filtering
- search
- create/edit/delete actions
- import/export JSON

---

## 14. Suggested Initial Categories

The default categories shipped in version 1:

- `local component`
- `master/ui kit usage`
- `cross-file dependency`
- `plain element extraction opportunity`
- `missing component reuse`
- `inconsistency`
- `legacy large component`
- `deep clicking issue`
- `nested property issue`
- `documentation gap`

Default component levels:

- `token`
- `atomic`
- `compound`
- `pattern`
- `template`
- `page`

Default statuses:

- `open`
- `reviewed`
- `proposed`
- `in progress`
- `resolved`

Default priorities:

- `low`
- `medium`
- `high`
- `critical`

---

## 15. MVP Success Criteria

The MVP is successful if:

- one full MAI audit can be documented without external notes
- findings can be filtered and reviewed quickly
- audit data persists locally after refresh
- audit data can be exported and re-imported
- the format is usable for future MAI files beyond one MM+ case

---

## 16. Sample Seed Content

The app should optionally preload one sample audit based on:

- `MM+ Aktivitas Promosi FA Audit`

Sample findings may include:

- local-only component usage
- reused component from another file
- plain text pairing extraction opportunity
- bottom sheet reuse opportunity
- tab bar reuse opportunity
- bottom action bar reuse opportunity
- empty/success state extraction opportunity
- dialog extraction opportunity
- table cell inconsistency
- deep clicking problem in log component

---

## 17. Future Enhancements

- audit comparison between files
- component inventory map
- recurring issue heatmap
- relation mapping between `Master`, `UI Kit`, and feature files
- visual tagging for `ready to extract`, `needs alignment`, and `legacy`
- export presentation-ready summary for PD Lead

---

## 18. Delivery Notes For Developer / AI Builder

Build this as a static app using only:

- `HTML`
- `CSS`
- `Vanilla JavaScript`

Constraints:

- no framework required
- no backend required
- no external database required
- all data should work with `localStorage`
- structure code so it is easy to extend later

Expected output files:

- `index.html`
- `styles.css`
- `app.js`

The implementation should prioritize clarity and maintainability over visual complexity.
