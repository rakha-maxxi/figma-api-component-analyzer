# MAI Engineer Insight Form

This folder contains a Google Apps Script web form for collecting mobile engineering input from MAI, especially for Design Ops and UI kit decisions.

## Files

- [Code.gs](/Users/mtt/Documents/Codex/2026-04-24/i-m-faced-with-a-huge/gas-mai-engineer-form/Code.gs)
- [Index.html](/Users/mtt/Documents/Codex/2026-04-24/i-m-faced-with-a-huge/gas-mai-engineer-form/Index.html)
- [appsscript.json](/Users/mtt/Documents/Codex/2026-04-24/i-m-faced-with-a-huge/gas-mai-engineer-form/appsscript.json)

## What It Does

- Shows a branded web form for MAI mobile engineer feedback
- Collects answers for Design Ops questions
- Saves the responses into a Google Sheet
- Creates the response sheet automatically if it does not exist

## Setup

1. Create a new Google Apps Script project.
2. Copy the contents of `Code.gs`, `Index.html`, and `appsscript.json` into the project files.
3. In `Code.gs`, replace `SPREADSHEET_ID` with your target Google Sheet ID.
4. Deploy as a web app.

## Spreadsheet Output

Responses are stored in a sheet called `Engineer Responses`.

Columns:

- Timestamp
- Engineer Name
- Team / Role
- Pattern Repeat
- False Consistency
- Hardcoded Shared Candidate
- Large Specific Component Impact
- Preferred Reusable Shape
- Slot Scaffold Feasibility
- Top 3 Standardization Areas
- Extra Notes

## Notes

- The UI is optimized for mobile and desktop.
- The visual direction uses a grounded green palette inspired by Maxxi Tani / agricultural product culture.
