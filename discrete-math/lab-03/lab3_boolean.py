from __future__ import annotations

from itertools import product
from pathlib import Path

import numpy as np


OUT_DIR = Path(__file__).resolve().parent


def bit(value: bool) -> int:
    return int(bool(value))


def bits(values: np.ndarray) -> list[int]:
    return [bit(value) for value in values]


def implication(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.logical_or(np.logical_not(a), b)


def equivalence(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.equal(a, b)


def nand(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.logical_not(np.logical_and(a, b))


def make_rows(names: list[str]) -> dict[str, np.ndarray]:
    rows = np.array(list(product([False, True], repeat=len(names))), dtype=bool)
    return {name: rows[:, index] for index, name in enumerate(names)}


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    align = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, align, *body])


def write_timing_svg(path: Path, title: str, signals: list[tuple[str, np.ndarray]], labels: list[str]) -> None:
    step = 58
    left = 190
    right = 36
    top = 64
    row_h = 44
    amp = 13
    label_y = 30
    width = left + step * len(labels) + right
    height = top + row_h * len(signals) + 42
    grid_bottom = top + row_h * len(signals) - 8

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,Helvetica,sans-serif;font-size:13px;fill:#172033}",
        ".title{font-size:18px;font-weight:700}",
        ".label{font-weight:700}",
        ".grid{stroke:#d9dee8;stroke-width:1}",
        ".axis{stroke:#aeb7c7;stroke-width:1}",
        ".wave{fill:none;stroke:#1c5aa6;stroke-width:3;stroke-linejoin:round;stroke-linecap:round}",
        ".zeroone{font-size:11px;fill:#657086}",
        "</style>",
        f'<text x="{left}" y="{label_y}" class="title">{title}</text>',
    ]

    for index, label in enumerate(labels):
        x = left + index * step + step / 2
        parts.append(f'<text x="{x}" y="50" text-anchor="middle" class="zeroone">{label}</text>')
        gx = left + index * step
        parts.append(f'<line x1="{gx}" y1="{top - 24}" x2="{gx}" y2="{grid_bottom}" class="grid"/>')
    parts.append(
        f'<line x1="{left + len(labels) * step}" y1="{top - 24}" '
        f'x2="{left + len(labels) * step}" y2="{grid_bottom}" class="grid"/>'
    )

    for signal_index, (name, values) in enumerate(signals):
        base = top + signal_index * row_h + 24
        high_y = base - amp
        low_y = base + amp
        parts.append(f'<text x="18" y="{base + 5}" class="label">{name}</text>')
        parts.append(f'<text x="{left - 28}" y="{high_y + 4}" text-anchor="end" class="zeroone">1</text>')
        parts.append(f'<text x="{left - 28}" y="{low_y + 4}" text-anchor="end" class="zeroone">0</text>')
        parts.append(f'<line x1="{left - 18}" y1="{high_y}" x2="{left + step * len(labels)}" y2="{high_y}" class="axis"/>')
        parts.append(f'<line x1="{left - 18}" y1="{low_y}" x2="{left + step * len(labels)}" y2="{low_y}" class="axis"/>')

        values_as_bits = bits(values)
        y = high_y if values_as_bits[0] else low_y
        path_data = [f"M {left} {y}"]
        for i, value in enumerate(values_as_bits):
            x_next = left + (i + 1) * step
            current_y = high_y if value else low_y
            path_data.append(f"H {x_next}")
            if i + 1 < len(values_as_bits):
                next_y = high_y if values_as_bits[i + 1] else low_y
                if next_y != current_y:
                    path_data.append(f"V {next_y}")
        parts.append(f'<path d="{" ".join(path_data)}" class="wave"/>')

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def solve_task1() -> dict[str, np.ndarray]:
    values = make_rows(["x1", "x2", "x3"])
    not_x3 = np.logical_not(values["x3"])
    xor_part = np.logical_xor(values["x1"], not_x3)
    not_x2 = np.logical_not(values["x2"])
    eq_part = equivalence(values["x1"], not_x2)
    f = np.logical_and(xor_part, eq_part)
    return {
        **values,
        "not_x3": not_x3,
        "xor_part": xor_part,
        "not_x2": not_x2,
        "eq_part": eq_part,
        "f": f,
    }


