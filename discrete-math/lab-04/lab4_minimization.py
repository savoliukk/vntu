from __future__ import annotations

from itertools import product
import os
from pathlib import Path
from typing import Iterable

from sympy import And, Equivalent, Implies, Not, Symbol, symbols
from sympy.logic.boolalg import POSform, SOPform, simplify_logic


OUT_DIR = Path(os.path.relpath(Path(__file__).parent, Path.cwd()))
GRAY = [(0, 0), (0, 1), (1, 1), (1, 0)]


def as_int(value: bool) -> int:
    return int(bool(value))


def minterm_index(bits: Iterable[int]) -> int:
    result = 0
    for bit in bits:
        result = result * 2 + int(bit)
    return result


def eval_expr(expr, variables: list[Symbol], values: tuple[int, ...]) -> int:
    substitutions = {variable: bool(value) for variable, value in zip(variables, values)}
    return as_int(expr.subs(substitutions))


def truth_rows_from_expr(expr, variables: list[Symbol]) -> list[list[str]]:
    rows: list[list[str]] = []
    for values in product([0, 1], repeat=len(variables)):
        rows.append([str(minterm_index(values)), *map(str, values), str(eval_expr(expr, variables, values))])
    return rows


def truth_rows_from_minterms(minterms: set[int], dontcares: set[int] | None = None) -> list[list[str]]:
    dontcares = dontcares or set()
    rows: list[list[str]] = []
    for values in product([0, 1], repeat=4):
        index = minterm_index(values)
        if index in dontcares:
            result = "X"
        else:
            result = str(int(index in minterms))
        rows.append([str(index), *map(str, values), result])
    return rows


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    align = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, align, *body])


def karnaugh_grid(values_by_index: dict[int, str]) -> list[list[str]]:
    grid: list[list[str]] = []
    for row_bits in GRAY:
        row: list[str] = []
        for col_bits in GRAY:
            row.append(values_by_index[minterm_index((*row_bits, *col_bits))])
        grid.append(row)
    return grid


def write_kmap_svg(path: Path, title: str, row_label: str, col_label: str, values_by_index: dict[int, str]) -> None:
    grid = karnaugh_grid(values_by_index)
    cell = 58
    left = 116
    top = 100
    width = left + cell * 4 + 38
    height = top + cell * 4 + 40
    row_headers = ["00", "01", "11", "10"]
    col_headers = ["00", "01", "11", "10"]
    colors = {"1": "#dff4e7", "0": "#f4f6fb", "X": "#fff2cc"}

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,Helvetica,sans-serif;fill:#172033;font-size:14px}",
        ".title{font-size:18px;font-weight:700}",
        ".head{font-weight:700}",
        ".cellText{font-size:22px;font-weight:700}",
        ".cell{stroke:#60708a;stroke-width:1.2}",
        "</style>",
        f'<text x="{left}" y="32" class="title">{title}</text>',
        f'<text x="{left + cell * 2}" y="68" text-anchor="middle" class="head">{col_label}</text>',
        f'<text x="30" y="{top + cell * 2}" transform="rotate(-90 30 {top + cell * 2})" text-anchor="middle" class="head">{row_label}</text>',
    ]

    for index, header in enumerate(col_headers):
        x = left + index * cell + cell / 2
        parts.append(f'<text x="{x}" y="{top - 14}" text-anchor="middle" class="head">{header}</text>')

    for r, header in enumerate(row_headers):
        y = top + r * cell + cell / 2 + 5
        parts.append(f'<text x="{left - 22}" y="{y}" text-anchor="end" class="head">{header}</text>')

    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            x = left + c * cell
            y = top + r * cell
            fill = colors.get(value, "#ffffff")
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{fill}" class="cell"/>')
            parts.append(
                f'<text x="{x + cell / 2}" y="{y + cell / 2 + 8}" text-anchor="middle" class="cellText">{value}</text>'
            )

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def complexity(expr) -> tuple[int, int]:
    text = str(expr)
    literals = sum(text.count(name) for name in ["A", "B", "C", "D", "x1", "x2", "x3", "x4"])
    operations = text.count("&") + text.count("|") + text.count("~")
    return literals, operations


