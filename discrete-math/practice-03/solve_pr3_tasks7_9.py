from __future__ import annotations

import json
import os
from pathlib import Path


OUT_DIR = Path(os.path.relpath(Path(__file__).parent, Path.cwd()))
VARS = ["A", "B", "C", "D"]


def logical_not(x: int) -> int:
    return 0 if x else 1


def logical_and(*xs: int) -> int:
    return 1 if all(xs) else 0


def logical_or(*xs: int) -> int:
    return 1 if any(xs) else 0


def xor(a: int, b: int) -> int:
    return int(bool(a)) ^ int(bool(b))


def impl(a: int, b: int) -> int:
    return logical_or(logical_not(a), b)


def equiv(a: int, b: int) -> int:
    return 1 if a == b else 0


def nand(a: int, b: int) -> int:
    return logical_not(logical_and(a, b))


def rows_for(fn):
    rows = []
    for i in range(16):
        a = (i >> 3) & 1
        b = (i >> 2) & 1
        c = (i >> 1) & 1
        d = i & 1
        rows.append({"i": i, "A": a, "B": b, "C": c, "D": d, **fn(a, b, c, d)})
    return rows


def bin4(n: int) -> str:
    return format(n, "04b")


def ones(pattern: str) -> int:
    return pattern.count("1")


def combine(a: str, b: str) -> str | None:
    diff = 0
    result = ""
    for left, right in zip(a, b):
        if left == right:
            result += left
        elif left != "-" and right != "-":
            diff += 1
            result += "-"
        else:
            return None
    return result if diff == 1 else None


def covers(pattern: str, minterm: int) -> bool:
    bits = bin4(minterm)
    return all(bit == "-" or bit == bits[index] for index, bit in enumerate(pattern))


def literal_count(patterns: list[str]) -> int:
    return sum(sum(1 for bit in pattern if bit != "-") for pattern in patterns)


def quine(minterms: list[int]) -> dict[str, object]:
    initial = [{"pattern": bin4(m), "terms": [m]} for m in minterms]
    stages = []
    prime_map: dict[str, dict[str, object]] = {}
    current = initial

    while current:
        used: set[str] = set()
        next_map: dict[str, dict[str, object]] = {}
        by_ones: dict[int, list[dict[str, object]]] = {}
        for item in current:
            key = ones(str(item["pattern"]).replace("-", ""))
            by_ones.setdefault(key, []).append(item)

        stage_rows = [{"pattern": item["pattern"], "terms": item["terms"]} for item in current]
        for key in sorted(by_ones):
            for left in by_ones.get(key, []):
                for right in by_ones.get(key + 1, []):
                    pattern = combine(str(left["pattern"]), str(right["pattern"]))
                    if pattern:
                        used.add(str(left["pattern"]))
                        used.add(str(right["pattern"]))
                        terms = sorted(set(left["terms"]) | set(right["terms"]))
                        next_map.setdefault(pattern, {"pattern": pattern, "terms": terms})

        for item in current:
            if item["pattern"] not in used:
                prime_map[str(item["pattern"])] = item
        stages.append(stage_rows)
        current = list(next_map.values())

    primes = sorted(
        [
            {"pattern": pattern, "terms": [m for m in minterms if covers(pattern, m)]}
            for pattern in prime_map
        ],
        key=lambda item: str(item["pattern"]),
    )

    chart = {
        m: [str(prime["pattern"]) for prime in primes if covers(str(prime["pattern"]), m)]
        for m in minterms
    }

    essential: list[str] = []
    for m in minterms:
        if len(chart[m]) == 1 and chart[m][0] not in essential:
            essential.append(chart[m][0])

    remaining_primes = [str(prime["pattern"]) for prime in primes]

    def covers_all(patterns: list[str]) -> bool:
        return all(any(covers(pattern, m) for pattern in patterns) for m in minterms)

    candidates: list[list[str]] = []
    for mask in range(1, 1 << len(remaining_primes)):
        patterns = [
            pattern
            for index, pattern in enumerate(remaining_primes)
            if mask & (1 << index)
        ]
        if covers_all(patterns):
            candidates.append(patterns)
    candidates.sort(key=lambda items: (literal_count(items), len(items), ",".join(items)))

    return {
        "minterms": minterms,
        "stages": stages,
        "primes": primes,
        "chart": chart,
        "essential": essential,
        "selected": candidates[0],
    }


