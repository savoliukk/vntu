from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(os.path.relpath(Path(__file__).parent, Path.cwd()))


def format_set(values: set, *, letters: bool = False) -> str:
    ordered = sorted(values) if letters else sorted(values)
    return "{" + ", ".join(map(str, ordered)) + "}"


def write_venn_svg(path: Path, regions: dict[str, int]) -> None:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="760" height="520" viewBox="0 0 760 520">
  <rect x="20" y="20" width="720" height="460" fill="#ffffff" stroke="#111827" stroke-width="2"/>
  <text x="380" y="58" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="700">Варіант 8: розподіл респондентів</text>
  <circle cx="315" cy="230" r="135" fill="#ef4444" fill-opacity="0.38" stroke="#b91c1c" stroke-width="3"/>
  <circle cx="445" cy="230" r="135" fill="#22c55e" fill-opacity="0.38" stroke="#15803d" stroke-width="3"/>
  <circle cx="380" cy="330" r="135" fill="#3b82f6" fill-opacity="0.38" stroke="#1d4ed8" stroke-width="3"/>
  <text x="238" y="106" font-family="Arial, sans-serif" font-size="22" font-weight="700">A</text>
  <text x="512" y="106" font-family="Arial, sans-serif" font-size="22" font-weight="700">B</text>
  <text x="380" y="492" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" font-weight="700">C</text>
  <text x="248" y="224" text-anchor="middle" font-family="Arial, sans-serif" font-size="24">{regions["only_a"]}</text>
  <text x="512" y="224" text-anchor="middle" font-family="Arial, sans-serif" font-size="24">{regions["only_b"]}</text>
  <text x="380" y="397" text-anchor="middle" font-family="Arial, sans-serif" font-size="24">{regions["only_c"]}</text>
  <text x="380" y="197" text-anchor="middle" font-family="Arial, sans-serif" font-size="24">{regions["ab_only"]}</text>
  <text x="316" y="307" text-anchor="middle" font-family="Arial, sans-serif" font-size="24">{regions["ac_only"]}</text>
  <text x="444" y="307" text-anchor="middle" font-family="Arial, sans-serif" font-size="24">{regions["bc_only"]}</text>
  <text x="380" y="274" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="700">{regions["abc"]}</text>
  <text x="610" y="438" text-anchor="middle" font-family="Arial, sans-serif" font-size="20">жодного: {regions["none"]}</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def solve_task1() -> dict[str, set[str]]:
    # Завдання 1, лабораторний варіант 8.
    U_lab = set("abcdefghij")
    A_lab = {"a", "b", "c", "f", "g", "i"}
    B_lab = {"b", "d", "g", "j"}
    C_lab = {"a", "e", "g", "h"}
    D_lab = {"c", "d", "e", "i", "j"}

    lab_ab = A_lab & B_lab
    lab_ab_union_c = lab_ab | C_lab
    lab_x = lab_ab_union_c | D_lab

    return {
        "U_lab": U_lab,
        "A_lab": A_lab,
        "B_lab": B_lab,
        "C_lab": C_lab,
        "D_lab": D_lab,
        "lab_ab": lab_ab,
        "lab_ab_union_c": lab_ab_union_c,
        "lab_x": lab_x,
    }


def solve_task2() -> dict[str, set[int]]:
    # Завдання 2, практичний варіант 29.
    U_pr = set(range(1, 15))
    A_pr = {1, 2, 3, 4, 7, 9}
    B_pr = {3, 4, 5, 6, 11, 12, 13}
    C_pr = {2, 3, 4, 7, 8, 12, 13, 14}
    D_pr = {1, 7, 14}

    pr_a_union_b = A_pr | B_pr
    pr_not_c = U_pr - C_pr
    pr_not_d = U_pr - D_pr
    pr_not_c_and_not_d = pr_not_c & pr_not_d
    pr_x = pr_a_union_b | pr_not_c_and_not_d

    return {
        "U_pr": U_pr,
        "A_pr": A_pr,
        "B_pr": B_pr,
        "C_pr": C_pr,
        "D_pr": D_pr,
        "pr_a_union_b": pr_a_union_b,
        "pr_not_c": pr_not_c,
        "pr_not_d": pr_not_d,
        "pr_not_c_and_not_d": pr_not_c_and_not_d,
        "pr_x": pr_x,
    }


def solve_task3() -> dict[str, object]:
    # Завдання 3, лабораторний варіант 8 з табл. Л1.2.
    n1, n2, n3 = 9, 14, 18
    n12, n13, n23, n123 = 4, 3, 5, 2
    total = 50

    regions = {
        "only_a": n1 - n12 - n13 + n123,
        "only_b": n2 - n12 - n23 + n123,
        "only_c": n3 - n13 - n23 + n123,
        "ab_only": n12 - n123,
        "ac_only": n13 - n123,
        "bc_only": n23 - n123,
        "abc": n123,
    }
    at_least_one = n1 + n2 + n3 - n12 - n13 - n23 + n123
    regions["none"] = total - at_least_one
    only_one = regions["only_a"] + regions["only_b"] + regions["only_c"]

    return {
        "regions": regions,
        "at_least_one": at_least_one,
        "only_one": only_one,
    }


def main() -> None:
    task1 = solve_task1()
    task2 = solve_task2()
    task3 = solve_task3()
    regions = task3["regions"]

    output = f"""Лабораторна робота №1. Варіант 8

Завдання 1
U = {format_set(task1["U_lab"], letters=True)}
A = {format_set(task1["A_lab"], letters=True)}
B = {format_set(task1["B_lab"], letters=True)}
C = {format_set(task1["C_lab"], letters=True)}
D = {format_set(task1["D_lab"], letters=True)}
A ∩ B = {format_set(task1["lab_ab"], letters=True)}
(A ∩ B) ∪ C = {format_set(task1["lab_ab_union_c"], letters=True)}
X = ((A ∩ B) ∪ C) ∪ D = {format_set(task1["lab_x"], letters=True)}

Завдання 2. Практичний варіант 29
U = {format_set(task2["U_pr"])}
A = {format_set(task2["A_pr"])}
B = {format_set(task2["B_pr"])}
C = {format_set(task2["C_pr"])}
D = {format_set(task2["D_pr"])}
A ∪ B = {format_set(task2["pr_a_union_b"])}
~C = U \\ C = {format_set(task2["pr_not_c"])}
~D = U \\ D = {format_set(task2["pr_not_d"])}
~C ∩ ~D = {format_set(task2["pr_not_c_and_not_d"])}
X = (A ∪ B) ∪ (~C ∩ ~D) = {format_set(task2["pr_x"])}

Завдання 3
Тільки A = {regions["only_a"]}
Тільки B = {regions["only_b"]}
Тільки C = {regions["only_c"]}
A ∩ B без C = {regions["ab_only"]}
A ∩ C без B = {regions["ac_only"]}
B ∩ C без A = {regions["bc_only"]}
A ∩ B ∩ C = {regions["abc"]}
Принаймні один додаток = {task3["at_least_one"]}
Лише один конкретний додаток = {task3["only_one"]}
Жодного з додатків = {regions["none"]}
"""

    (BASE_DIR / "lab1_results.txt").write_text(output, encoding="utf-8")
    write_venn_svg(BASE_DIR / "venn_variant8.svg", regions)
    print(output)


if __name__ == "__main__":
    main()