def main() -> None:
    A, B, C, D = symbols("A B C D")
    variables_task1 = [A, B, C, D]

    # Variant 24 from table 5.1:
    # f = ((A -> B) and C) equivalent (A NAND D)
    task1_expr = Equivalent(And(Implies(A, B), C), Not(And(A, D)))
    task1_dnf = simplify_logic(task1_expr, form="dnf")
    task1_cnf = simplify_logic(task1_expr, form="cnf")
    task1_true = {
        index
        for index, values in enumerate(product([0, 1], repeat=4))
        if eval_expr(task1_expr, variables_task1, values)
    }

    x1, x2, x3, x4 = symbols("x1 x2 x3 x4")
    variables_task2 = [x1, x2, x3, x4]
    task2_minterms = {0, 4, 5, 8, 9, 10, 12, 13, 14}
    task2_dontcares = {1, 3, 7}
    task2_sop = SOPform(variables_task2, sorted(task2_minterms))
    task2_pos = POSform(variables_task2, sorted(task2_minterms))
    task2_sop_dc = SOPform(variables_task2, sorted(task2_minterms), sorted(task2_dontcares))
    task2_pos_dc = POSform(variables_task2, sorted(task2_minterms), sorted(task2_dontcares))

    task1_values = {i: str(int(i in task1_true)) for i in range(16)}
    task2_values = {i: str(int(i in task2_minterms)) for i in range(16)}
    task2_values_dc = {
        i: ("X" if i in task2_dontcares else str(int(i in task2_minterms))) for i in range(16)
    }

    write_kmap_svg(OUT_DIR / "task1_kmap.svg", "Task 1 Karnaugh map", "AB", "CD", task1_values)
    write_kmap_svg(OUT_DIR / "task2_kmap.svg", "Task 2 Karnaugh map", "x1x2", "x3x4", task2_values)
    write_kmap_svg(
        OUT_DIR / "task2_kmap_dontcares.svg",
        "Task 2 Karnaugh map with don't-cares",
        "x1x2",
        "x3x4",
        task2_values_dc,
    )

    results = "\n\n".join(
        [
            "ЛР4. Мінімізація булевих функцій",
            "Завдання 1, варіант 24",
            "Початкова функція: f = ((A -> B) & C) ~ (A NAND D)",
            f"Набори, де f = 1: {sorted(task1_true)}",
            f"МінДНФ simplify_logic: {task1_dnf}",
            f"МінКНФ simplify_logic: {task1_cnf}",
            f"Складність мінДНФ (літерали, операції): {complexity(task1_dnf)}",
            f"Складність мінКНФ (літерали, операції): {complexity(task1_cnf)}",
            markdown_table(["i", "A", "B", "C", "D", "f"], truth_rows_from_expr(task1_expr, variables_task1)),
            "Завдання 2, варіант 24",
            f"Мінтерми: {sorted(task2_minterms)}",
            f"МінДНФ SOPform: {task2_sop}",
            f"МінКНФ POSform: {task2_pos}",
            f"Складність мінДНФ (літерали, операції): {complexity(task2_sop)}",
            f"Складність мінКНФ (літерали, операції): {complexity(task2_pos)}",
            markdown_table(["i", "x1", "x2", "x3", "x4", "F"], truth_rows_from_minterms(task2_minterms)),
            f"Обрані неважливі терми: {sorted(task2_dontcares)}",
            f"МінДНФ SOPform з неважливими термами: {task2_sop_dc}",
            f"МінКНФ POSform з неважливими термами: {task2_pos_dc}",
            f"Складність мінДНФ з неважливими термами (літерали, операції): {complexity(task2_sop_dc)}",
            f"Складність мінКНФ з неважливими термами (літерали, операції): {complexity(task2_pos_dc)}",
            markdown_table(
                ["i", "x1", "x2", "x3", "x4", "F"],
                truth_rows_from_minterms(task2_minterms, task2_dontcares),
            ),
        ]
    )

    (OUT_DIR / "lab4_results.txt").write_text(results + "\n", encoding="utf-8")
    print(results)


if __name__ == "__main__":
    main()
