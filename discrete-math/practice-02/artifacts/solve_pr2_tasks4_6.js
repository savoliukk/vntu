const fs = require("fs");
const path = require("path");

const outDir = __dirname;

const universe = [1, 2, 3, 4, 5, 6, 7, 8, 9];
const rows = {
  A: { items: [2, 5, 6, 7], cost: 3 },
  B: { items: [2, 8, 9], cost: 1 },
  C: { items: [1, 3, 7], cost: 2 },
  D: { items: [3, 5, 6, 9], cost: 2 },
  E: { items: [1, 3, 4, 8, 9], cost: 3 },
  F: { items: [1, 4, 6], cost: 1 },
  G: { items: [4, 5, 8], cost: 1 },
  H: { items: [3, 7], cost: 1 },
};

const rowNames = Object.keys(rows);

function arrayEq(a, b) {
  return a.length === b.length && a.every((x, i) => x === b[i]);
}

function union(names) {
  return [...new Set(names.flatMap((name) => rows[name].items))].sort((a, b) => a - b);
}

function rowCost(names) {
  return names.reduce((total, name) => total + rows[name].cost, 0);
}

function combinations(items, size, start = 0, prefix = [], result = []) {
  if (prefix.length === size) {
    result.push([...prefix]);
    return result;
  }
  for (let i = start; i <= items.length - (size - prefix.length); i += 1) {
    prefix.push(items[i]);
    combinations(items, size, i + 1, prefix, result);
    prefix.pop();
  }
  return result;
}

function isCover(names) {
  return arrayEq(union(names), universe);
}

function isIrredundant(names) {
  return isCover(names) && names.every((name) => !isCover(names.filter((item) => item !== name)));
}

function allCovers() {
  const covers = [];
  for (let size = 1; size <= rowNames.length; size += 1) {
    for (const combo of combinations(rowNames, size)) {
      if (isCover(combo)) covers.push(combo);
    }
  }
  return covers;
}

const covers = allCovers();
const irredundantCovers = covers.filter(isIrredundant);
const minCost = Math.min(...covers.map(rowCost));
const minCostCovers = covers
  .filter((cover) => rowCost(cover) === minCost)
  .sort((a, b) => a.length - b.length || a.join("").localeCompare(b.join("")));
const minLength = Math.min(...covers.map((cover) => cover.length));
const shortestCovers = covers
  .filter((cover) => cover.length === minLength)
  .sort((a, b) => rowCost(a) - rowCost(b) || a.join("").localeCompare(b.join("")));

const D = [1, 2, 3, 4, 5, 6];
const relation = [];
for (const m of D) {
  for (const n of D) {
    if ((3 * m + 1 - 2 * n) % 2 === 0) relation.push([m, n]);
  }
}
const matrix = D.map((m) => D.map((n) => (((3 * m + 1 - 2 * n) % 2 === 0) ? 1 : 0)));

function hasPair(a, b) {
  return relation.some(([x, y]) => x === a && y === b);
}

function classifyRelation() {
  const reflexive = D.every((x) => hasPair(x, x));
  const irreflexive = D.every((x) => !hasPair(x, x));
  const symmetric = relation.every(([a, b]) => hasPair(b, a));
  const antisymmetric = relation.every(([a, b]) => a === b || !hasPair(b, a));
  const asymmetric = irreflexive && relation.every(([a, b]) => !hasPair(b, a));
  const transitive = relation.every(([a, b]) =>
    relation
      .filter(([x]) => x === b)
      .every(([, c]) => hasPair(a, c)));
  return { reflexive, irreflexive, symmetric, antisymmetric, asymmetric, transitive };
}

const task6 = {
  variant59: {
    allPlacements: 3 ** 9,
    firstCarExactly3: combination(9, 3) * (2 ** 6),
    eachCarExactly3: factorial(9) / (factorial(3) ** 3),
    distribution4_3_2: factorial(9) / (factorial(4) * factorial(3) * factorial(2)) * factorial(3),
  },
  variant33: {
    lettersIntoBoxes: permutation(11, 5),
  },
};

function factorial(n) {
  let result = 1;
  for (let i = 2; i <= n; i += 1) result *= i;
  return result;
}

function combination(n, k) {
  return factorial(n) / (factorial(k) * factorial(n - k));
}

function permutation(n, k) {
  return factorial(n) / factorial(n - k);
}

const results = {
  task4: {
    variant: 9,
    D,
    predicate: "(3m + 1 - 2n) is even",
    simplifiedPredicate: "m is odd",
    relation,
    matrix,
    classification: classifyRelation(),
  },
  task5: {
    variant: 24,
    universe,
    rows,
    irredundantCovers: irredundantCovers.map((cover) => ({
      rows: cover,
      cost: rowCost(cover),
      length: cover.length,
    })),
    minCost,
    minCostCovers: minCostCovers.map((cover) => ({ rows: cover, cost: rowCost(cover), length: cover.length })),
    minLength,
    shortestCovers: shortestCovers.map((cover) => ({ rows: cover, cost: rowCost(cover), length: cover.length })),
  },
  task6,
};

const graphLines = ["graph LR"];
for (const x of D) graphLines.push(`  v${x}(("${x}"))`);
for (const [m, n] of relation) graphLines.push(`  v${m} --> v${n}`);
fs.writeFileSync(path.join(outDir, "task4_relation_graph.mmd"), graphLines.join("\n") + "\n", "utf8");

const text = [
  "Практична робота 2: контрольні результати",
  "",
  `Задача 4: |R| = ${relation.length}, предикат еквівалентний умові m непарне.`,
  `Класифікація: ${JSON.stringify(results.task4.classification)}`,
  "",
  `Задача 5: мінімальна ціна = ${minCost}, покриття: ${minCostCovers.map((c) => c.join("")).join(", ")}`,
  `Найкоротша довжина = ${minLength}, покриття: ${shortestCovers.map((c) => c.join("")).join(", ")}`,
  "",
  `Задача 6, варіант 59: ${JSON.stringify(task6.variant59)}`,
  `Задача 6, варіант 33: ${JSON.stringify(task6.variant33)}`,
  "",
].join("\n");

fs.writeFileSync(
  path.join(outDir, "pr2_tasks4_6_results.json"),
  JSON.stringify(results, null, 2),
  "utf8",
);
fs.writeFileSync(path.join(outDir, "pr2_tasks4_6_results.txt"), text, "utf8");

console.log(text);
