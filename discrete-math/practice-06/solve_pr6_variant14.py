from __future__ import annotations

import itertools
import json
import math
import os
from pathlib import Path


OUT_DIR = Path(os.path.relpath(Path(__file__).parent, Path.cwd()))
VERTICES = [1, 2, 3, 4, 5]
INF = math.inf
MATRIX = [
    [INF, 16, 9, INF, 2],
    [11, INF, 14, 9, 6],
    [21, 4, INF, 4, 18],
    [7, INF, 1, INF, 22],
    [8, 9, 11, 15, INF],
]


def format_vertex(vertex: int) -> str:
    return f"X{vertex}"


def format_cycle(cycle: list[int]) -> str:
    return " -> ".join(format_vertex(vertex) for vertex in cycle)


def edge_weight(from_vertex: int, to_vertex: int) -> float:
    return MATRIX[from_vertex - 1][to_vertex - 1]


def cycle_edges(cycle: list[int]) -> list[tuple[int, int]]:
    return [(cycle[index], cycle[index + 1]) for index in range(len(cycle) - 1)]


def analyze_cycle(cycle: list[int]) -> dict[str, object]:
    weights: list[int] = []
    cost = 0
    for from_vertex, to_vertex in cycle_edges(cycle):
        weight = edge_weight(from_vertex, to_vertex)
        if not math.isfinite(weight):
            return {
                "cycle": cycle,
                "valid": False,
                "forbiddenEdge": [from_vertex, to_vertex],
                "weights": weights,
                "cost": None,
            }
        weights.append(int(weight))
        cost += int(weight)
    return {
        "cycle": cycle,
        "valid": True,
        "forbiddenEdge": None,
        "weights": weights,
        "cost": cost,
    }


def main() -> None:
    all_cycles = [
        analyze_cycle([1, *order, 1])
        for order in itertools.permutations(VERTICES[1:])
    ]
    valid_cycles = sorted(
        [item for item in all_cycles if item["valid"]],
        key=lambda item: (item["cost"], format_cycle(item["cycle"])),
    )
    if not valid_cycles:
        raise ValueError("No Hamiltonian cycle exists for variant 14.")

    best_cost = valid_cycles[0]["cost"]
    best_cycles = [item for item in valid_cycles if item["cost"] == best_cost]
    if best_cost != 33 or len(best_cycles) != 2:
        raise ValueError(f"Unexpected optimum: cost={best_cost}, count={len(best_cycles)}")

    for item in valid_cycles:
        cycle = item["cycle"]
        unique = set(cycle[:-1])
        if cycle[0] != 1 or cycle[-1] != 1 or len(unique) != len(VERTICES):
            raise ValueError(f"Invalid Hamiltonian cycle structure: {format_cycle(cycle)}")

    allowed_arcs = [
        {"from": VERTICES[i], "to": VERTICES[j], "weight": int(MATRIX[i][j])}
        for i in range(len(VERTICES))
        for j in range(len(VERTICES))
        if math.isfinite(MATRIX[i][j])
    ]

    result = {
        "variant": 14,
        "vertices": [format_vertex(vertex) for vertex in VERTICES],
        "matrix": [
            [int(value) if math.isfinite(value) else None for value in row]
            for row in MATRIX
        ],
        "allowedArcCount": len(allowed_arcs),
        "checkedCycleCount": len(all_cycles),
        "validCycleCount": len(valid_cycles),
        "rejectedCycleCount": len(all_cycles) - len(valid_cycles),
        "minimumCost": best_cost,
        "optimalCycles": [
            {
                "cycle": format_cycle(item["cycle"]),
                "weights": item["weights"],
                "cost": item["cost"],
            }
            for item in best_cycles
        ],
        "validCycles": [
            {
                "order": index + 1,
                "cycle": format_cycle(item["cycle"]),
                "weights": item["weights"],
                "cost": item["cost"],
                "optimal": item["cost"] == best_cost,
            }
            for index, item in enumerate(valid_cycles)
        ],
    }

    summary = "\n".join(
        [
            "Практична робота 6, варіант 14",
            "Тема: гамільтонів контур мінімальної вартості",
            "",
            f"Перевірено перестановок: {result['checkedCycleCount']}",
            f"Допустимих гамільтонових контурів: {result['validCycleCount']}",
            f"Мінімальна вартість: V = {result['minimumCost']}",
            "Оптимальні контури:",
            *[
                f"{index + 1}. {item['cycle']}; {' + '.join(map(str, item['weights']))} = {item['cost']}"
                for index, item in enumerate(result["optimalCycles"])
            ],
            "",
        ]
    )

    (OUT_DIR / "variant14_results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "variant14_results.txt").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
