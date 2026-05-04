# MAI Design Ops Toolkit

A collection of Design Ops tools for **MAI Stream** — built to audit, analyze, and improve design system health across projects like **MM+**, **FS+**, and **Maxi Rewards**.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Analyzer](#running-the-analyzer)
- [Demo Mode](#demo-mode)
- [Analyzing a Real Figma File](#analyzing-a-real-figma-file)
- [Dashboard Features](#dashboard-features)
- [API Reference](#api-reference)
- [Folder Structure](#folder-structure)
- [Environment Variables](#environment-variables)
- [PRD Documents](#prd-documents)

---

## Overview

The main tool in this repository is the **Figma Component Refactor Analyzer** — a zero-dependency Python application that:

- Fetches Figma file JSON via the REST API using a personal access token
- Parses and classifies every node (COMPONENT, INSTANCE, FRAME, GROUP, TEXT, etc.)
- Detects component instance source (local, remote/library, published, unknown)
- Identifies repeated native structures that could become reusable components
- Flags oversized or page-like components that need decomposition
- Generates refactor recommendations with priority and confidence scoring
- Serves a built-in dashboard and JSON API — no external dependencies required

---

## Prerequisites

- **Python 3.10+** (no pip packages needed — fully dependency-free)
- **Figma Pro** account with a personal access token (for live file analysis)

---

## Installation

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd i-m-faced-with-a-huge
   ```

2. **Create your `.env` file** (optional but recommended)

   ```bash
   cp .env.example .env
   ```

   Then add your Figma token:

   ```
   FIGMA_TOKEN=figd_your_token_here
   ```

   > The `.env` file is gitignored. Your token stays local and is never exposed to the frontend.

That's it — no `pip install`, no `npm install`, no build step.

---

## Running the Analyzer

```bash
python3 -m component_analyzer.server
```

The server starts at:

```
http://127.0.0.1:8123
```

To use a custom port:

```bash
python3 -c "from component_analyzer.server import run; run(port=9000)"
```

To pass the token inline (instead of `.env`):

```bash
export FIGMA_TOKEN=figd_your_token_here
python3 -m component_analyzer.server
```

---

## Demo Mode

You can test the full analyzer flow without a Figma token:

1. Open `http://127.0.0.1:8123`
2. Click **Load Demo** — or use file key `demo` in the analyze form

This loads a built-in Figma-like payload (`demo_data.py`) so you can verify the dashboard, metrics, filtering, and recommendations locally.

---

## Analyzing a Real Figma File

1. Open the dashboard at `http://127.0.0.1:8123`
2. Click **Analyze File**
3. Fill in:
   - **Figma file key** — from the URL: `figma.com/design/<FILE_KEY>/...`
   - **Project name** — e.g. `MM+`, `FS+`
   - **Platform** — e.g. `Mobile`, `Tablet`, `Web`
   - **Token** — leave empty if `FIGMA_TOKEN` is in `.env`
4. Click **Start Analysis**

### Optional: Deep Compare

If you want to check whether native patterns match components in a master/UI kit file:

1. Enter the **reference file key** (e.g. your master UI kit)
2. Check **Enable deep compare against reference file**

> ⚠️ Deep compare fetches a second full file — it is slower and uses more API quota.

---

## Dashboard Features

### Evidence Metrics
Top-level cards showing component adoption rate, large component count, repeated native clusters, and refactor candidates.

### Focus Dropdown
A dropdown filter in the analysis header that lets you narrow all findings to a specific metric area:

| Focus Option | What It Shows |
|---|---|
| **All Findings** | Everything (default) |
| **Text Pairing** | Metric pairs, label + value, list items — text-based patterns |
| **Component / Native Frame Candidates** | Native structures that could become components |
| **Scaffold & Shell Patterns** | Section shells, dialog shells, card-level scaffolds |
| **Large Components** | Oversized, section-like, or page-like components |
| **Existing Component Not Reused** | Known components that are rebuilt manually |
| **Repeated Native Patterns** | All repeated native clusters |

### Tabs

| Tab | Purpose |
|---|---|
| **Snapshot** | Quick overview: top recommendations + component source usage |
| **Findings: Large Components** | Components too big to reuse safely — with complexity breakdown |
| **Findings: Reuse Gaps** | Promotion-ready candidates, existing not reused, raw duplicates, low value |
| **Action Plan** | Prioritized recommendation list: what to refactor, promote, or fix |

### Sidebar
Recent analysis runs with quick-switch — click any run to reload its results instantly.

---

## API Reference

### `POST /api/analyze`

Start a new analysis.

```json
{
  "token": "figd_xxx",
  "file_key": "abc123",
  "project_name": "MM+",
  "platform": "Tablet"
}
```

With deep compare:

```json
{
  "file_key": "abc123",
  "reference_file_key": "master_file_key",
  "enable_reference_compare": true,
  "project_name": "MM+",
  "platform": "Tablet"
}
```

### `GET /api/analyses`

List all saved analysis runs.

### `GET /api/analyses/{id}`

Get full analysis result by ID.

### `GET /api/health`

Health check — returns `{"ok": true}`.

---

## Folder Structure

```
i-m-faced-with-a-huge/
│
├── .env                          # Figma token (gitignored)
├── .gitignore
├── README.md                     # ← You are here
│
├── component_analyzer/           # Main analyzer application
│   ├── __init__.py               # Package marker
│   ├── server.py                 # HTTP server — routes, static files, API handlers
│   ├── analyzer.py               # Core analysis engine — parsing, heuristics, metrics
│   ├── figma_client.py           # Figma REST API client — fetch file JSON
│   ├── demo_data.py              # Built-in demo payload for offline testing
│   ├── storage.py                # Simple JSON file persistence layer
│   ├── README.md                 # Module-level documentation
│   │
│   ├── static/                   # Frontend dashboard (served at /)
│   │   ├── index.html            # Dashboard HTML — layout, dialog, tabs
│   │   ├── styles.css            # Full CSS — design tokens, responsive, components
│   │   └── app.js                # Dashboard JS — rendering, filtering, API calls
│   │
│   └── data/                     # Runtime storage (gitignored)
│       └── analyses.json         # Persisted analysis results
│
├── gas-mai-engineer-form/        # Google Apps Script — MAI interview forms
│   ├── Code.gs                   # Main GAS entry point
│   ├── CreateMaiEngineerForm.gs  # Engineer interview form builder
│   ├── CreateMaiPdForm.gs        # Product Designer interview form builder
│   ├── Index.html                # Form UI template
│   ├── appsscript.json           # GAS project manifest
│   └── README.md                 # GAS module documentation
│
├── figma-component-usage-analyzer-prd.md    # Full PRD — analyzer requirements & metrics
├── figma-component-refactor-analyzer-prd.md # Refactor-focused PRD extension
├── mai-design-ops-behavior-prd.md           # Design Ops behavioral analysis PRD
└── mai-design-ops-handoff.md                # Design-to-engineering handoff guide
```

### Key Modules Explained

| File | Role |
|---|---|
| `analyzer.py` | The brain — walks the Figma node tree, builds signatures, clusters repeated patterns, scores promotion candidates, assesses component complexity, and generates recommendations |
| `server.py` | Lightweight HTTP server (stdlib only) — serves the dashboard, handles `/api/analyze` POST and analysis CRUD endpoints, loads `.env` |
| `figma_client.py` | Thin wrapper around `requests`-free `urllib` to call the Figma REST API with token auth and error handling |
| `demo_data.py` | Returns a realistic Figma-like JSON tree so you can test locally without API access |
| `storage.py` | Reads/writes `data/analyses.json` — simple append-and-list persistence |
| `app.js` | Dashboard rendering — metrics cards, recommendation strips, candidate lists, tab navigation, focus dropdown filtering |
| `styles.css` | Full design system — IBM Plex Sans, green/amber/red semantic tones, responsive grid, glassmorphic tabs |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `FIGMA_TOKEN` | Optional | Figma personal access token. Set in `.env` or export in shell. If not set, you must provide it in the dashboard form. |

---

## PRD Documents

These markdown files document the product requirements and Design Ops strategy:

| Document | Description |
|---|---|
| `figma-component-usage-analyzer-prd.md` | Complete PRD — goals, metrics definitions, heuristic formulas, API design, data model, dashboard requirements |
| `figma-component-refactor-analyzer-prd.md` | Refactor intelligence extension — candidate scoring, promotion opportunity, implementation alignment |
| `mai-design-ops-behavior-prd.md` | Behavioral analysis — designer patterns, interview frameworks, governance workflow |
| `mai-design-ops-handoff.md` | Design-to-engineering handoff — token usage, component mapping, QA checklist |

---

## License

Internal MAI Stream tool — not for public distribution.
