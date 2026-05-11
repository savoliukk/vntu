const fs = require("fs");
const path = require("path");

const outDir = __dirname;
const vars = ["A", "B", "C", "D"];

const not = (x) => (x ? 0 : 1);
const and = (...xs) => (xs.every(Boolean) ? 1 : 0);
const or = (...xs) => (xs.some(Boolean) ? 1 : 0);
const xor = (a, b) => ((a ? 1 : 0) ^ (b ? 1 : 0));
const impl = (a, b) => or(not(a), b);
const equiv = (a, b) => (a === b ? 1 : 0);
const nand = (a, b) => not(and(a, b));

function rowsFor(fn) {
  const rows = [];
  for (let i = 0; i < 16; i += 1) {
    const A = (i >> 3) & 1;
    const B = (i >> 2) & 1;
    const C = (i >> 1) & 1;
    const D = i & 1;
    rows.push({ i, A, B, C, D, ...fn(A, B, C, D) });
  }
  return rows;
}

const task7Rows = rowsFor((A, B, C, D) => {
  const implication = impl(A, B);
  const bxord = xor(B, D);
  const right = and(C, bxord);
  const f = equiv(implication, right);
  return { implication, bxord, right, f };
});

const task8Rows = rowsFor((A, B, C, D) => {
  const implication = impl(A, B);
  const sheffer = nand(C, B);
  const equivalence = equiv(implication, sheffer);
  const f = xor(equivalence, D);
  return { implication, sheffer, equivalence, f };
});

function bin(n) {
  return n.toString(2).padStart(4, "0");
}

function ones(pattern) {
  return [...pattern].filter((x) => x === "1").length;
}

function combine(a, b) {
  let diff = 0;
  let result = "";
  for (let i = 0; i < a.length; i += 1) {
    if (a[i] === b[i]) result += a[i];
    else if (a[i] !== "-" && b[i] !== "-") {
      diff += 1;
      result += "-";
    } else return null;
  }
  return diff === 1 ? result : null;
}

function covers(pattern, minterm) {
  const bits = bin(minterm);
  return [...pattern].every((bit, i) => bit === "-" || bit === bits[i]);
}

function quine(minterms) {
  let groups = new Map();
  const initial = minterms.map((m) => ({ pattern: bin(m), terms: [m] }));
  for (const item of initial) {
    const key = ones(item.pattern);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  }

  const stages = [];
  const primeMap = new Map();
  let current = initial;

  while (current.length > 0) {
    const used = new Set();
    const nextMap = new Map();
    const byOnes = new Map();
    for (const item of current) {
      const key = ones(item.pattern.split("-").join(""));
      if (!byOnes.has(key)) byOnes.set(key, []);
      byOnes.get(key).push(item);
    }

    const stageRows = current.map((item) => ({ pattern: item.pattern, terms: item.terms }));
    const keys = [...byOnes.keys()].sort((a, b) => a - b);
    for (const key of keys) {
      const left = byOnes.get(key) || [];
      const right = byOnes.get(key + 1) || [];
      for (const a of left) {
        for (const b of right) {
          const pattern = combine(a.pattern, b.pattern);
          if (pattern) {
            used.add(a.pattern);
            used.add(b.pattern);
            const terms = [...new Set([...a.terms, ...b.terms])].sort((x, y) => x - y);
            if (!nextMap.has(pattern)) nextMap.set(pattern, { pattern, terms });
          }
        }
      }
    }

    for (const item of current) {
      if (!used.has(item.pattern)) primeMap.set(item.pattern, item);
    }
    stages.push(stageRows);
    current = [...nextMap.values()];
  }

  const primes = [...primeMap.values()]
    .map((p) => ({ pattern: p.pattern, terms: minterms.filter((m) => covers(p.pattern, m)) }))
    .sort((a, b) => a.pattern.localeCompare(b.pattern));

  const chart = Object.fromEntries(minterms.map((m) => [
    m,
    primes.filter((p) => covers(p.pattern, m)).map((p) => p.pattern),
  ]));

  const essential = [];
  for (const m of minterms) {
    if (chart[m].length === 1 && !essential.includes(chart[m][0])) essential.push(chart[m][0]);
  }

  const coversAll = (patterns) =>
    minterms.every((m) => patterns.some((pattern) => covers(pattern, m)));

  const remainingPrimes = primes.map((p) => p.pattern);
  const candidates = [];
  for (let mask = 1; mask < (1 << remainingPrimes.length); mask += 1) {
    const patterns = remainingPrimes.filter((_, i) => mask & (1 << i));
    if (coversAll(patterns)) candidates.push(patterns);
  }
  candidates.sort((a, b) =>
    literalCount(a) - literalCount(b)
    || a.length - b.length
    || a.join(",").localeCompare(b.join(",")));

  return { minterms, stages, primes, chart, essential, selected: candidates[0] };
}