def dnf_term(pattern: str) -> str:
    literals = [
        VARS[index] if bit == "1" else f"¬{VARS[index]}"
        for index, bit in enumerate(pattern)
        if bit != "-"
    ]
    return " ∧ ".join(literals) if literals else "1"


def cnf_clause_from_zero(pattern: str) -> str:
    literals = [
        f"¬{VARS[index]}" if bit == "1" else VARS[index]
        for index, bit in enumerate(pattern)
        if bit != "-"
    ]
    return f"({' ∨ '.join(literals)})" if literals else "(0)"


def karnaugh(rows: list[dict[str, int]]) -> list[list[int]]:
    ab_order = ["00", "01", "11", "10"]
    cd_order = ["00", "01", "11", "10"]
    result = []
    for ab in ab_order:
        row = []
        for cd in cd_order:
            a, b = int(ab[0]), int(ab[1])
            c, d = int(cd[0]), int(cd[1])
            row.append(
                next(
                    item["f"]
                    for item in rows
                    if item["A"] == a and item["B"] == b and item["C"] == c and item["D"] == d
                )
            )
        result.append(row)
    return result


def main() -> None:
    task7_rows = rows_for(
        lambda a, b, c, d: {
            "implication": impl(a, b),
            "bxord": xor(b, d),
            "right": logical_and(c, xor(b, d)),
            "f": equiv(impl(a, b), logical_and(c, xor(b, d))),
        }
    )
    task8_rows = rows_for(
        lambda a, b, c, d: {
            "implication": impl(a, b),
            "sheffer": nand(c, b),
            "equivalence": equiv(impl(a, b), nand(c, b)),
            "f": xor(equiv(impl(a, b), nand(c, b)), d),
        }
    )

    task8_minterms = [row["i"] for row in task8_rows if row["f"] == 1]
    task8_zeros = [row["i"] for row in task8_rows if row["f"] == 0]
    task8_dnf = quine(task8_minterms)
    task8_cnf = quine(task8_zeros)
    task9_minterms = [1, 2, 3, 5, 10, 14, 15]
    task9 = quine(task9_minterms)

    results = {
        "task7": {
            "variant": 14,
            "expression": "(A → B) ~ (C ∧ (B ⊕ D))",
            "rows": task7_rows,
            "vector": [row["f"] for row in task7_rows],
        },
        "task8": {
            "variant": 1,
            "expression": "((A → B) ~ (C | B)) ⊕ D",
            "rows": task8_rows,
            "vector": [row["f"] for row in task8_rows],
            "minterms": task8_minterms,
            "zeros": task8_zeros,
            "karnaugh": karnaugh(task8_rows),
            "minDnfPatterns": task8_dnf["selected"],
            "minDnf": " ∨ ".join(dnf_term(pattern) for pattern in task8_dnf["selected"]),
            "minCnfPatterns": task8_cnf["selected"],
            "minCnf": " ∧ ".join(cnf_clause_from_zero(pattern) for pattern in task8_cnf["selected"]),
        },
        "task9": {
            "variant": 2,
            "minterms": task9_minterms,
            "stages": task9["stages"],
            "primeImplicants": task9["primes"],
            "chart": task9["chart"],
            "essential": task9["essential"],
            "selected": task9["selected"],
            "minDnf": " ∨ ".join(dnf_term(pattern) for pattern in task9["selected"]),
        },
    }

    text = "\n".join(
        [
            "Практична робота 3: контрольні результати",
            "",
            f"Задача 7: вектор f = [{', '.join(map(str, results['task7']['vector']))}]",
            "",
            f"Задача 8: мінтерми = ({', '.join(map(str, task8_minterms))}), нулі = ({', '.join(map(str, task8_zeros))})",
            f"  мінДНФ = {results['task8']['minDnf']}",
            f"  мінКНФ = {results['task8']['minCnf']}",
            "",
            f"Задача 9: F = ({', '.join(map(str, task9_minterms))})",
            f"  істотні імпліканти = {', '.join(task9['essential'])}",
            f"  мінДНФ = {results['task9']['minDnf']}",
            "",
        ]
    )

    (OUT_DIR / "pr3_tasks7_9_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "pr3_tasks7_9_results.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
