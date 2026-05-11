from __future__ import annotations

from itertools import combinations
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

UNIVERSE = set(range(1, 10))
SETS = {
    "A": {1, 2, 6},
    "B": {2, 3, 4, 5},
    "C": {6, 7, 8},
    "D": {2, 3, 7, 9},
    "E": {1, 3, 4},
    "F": {1, 4, 5, 6, 8},
    "G": {5, 8, 9},
    "H": {1, 6},
}
COSTS = {
    "A": 1,
    "B": 2,
    "C": 1,
    "D": 3,
    "E": 2,
    "F": 3,
    "G": 1,
    "H": 1,
}


def fmt_set(values: set[int]) -> str:
    return "{" + ", ".join(map(str, sorted(values))) + "}"


def union_of(names: tuple[str, ...] | list[str]) -> set[int]:
    result: set[int] = set()
    for name in names:
        result |= SETS[name]
    return result


def price(names: tuple[str, ...] | list[str]) -> int:
    return sum(COSTS[name] for name in names)


def is_cover(names: tuple[str, ...] | list[str]) -> bool:
    return union_of(names) == UNIVERSE


def is_irredundant(names: tuple[str, ...] | list[str]) -> bool:
    if not is_cover(names):
        return False
    return all(not is_cover([item for item in names if item != name]) for name in names)


def full_enumeration() -> list[tuple[str, ...]]:
    names = tuple(SETS)
    covers: list[tuple[str, ...]] = []
    for size in range(1, len(names) + 1):
        for combo in combinations(names, size):
            if is_irredundant(combo):
                covers.append(combo)
    return covers


def boundary_enumeration() -> list[tuple[str, ...]]:
    """Branch on the least-covered uncovered column and prune known supersets."""
    names = tuple(SETS)
    found: set[tuple[str, ...]] = set()

    def search(chosen: tuple[str, ...], covered: set[int]) -> None:
        if covered == UNIVERSE:
            normalized = tuple(name for name in names if name in chosen)
            if is_irredundant(normalized):
                found.add(normalized)
            return

        chosen_set = set(chosen)
        for existing in found:
            if set(existing) <= chosen_set:
                return

        uncovered = UNIVERSE - covered
        candidate_columns = sorted(
            uncovered,
            key=lambda column: sum(1 for name in names if column in SETS[name] and name not in chosen_set),
        )
        column = candidate_columns[0]
        row_candidates = [
            name
            for name in names
            if name not in chosen_set and column in SETS[name]
        ]
        row_candidates.sort(key=lambda name: (-len(SETS[name] - covered), COSTS[name], name))

        for name in row_candidates:
            search(chosen + (name,), covered | SETS[name])

    search(tuple(), set())
    return sorted(found, key=lambda combo: (len(combo), price(combo), combo))


def minimal_column_maximal_row() -> tuple[list[str], list[str]]:
    uncovered = set(UNIVERSE)
    chosen: list[str] = []
    trace: list[str] = []

    while uncovered:
        column_counts = {
            column: [name for name, values in SETS.items() if column in values and name not in chosen]
            for column in uncovered
        }
        column = min(column_counts, key=lambda item: (len(column_counts[item]), item))
        candidates = column_counts[column]
        selected = max(
            candidates,
            key=lambda name: (len(SETS[name] & uncovered), -COSTS[name], -ord(name)),
        )
        chosen.append(selected)
        trace.append(
            f"мінімальний стовпчик {column}, обрано рядок {selected}, "
            f"нове покриття {fmt_set(union_of(chosen))}"
        )
        uncovered -= SETS[selected]

    return chosen, trace


def nuclear_rows_method() -> tuple[list[str], list[str]]:
    uncovered = set(UNIVERSE)
    chosen: list[str] = []
    trace: list[str] = []

    while uncovered:
        essential: list[str] = []
        for column in sorted(uncovered):
            rows = [name for name, values in SETS.items() if column in values and name not in chosen]
            if len(rows) == 1 and rows[0] not in essential:
                essential.append(rows[0])

        if essential:
            for name in essential:
                if name not in chosen:
                    chosen.append(name)
                    trace.append(
                        f"ядровий рядок {name}, покрито {fmt_set(SETS[name])}, "
                        f"разом {fmt_set(union_of(chosen))}"
                    )
            uncovered -= union_of(essential)
            continue

        column_counts = {
            column: [name for name, values in SETS.items() if column in values and name not in chosen]
            for column in uncovered
        }
        column = min(column_counts, key=lambda item: (len(column_counts[item]), item))
        selected = max(
            column_counts[column],
            key=lambda name: (len(SETS[name] & uncovered), -COSTS[name], -ord(name)),
        )
        chosen.append(selected)
        trace.append(
            f"ядрових рядків немає; для стовпчика {column} обрано {selected}, "
            f"разом {fmt_set(union_of(chosen))}"
        )
        uncovered -= SETS[selected]

    return chosen, trace


def markdown_table() -> str:
    headers = ["Підмножина"] + [str(i) for i in range(1, 10)] + ["Ціна"]
    rows = ["| " + " | ".join(headers) + " |"]
    rows.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for name, values in SETS.items():
        cells = [name]
        cells.extend("1" if column in values else "" for column in range(1, 10))
        cells.append(str(COSTS[name]))
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def main() -> None:
    full = full_enumeration()
    boundary = boundary_enumeration()
    min_col_cover, min_col_trace = minimal_column_maximal_row()
    nuclear_cover, nuclear_trace = nuclear_rows_method()
    shortest = [combo for combo in full if len(combo) == min(map(len, full))]

    lines: list[str] = []
    lines.append("Лабораторна робота №2. Варіант 4")
    lines.append("")
    lines.append(f"U = {fmt_set(UNIVERSE)}")
    for name, values in SETS.items():
        lines.append(f"{name} = {fmt_set(values)}, ціна = {COSTS[name]}")
    lines.append("")

    lines.append("Усі безнадлишкові покриття методом повного перебору:")
    for combo in full:
        lines.append(f"{' ∪ '.join(combo)}; ціна = {price(combo)}")
    lines.append(f"Кількість безнадлишкових покриттів: {len(full)}")
    lines.append("")

    lines.append("Безнадлишкові покриття методом граничного перебору:")
    for combo in boundary:
        lines.append(f"{' ∪ '.join(combo)}; ціна = {price(combo)}")
    lines.append(f"Кількість безнадлишкових покриттів: {len(boundary)}")
    lines.append("")

    lines.append("Найкоротші покриття за повним перебором:")
    for combo in shortest:
        lines.append(f"{' ∪ '.join(combo)}; потужність = {len(combo)}, ціна = {price(combo)}")
    lines.append("")

    lines.append("Метод мінімального стовпчика - максимального рядка:")
    for item in min_col_trace:
        lines.append(f"- {item}")
    lines.append(f"Результат: {' ∪ '.join(min_col_cover)}; ціна = {price(min_col_cover)}")
    lines.append("")

    lines.append("Метод ядерних рядків:")
    for item in nuclear_trace:
        lines.append(f"- {item}")
    lines.append(f"Результат: {' ∪ '.join(nuclear_cover)}; ціна = {price(nuclear_cover)}")

    output = "\n".join(lines)
    (BASE_DIR / "lab2_results.txt").write_text(output, encoding="utf-8")
    (BASE_DIR / "variant4_table.md").write_text(markdown_table(), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
