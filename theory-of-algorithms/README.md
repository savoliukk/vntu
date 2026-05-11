# Theory of Algorithms

This directory contains code-based lab artifacts for the Theory of Algorithms course.

## Included labs

- `lab-02` - insertion sort benchmark and report artifacts
- `lab-04` - optimized bubble sort benchmark and report artifacts
- `lab-05` - merge sort benchmark and report artifacts
- `lab-07` - heapsort benchmark and report artifacts
- `lab-08` - counting sort benchmark, report artifacts, and benchmark CSV

Labs `01`, `03`, and `06` are intentionally excluded because their tasks are analytical and do not include a code implementation in the local artifact set.

## Docker

Run all benchmark projects:

```powershell
docker compose run --rm all
```

Run one lab:

```powershell
docker compose run --rm lab-02
docker compose run --rm lab-04
docker compose run --rm lab-05
docker compose run --rm lab-07
docker compose run --rm lab-08
```

The repository keeps the full selected lab archive, including generated `bin` and `obj` folders. Docker builds ignore those generated folders and rebuild projects inside the container.
