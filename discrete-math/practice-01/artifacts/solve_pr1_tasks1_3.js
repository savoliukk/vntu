const fs = require("fs");
const path = require("path");

const outDir = __dirname;

const set = (items) => new Set(items);
const sorted = (s) => [...s].sort((a, b) => a - b);
const union = (...sets) => set(sets.flatMap((s) => [...s]));
const intersect = (a, b) => set([...a].filter((x) => b.has(x)));
const diff = (a, b) => set([...a].filter((x) => !b.has(x)));
const comp = (u, a) => diff(u, a);

function fmt(items) {
  return `{${items.join(", ")}}`;
}

const task1 = {};
task1.U = set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]);
task1.A = set([1, 2, 3, 4, 7, 9]);
task1.B = set([3, 4, 5, 6, 11, 12, 13]);
task1.C = set([2, 3, 4, 7, 8, 12, 13, 14]);
task1.D = set([1, 7, 14]);
task1.aUnionB = union(task1.A, task1.B);
task1.notC = comp(task1.U, task1.C);
task1.notD = comp(task1.U, task1.D);
task1.notCAndNotD = intersect(task1.notC, task1.notD);
task1.result = union(task1.aUnionB, task1.notCAndNotD);

const task2 = {};
task2.U = set([1, 2, 3, 4, 5, 6, 7, 8, 9]);
task2.A = set([1, 2, 3, 4, 5, 9]);
task2.B = set([2, 4, 6, 8]);
task2.C = set([1, 3, 5, 7]);
task2.D = set([1, 4, 5, 7, 8, 9]);
task2.target = set([1, 2, 4, 5, 6, 7, 8, 9]);
task2.bUnionD = union(task2.B, task2.D);
task2.aMinusC = diff(task2.A, task2.C);
task2.result = union(task2.bUnionD, task2.aMinusC);

const results = {
  task1: {
    variant: 29,
    expression: "(A ∪ B) ∪ (C̄ ∩ D̄)",
    U: sorted(task1.U),
    A: sorted(task1.A),
    B: sorted(task1.B),
    C: sorted(task1.C),
    D: sorted(task1.D),
    aUnionB: sorted(task1.aUnionB),
    notC: sorted(task1.notC),
    notD: sorted(task1.notD),
    notCAndNotD: sorted(task1.notCAndNotD),
    result: sorted(task1.result),
  },
  task2: {
    variant: 19,
    target: sorted(task2.target),
    expression: "(B ∪ D) ∪ (A \\ C)",
    bUnionD: sorted(task2.bUnionD),
    aMinusC: sorted(task2.aMinusC),
    result: sorted(task2.result),
    matchesTarget:
      sorted(task2.result).join(",") === sorted(task2.target).join(","),
  },
  task3: {
    variants: [43, 6],
    diagrams: [
      {
        variant: 43,
        image: "venn_variant43.jpg",
        expression: "C ∪ (A ∩ B)",
      },
      {
        variant: 6,
        image: "venn_variant6.jpg",
        expression: "A ∩ B ∩ C ∩ D",
      },
    ],
  },
};

const text = [
  "Практична робота 1: контрольні результати",
  "",
  `Задача 1: X = ${fmt(results.task1.result)}`,
  `  A ∪ B = ${fmt(results.task1.aUnionB)}`,
  `  C̄ = ${fmt(results.task1.notC)}`,
  `  D̄ = ${fmt(results.task1.notD)}`,
  `  C̄ ∩ D̄ = ${fmt(results.task1.notCAndNotD)}`,
  "",
  `Задача 2: M = ${fmt(results.task2.result)}`,
  `  Цільова множина = ${fmt(results.task2.target)}`,
  `  Збіг із цільовою множиною: ${results.task2.matchesTarget ? "так" : "ні"}`,
  "",
  "Задача 3:",
  "  Варіант 43: E = C ∪ (A ∩ B)",
  "  Варіант 6: E = A ∩ B ∩ C ∩ D",
  "",
].join("\n");

fs.writeFileSync(
  path.join(outDir, "pr1_tasks1_3_results.json"),
  JSON.stringify(results, null, 2),
  "utf8",
);
fs.writeFileSync(path.join(outDir, "pr1_tasks1_3_results.txt"), text, "utf8");

console.log(text);
