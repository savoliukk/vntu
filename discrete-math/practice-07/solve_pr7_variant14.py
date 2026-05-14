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


def v(vertex: int) -> str:
    return f"X{vertex}"


def format_cycle(cycle: list[int]) -> str:
    return " -> ".join(v(vertex) for vertex in cycle)


def weight(from_vertex: int, to_vertex: int) -> float:
    return MATRIX[from_vertex - 1][to_vertex - 1]


def analyze_cycle(cycle: list[int]) -> dict[str, object]:
    weights: list[int] = []
    cost = 0
    for index in range(len(cycle) - 1):
        edge_weight = weight(cycle[index], cycle[index + 1])
        if not math.isfinite(edge_weight):
            return {
                "cycle": cycle,
                "valid": False,
                "forbiddenEdge": [cycle[index], cycle[index + 1]],
                "weights": [],
                "cost": None,
            }
        weights.append(int(edge_weight))
        cost += int(edge_weight)
    return {"cycle": cycle, "valid": True, "forbiddenEdge": None, "weights": weights, "cost": cost}


def main() -> None:
    all_cycles = [
        analyze_cycle([1, *order, 1])
        for order in itertools.permutations(VERTICES[1:])
    ]
    valid_cycles = sorted(
        [item for item in all_cycles if item["valid"]],
        key=lambda item: (item["cost"], format_cycle(item["cycle"])),
    )
    minimum_cost = valid_cycles[0]["cost"]
    optimal_cycles = [item for item in valid_cycles if item["cost"] == minimum_cost]

    if len(all_cycles) != 24:
        raise ValueError(f"Expected 24 checked cycles, got {len(all_cycles)}")
    if len(valid_cycles) != 14:
        raise ValueError(f"Expected 14 valid cycles, got {len(valid_cycles)}")
    if minimum_cost != 33:
        raise ValueError(f"Expected minimum cost 33, got {minimum_cost}")
    if len(optimal_cycles) != 2:
        raise ValueError(f"Expected 2 optimal cycles, got {len(optimal_cycles)}")

    for item in valid_cycles:
        cycle = item["cycle"]
        unique_vertices = set(cycle[:-1])
        if cycle[0] != 1 or cycle[-1] != 1 or len(unique_vertices) != len(VERTICES):
            raise ValueError(f"Invalid Hamiltonian cycle: {format_cycle(cycle)}")

    result = {
        "variant": 14,
        "task": "Hamiltonian cycle of minimum cost",
        "vertices": [v(vertex) for vertex in VERTICES],
        "matrix": [
            [int(value) if math.isfinite(value) else None for value in row]
            for row in MATRIX
        ],
        "checkedCycleCount": len(all_cycles),
        "validCycleCount": len(valid_cycles),
        "rejectedCycleCount": len(all_cycles) - len(valid_cycles),
        "minimumCost": minimum_cost,
        "optimalCycles": [
            {
                "cycle": format_cycle(item["cycle"]),
                "weights": item["weights"],
                "cost": item["cost"],
            }
            for item in optimal_cycles
        ],
        "validCycles": [
            {
                "order": index + 1,
                "cycle": format_cycle(item["cycle"]),
                "weights": item["weights"],
                "cost": item["cost"],
                "optimal": item["cost"] == minimum_cost,
            }
            for index, item in enumerate(valid_cycles)
        ],
    }

    summary = "\n".join(
        [
            "Практична робота 7, варіант 14",
            "Тема: гамільтонів контур",
            "",
            f"Перевірено перестановок: {len(all_cycles)}",
            f"Допустимих гамільтонових контурів: {len(valid_cycles)}",
            f"Недопустимих контурів: {len(all_cycles) - len(valid_cycles)}",
            f"Мінімальна вартість: V = {minimum_cost}",
            "Оптимальні контури:",
            *[
                f"{index + 1}. {format_cycle(item['cycle'])}; {' + '.join(map(str, item['weights']))} = {item['cost']}"
                for index, item in enumerate(optimal_cycles)
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
