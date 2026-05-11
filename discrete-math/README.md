# Discrete Mathematics Calculation Scripts

This directory contains only the calculation scripts for practical works 1-3 in the discrete mathematics course.

## Structure

- `practice-01/solve_pr1_tasks1_3.js` - set operations and Venn diagram expressions.
- `practice-02/solve_pr2_tasks4_6.js` - relations, coverings, and combinatorics.
- `practice-03/solve_pr3_tasks7_9.js` - logical functions, Karnaugh maps, and Quine minimization.

## Run Locally

```sh
npm run build
```

The build script runs all three practical work calculation scripts. Scripts print summaries to stdout and may create local result files, which are ignored by Git.

## Run With Docker

```sh
docker compose run --rm discrete-math
```
