# MAI Component Analyzer

This is a dependency-free Python app that:

- fetches a Figma file using a personal access token
- analyzes component usage and oversized components
- detects exact component instance source from Figma instance metadata
- detects repeated native structures
- generates short refactor recommendations
- serves a small dashboard and JSON API

## Run

```bash
python3 -m component_analyzer.server
```

Open:

- `http://127.0.0.1:8123`

## Analyze a real Figma file

Use the dashboard form and provide:

- Figma file key
- project name
- platform

If a local `.env` file contains `FIGMA_TOKEN`, you can leave the token field empty in the dashboard.

The normal fast path analyzes only the target file. It reads `INSTANCE.componentId`
and the file response `components` map to classify component source usage as
local, remote/library, published/remote-like, or unknown.

Use `Deep compare reference file key` only when you explicitly want slower
heuristic matching against another full Figma file, such as a master UI kit file.

You can also export a token before starting:

```bash
export FIGMA_TOKEN=your_token_here
python3 -m component_analyzer.server
```

## Demo mode

Use file key:

- `demo`

This loads a local Figma-like payload so you can verify the app without hitting the Figma API.

## API

### `POST /api/analyze`

```json
{
  "token": "figd_xxx",
  "file_key": "demo",
  "project_name": "FS+",
  "platform": "Mobile"
}
```

Optional deep compare:

```json
{
  "file_key": "demo",
  "reference_file_key": "demo-master",
  "enable_reference_compare": true,
  "project_name": "FS+",
  "platform": "Mobile"
}
```

### `GET /api/analyses`

Lists recent saved analyses.

### `GET /api/analyses/{id}`

Returns a full analysis result.
