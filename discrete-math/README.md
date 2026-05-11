# Discrete Mathematics

This directory contains artifacts for practical works 1-3 in the discrete mathematics course.

## Structure

- `practice-01/` - practical work 1 report and artifacts.
- `practice-02/` - practical work 2 report and artifacts.
- `practice-03/` - practical work 3 report and artifacts.
- `scripts/generate-reports.js` - regenerates the Markdown reports from computed JSON results.

Each practice directory has:

- `report.md` - final report.
- `artifacts/` - source scripts, rendered pages, extracted images, tables, and generated results.

Browser profiles and local cache folders are intentionally excluded.

## Run Locally

```sh
npm run build
```

The build script recomputes practical work results and regenerates reports.

## Run With Docker

```sh
docker compose run --rm discrete-math
```