function literalCount(patterns) {
  return patterns.reduce((total, pattern) => total + [...pattern].filter((x) => x !== "-").length, 0);
}

function dnfTerm(pattern) {
  const lits = [...pattern].flatMap((bit, i) => {
    if (bit === "-") return [];
    return bit === "1" ? [vars[i]] : [`¬${vars[i]}`];
  });
  return lits.length ? lits.join(" ∧ ") : "1";
}

function cnfClauseFromZero(pattern) {
  const lits = [...pattern].flatMap((bit, i) => {
    if (bit === "-") return [];
    return bit === "1" ? [`¬${vars[i]}`] : [vars[i]];
  });
  return lits.length ? `(${lits.join(" ∨ ")})` : "(0)";
}

function karnaugh(rows) {
  const abOrder = ["00", "01", "11", "10"];
  const cdOrder = ["00", "01", "11", "10"];
  return abOrder.map((ab) =>
    cdOrder.map((cd) => {
      const A = Number(ab[0]);
      const B = Number(ab[1]);
      const C = Number(cd[0]);
      const D = Number(cd[1]);
      return rows.find((r) => r.A === A && r.B === B && r.C === C && r.D === D).f;
    }));
}

const task8Minterms = task8Rows.filter((r) => r.f === 1).map((r) => r.i);
const task8Zeros = task8Rows.filter((r) => r.f === 0).map((r) => r.i);
const task8Dnf = quine(task8Minterms);
const task8Cnf = quine(task8Zeros);

const task9Minterms = [1, 2, 3, 5, 10, 14, 15];
const task9 = quine(task9Minterms);

const results = {
  task7: {
    variant: 14,
    expression: "(A → B) ~ (C ∧ (B ⊕ D))",
    rows: task7Rows,
    vector: task7Rows.map((r) => r.f),
  },
  task8: {
    variant: 1,
    expression: "((A → B) ~ (C | B)) ⊕ D",
    rows: task8Rows,
    vector: task8Rows.map((r) => r.f),
    minterms: task8Minterms,
    zeros: task8Zeros,
    karnaugh: karnaugh(task8Rows),
    minDnfPatterns: task8Dnf.selected,
    minDnf: task8Dnf.selected.map(dnfTerm).join(" ∨ "),
    minCnfPatterns: task8Cnf.selected,
    minCnf: task8Cnf.selected.map(cnfClauseFromZero).join(" ∧ "),
  },
  task9: {
    variant: 2,
    minterms: task9Minterms,
    stages: task9.stages,
    primeImplicants: task9.primes,
    chart: task9.chart,
    essential: task9.essential,
    selected: task9.selected,
    minDnf: task9.selected.map(dnfTerm).join(" ∨ "),
  },
};

const text = [
  "Практична робота 3: контрольні результати",
  "",
  `Задача 7: вектор f = [${results.task7.vector.join(", ")}]`,
  "",
  `Задача 8: мінтерми = (${task8Minterms.join(", ")}), нулі = (${task8Zeros.join(", ")})`,
  `  мінДНФ = ${results.task8.minDnf}`,
  `  мінКНФ = ${results.task8.minCnf}`,
  "",
  `Задача 9: F = (${task9Minterms.join(", ")})`,
  `  істотні імпліканти = ${task9.essential.join(", ")}`,
  `  мінДНФ = ${results.task9.minDnf}`,
  "",
].join("\n");

fs.writeFileSync(
  path.join(outDir, "pr3_tasks7_9_results.json"),
  JSON.stringify(results, null, 2),
  "utf8",
);
fs.writeFileSync(path.join(outDir, "pr3_tasks7_9_results.txt"), text, "utf8");

console.log(text);
