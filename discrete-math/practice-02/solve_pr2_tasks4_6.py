from __future__ import annotations

import itertools
import json
import math
import os
from pathlib import Path


OUT_DIR = Path(os.path.relpath(Path(__file__).parent, Path.cwd()))


UNIVERSE = list(range(1, 10))
ROWS = {
    "A": {"items": [2, 5, 6, 7], "cost": 3},
    "B": {"items": [2, 8, 9], "cost": 1},
    "C": {"items": [1, 3, 7], "cost": 2},
    "D": {"items": [3, 5, 6, 9], "cost": 2},
    "E": {"items": [1, 3, 4, 8, 9], "cost": 3},
    "F": {"items": [1, 4, 6], "cost": 1},
    "G": {"items": [4, 5, 8], "cost": 1},
    "H": {"items": [3, 7], "cost": 1},
}
ROW_NAMES = list(ROWS)
D = list(range(1, 7))


def union(names: list[str] | tuple[str, ...]) -> list[int]:
    values = set()
    for name in names:
        values.update(ROWS[name]["items"])
    return sorted(values)


def row_cost(names: list[str] | tuple[str, ...]) -> int:
    return sum(int(ROWS[name]["cost"]) for name in names)


def is_cover(names: list[str] | tuple[str, ...]) -> bool:
    return union(names) == UNIVERSE


def is_irredundant(names: tuple[str, ...]) -> bool:
    return is_cover(names) and all(
        not is_cover(tuple(item for item in names if item != name))
        for name in names
    )


def relation_pairs() -> list[list[int]]:
    return [
        [m, n]
        for m in D
        for n in D
        if (3 * m + 1 - 2 * n) % 2 == 0
    ]


def has_pair(relation: list[list[int]], a: int, b: int) -> bool:
    return any(x == a and y == b for x, y in relation)


def classify_relation(relation: list[list[int]]) -> dict[str, bool]:
    reflexive = all(has_pair(relation, x, x) for x in D)
    irreflexive = all(not has_pair(relation, x, x) for x in D)
    symmetric = all(has_pair(relation, b, a) for a, b in relation)
    antisymmetric = all(a == b or not has_pair(relation, b, a) for a, b in relation)
    asymmetric = irreflexive and all(not has_pair(relation, b, a) for a, b in relation)
    transitive = all(
        all(has_pair(relation, a, c) for x, c in relation if x == b)
        for a, b in relation
    )
    return {
        "reflexive": reflexive,
        "irreflexive": irreflexive,
        "symmetric": symmetric,
        "antisymmetric": antisymmetric,
        "asymmetric": asymmetric,
        "transitive": transitive,
    }


def main() -> None:
    covers: list[tuple[str, ...]] = []
    for size in range(1, len(ROW_NAMES) + 1):
        for combo in itertools.combinations(ROW_NAMES, size):
            if is_cover(combo):
                covers.append(combo)

    irredundant_covers = [cover for cover in covers if is_irredundant(cover)]
    min_cost = min(row_cost(cover) for cover in covers)
    min_cost_covers = sorted(
        [cover for cover in covers if row_cost(cover) == min_cost],
        key=lambda cover: (len(cover), "".join(cover)),
    )
    min_length = min(len(cover) for cover in covers)
    shortest_covers = sorted(
        [cover for cover in covers if len(cover) == min_length],
        key=lambda cover: (row_cost(cover), "".join(cover)),
    )

    relation = relation_pairs()
    matrix = [
        [1 if (3 * m + 1 - 2 * n) % 2 == 0 else 0 for n in D]
        for m in D
    ]
    classification = classify_relation(relation)

    task6 = {
        "variant59": {
            "allPlacements": 3**9,
            "firstCarExactly3": math.comb(9, 3) * (2**6),
            "eachCarExactly3": math.factorial(9) // (math.factorial(3) ** 3),
            "distribution4_3_2": math.factorial(9)
            // (math.factorial(4) * math.factorial(3) * math.factorial(2))
            * math.factorial(3),
        },
        "variant33": {
            "lettersIntoBoxes": math.factorial(11) // math.factorial(11 - 5),
        },
    }

    results = {
        "task4": {
            "variant": 9,
            "D": D,
            "predicate": "(3m + 1 - 2n) is even",
            "simplifiedPredicate": "m is odd",
            "relation": relation,
            "matrix": matrix,
            "classification": classification,
        },
        "task5": {
            "variant": 24,
            "universe": UNIVERSE,
            "rows": ROWS,
            "irredundantCovers": [
                {"rows": list(cover), "cost": row_cost(cover), "length": len(cover)}
                for cover in irredundant_covers
            ],
            "minCost": min_cost,
            "minCostCovers": [
                {"rows": list(cover), "cost": row_cost(cover), "length": len(cover)}
                for cover in min_cost_covers
            ],
            "minLength": min_length,
            "shortestCovers": [
                {"rows": list(cover), "cost": row_cost(cover), "length": len(cover)}
                for cover in shortest_covers
            ],
        },
        "task6": task6,
    }

    text = "\n".join(
        [
            "Практична робота 2: контрольні результати",
            "",
            f"Задача 4: |R| = {len(relation)}, предикат еквівалентний умові m непарне.",
            f"Класифікація: {json.dumps(classification, ensure_ascii=False, separators=(',', ':'))}",
            "",
            f"Задача 5: мінімальна ціна = {min_cost}, покриття: {', '.join(''.join(c) for c in min_cost_covers)}",
            f"Найкоротша довжина = {min_length}, покриття: {', '.join(''.join(c) for c in shortest_covers)}",
            "",
            f"Задача 6, варіант 59: {json.dumps(task6['variant59'], ensure_ascii=False, separators=(',', ':'))}",
            f"Задача 6, варіант 33: {json.dumps(task6['variant33'], ensure_ascii=False, separators=(',', ':'))}",
            "",
        ]
    )

    (OUT_DIR / "pr2_tasks4_6_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "pr2_tasks4_6_results.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
