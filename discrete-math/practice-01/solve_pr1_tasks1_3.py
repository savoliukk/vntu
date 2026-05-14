from __future__ import annotations

import json
import os
from pathlib import Path


OUT_DIR = Path(os.path.relpath(Path(__file__).parent, Path.cwd()))


def sorted_set(values: set[int]) -> list[int]:
    return sorted(values)


def fmt(items: list[int]) -> str:
    return "{" + ", ".join(map(str, items)) + "}"


def main() -> None:
    task1: dict[str, object] = {}
    u1 = set(range(1, 15))
    a1 = {1, 2, 3, 4, 7, 9}
    b1 = {3, 4, 5, 6, 11, 12, 13}
    c1 = {2, 3, 4, 7, 8, 12, 13, 14}
    d1 = {1, 7, 14}
    a_union_b = a1 | b1
    not_c = u1 - c1
    not_d = u1 - d1
    not_c_and_not_d = not_c & not_d
    result1 = a_union_b | not_c_and_not_d

    u2 = set(range(1, 10))
    a2 = {1, 2, 3, 4, 5, 9}
    b2 = {2, 4, 6, 8}
    c2 = {1, 3, 5, 7}
    d2 = {1, 4, 5, 7, 8, 9}
    target2 = {1, 2, 4, 5, 6, 7, 8, 9}
    b_union_d = b2 | d2
    a_minus_c = a2 - c2
    result2 = b_union_d | a_minus_c

    task1.update(
        {
            "variant": 29,
            "expression": "(A ∪ B) ∪ (C̄ ∩ D̄)",
            "U": sorted_set(u1),
            "A": sorted_set(a1),
            "B": sorted_set(b1),
            "C": sorted_set(c1),
            "D": sorted_set(d1),
            "aUnionB": sorted_set(a_union_b),
            "notC": sorted_set(not_c),
            "notD": sorted_set(not_d),
            "notCAndNotD": sorted_set(not_c_and_not_d),
            "result": sorted_set(result1),
        }
    )

    results = {
        "task1": task1,
        "task2": {
            "variant": 19,
            "target": sorted_set(target2),
            "expression": "(B ∪ D) ∪ (A \\ C)",
            "bUnionD": sorted_set(b_union_d),
            "aMinusC": sorted_set(a_minus_c),
            "result": sorted_set(result2),
            "matchesTarget": sorted_set(result2) == sorted_set(target2),
        },
        "task3": {
            "variants": [43, 6],
            "diagrams": [
                {
                    "variant": 43,
                    "image": "venn_variant43.jpg",
                    "expression": "C ∪ (A ∩ B)",
                },
                {
                    "variant": 6,
                    "image": "venn_variant6.jpg",
                    "expression": "A ∩ B ∩ C ∩ D",
                },
            ],
        },
    }

    text = "\n".join(
        [
            "Практична робота 1: контрольні результати",
            "",
            f"Задача 1: X = {fmt(results['task1']['result'])}",
            f"  A ∪ B = {fmt(results['task1']['aUnionB'])}",
            f"  C̄ = {fmt(results['task1']['notC'])}",
            f"  D̄ = {fmt(results['task1']['notD'])}",
            f"  C̄ ∩ D̄ = {fmt(results['task1']['notCAndNotD'])}",
            "",
            f"Задача 2: M = {fmt(results['task2']['result'])}",
            f"  Цільова множина = {fmt(results['task2']['target'])}",
            f"  Збіг із цільовою множиною: {'так' if results['task2']['matchesTarget'] else 'ні'}",
            "",
            "Задача 3:",
            "  Варіант 43: E = C ∪ (A ∩ B)",
            "  Варіант 6: E = A ∩ B ∩ C ∩ D",
            "",
        ]
    )

    (OUT_DIR / "pr1_tasks1_3_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "pr1_tasks1_3_results.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