def solve_task2() -> dict[str, np.ndarray]:
    values = make_rows(["A", "B", "C", "D"])
    impl_part = implication(values["A"], values["B"])
    and_part = np.logical_and(impl_part, values["C"])
    nand_part = nand(values["A"], values["D"])
    f = equivalence(and_part, nand_part)
    return {
        **values,
        "impl_part": impl_part,
        "and_part": and_part,
        "nand_part": nand_part,
        "f": f,
    }


def build_results() -> str:
    task1 = solve_task1()
    task1_rows = []
    for i in range(8):
        task1_rows.append(
            [
                str(i),
                str(bit(task1["x1"][i])),
                str(bit(task1["x2"][i])),
                str(bit(task1["x3"][i])),
                str(bit(task1["not_x3"][i])),
                str(bit(task1["xor_part"][i])),
                str(bit(task1["not_x2"][i])),
                str(bit(task1["eq_part"][i])),
                str(bit(task1["f"][i])),
            ]
        )

    task2 = solve_task2()
    task2_rows = []
    for i in range(16):
        task2_rows.append(
            [
                str(i),
                str(bit(task2["A"][i])),
                str(bit(task2["B"][i])),
                str(bit(task2["C"][i])),
                str(bit(task2["D"][i])),
                str(bit(task2["impl_part"][i])),
                str(bit(task2["and_part"][i])),
                str(bit(task2["nand_part"][i])),
                str(bit(task2["f"][i])),
            ]
        )

    task1_labels = [
        f'{bit(task1["x1"][i])}{bit(task1["x2"][i])}{bit(task1["x3"][i])}'
        for i in range(8)
    ]
    task2_labels = [
        f'{bit(task2["A"][i])}{bit(task2["B"][i])}{bit(task2["C"][i])}{bit(task2["D"][i])}'
        for i in range(16)
    ]

    write_timing_svg(
        OUT_DIR / "task1_timing.svg",
        "Task 1: f = (x1 XOR NOT x3) AND (x1 EQUIV NOT x2)",
        [
            ("x1", task1["x1"]),
            ("x2", task1["x2"]),
            ("x3", task1["x3"]),
            ("NOT x3", task1["not_x3"]),
            ("x1 XOR NOT x3", task1["xor_part"]),
            ("NOT x2", task1["not_x2"]),
            ("x1 EQUIV NOT x2", task1["eq_part"]),
            ("f", task1["f"]),
        ],
        task1_labels,
    )
    write_timing_svg(
        OUT_DIR / "task2_timing.svg",
        "Task 2: f = (((A IMPL B) AND C) EQUIV (A NAND D))",
        [
            ("A", task2["A"]),
            ("B", task2["B"]),
            ("C", task2["C"]),
            ("D", task2["D"]),
            ("A IMPL B", task2["impl_part"]),
            ("(A IMPL B) AND C", task2["and_part"]),
            ("A NAND D", task2["nand_part"]),
            ("f", task2["f"]),
        ],
        task2_labels,
    )

    return "\n\n".join(
        [
            "ЛР3. Булеві функції",
            "Завдання 1, варіант 7: f = (x1 XOR NOT x3) AND (x1 EQUIV NOT x2)",
            markdown_table(
                ["i", "x1", "x2", "x3", "NOT x3", "x1 XOR NOT x3", "NOT x2", "x1 EQUIV NOT x2", "f"],
                task1_rows,
            ),
            f"Вектор f для завдання 1: {bits(task1['f'])}",
            "Завдання 2, практичний варіант 24: f = ((A IMPL B) AND C) EQUIV (A NAND D)",
            markdown_table(
                ["i", "A", "B", "C", "D", "A IMPL B", "(A IMPL B) AND C", "A NAND D", "f"],
                task2_rows,
            ),
            f"Вектор f для завдання 2: {bits(task2['f'])}",
        ]
    )


def main() -> None:
    results = build_results()
    (OUT_DIR / "lab3_results.txt").write_text(results + "\n", encoding="utf-8")
    print(results)


if __name__ == "__main__":
    main()
