from __future__ import annotations

import json
import math
import os
from pathlib import Path


OUT_DIR = Path(os.path.relpath(Path(__file__).parent, Path.cwd()))
VERTICES = [f"X{index}" for index in range(1, 14)]
SOURCE = "X1"
TARGET = "X13"
EDGES = [
    ("X1", "X2", 3),
    ("X1", "X3", 4),
    ("X1", "X4", 4),
    ("X2", "X5", 1),
    ("X2", "X6", 2),
    ("X3", "X5", 2),
    ("X3", "X7", 1),
    ("X4", "X6", 2),
    ("X4", "X7", 2),
    ("X4", "X8", 3),
    ("X5", "X9", 2),
    ("X5", "X11", 2),
    ("X6", "X10", 1),
    ("X6", "X12", 1),
    ("X7", "X9", 1),
    ("X7", "X10", 1),
    ("X8", "X11", 1),
    ("X8", "X12", 2),
    ("X9", "X13", 3),
    ("X10", "X13", 2),
    ("X11", "X13", 2),
    ("X12", "X13", 3),
]
LAYERS = [
    ["X1"],
    ["X2", "X3", "X4"],
    ["X5", "X6", "X7", "X8"],
    ["X9", "X10", "X11", "X12"],
    ["X13"],
]


def adjacency() -> dict[str, list[dict[str, object]]]:
    graph = {vertex: [] for vertex in VERTICES}
    for from_vertex, to_vertex, weight in EDGES:
        graph[from_vertex].append({"to": to_vertex, "weight": weight})
    return graph


def restore_path(previous: dict[str, str | None], finish: str) -> list[str]:
    path_items = []
    current: str | None = finish
    while current:
        path_items.append(current)
        current = previous[current]
    return list(reversed(path_items))


def format_distance(value: float) -> str:
    return str(int(value)) if math.isfinite(value) else "inf"


def wave_algorithm() -> dict[str, object]:
    graph = adjacency()
    distances = {vertex: math.inf for vertex in VERTICES}
    previous: dict[str, str | None] = {vertex: None for vertex in VERTICES}
    trace = []
    distances[SOURCE] = 0

    for layer in LAYERS:
        before = dict(distances)
        for from_vertex in layer:
            if not math.isfinite(distances[from_vertex]):
                continue
            for edge in graph[from_vertex]:
                to_vertex = str(edge["to"])
                candidate = distances[from_vertex] + int(edge["weight"])
                if candidate < distances[to_vertex]:
                    distances[to_vertex] = candidate
                    previous[to_vertex] = from_vertex
        trace.append(
            {
                "layer": layer,
                "changed": [
                    {
                        "vertex": vertex,
                        "distance": int(distances[vertex]),
                        "previous": previous[vertex],
                    }
                    for vertex in VERTICES
                    if distances[vertex] != before[vertex]
                ],
            }
        )

    return {
        "distance": int(distances[TARGET]),
        "path": restore_path(previous, TARGET),
        "distances": {vertex: int(distances[vertex]) for vertex in VERTICES},
        "previous": previous,
        "trace": trace,
    }


def dijkstra() -> dict[str, object]:
    graph = adjacency()
    distances = {vertex: math.inf for vertex in VERTICES}
    previous: dict[str, str | None] = {vertex: None for vertex in VERTICES}
    visited: set[str] = set()
    trace = []
    distances[SOURCE] = 0

    while len(visited) < len(VERTICES):
        current = sorted(
            [vertex for vertex in VERTICES if vertex not in visited],
            key=lambda vertex: (distances[vertex], vertex),
        )[0]
        if not current or not math.isfinite(distances[current]):
            break
        visited.add(current)

        updates = []
        for edge in graph[current]:
            to_vertex = str(edge["to"])
            if to_vertex in visited:
                continue
            candidate = distances[current] + int(edge["weight"])
            if candidate < distances[to_vertex]:
                distances[to_vertex] = candidate
                previous[to_vertex] = current
                updates.append(
                    {
                        "vertex": to_vertex,
                        "distance": int(candidate),
                        "previous": current,
                    }
                )
        trace.append(
            {
                "selected": current,
                "selectedDistance": int(distances[current]),
                "updates": updates,
            }
        )

    return {
        "distance": int(distances[TARGET]),
        "path": restore_path(previous, TARGET),
        "distances": {vertex: int(distances[vertex]) for vertex in VERTICES},
        "previous": previous,
        "trace": trace,
    }


def enumerate_shortest_paths(shortest_distance: int, limit: int = 20) -> list[list[str]]:
    graph = adjacency()
    result: list[list[str]] = []

    def walk(vertex: str, distance: int, path_items: list[str]) -> None:
        if len(result) >= limit or distance > shortest_distance:
            return
        if vertex == TARGET:
            if distance == shortest_distance:
                result.append(path_items[:])
            return
        for edge in graph[vertex]:
            walk(str(edge["to"]), distance + int(edge["weight"]), [*path_items, str(edge["to"])])

    walk(SOURCE, 0, [SOURCE])
    return result


def main() -> None:
    wave = wave_algorithm()
    dijkstra_result = dijkstra()
    all_shortest_paths = enumerate_shortest_paths(int(dijkstra_result["distance"]))

    result = {
        "variant": 14,
        "source": SOURCE,
        "target": TARGET,
        "vertices": VERTICES,
        "layers": LAYERS,
        "edges": [
            {"from": from_vertex, "to": to_vertex, "weight": weight}
            for from_vertex, to_vertex, weight in EDGES
        ],
        "wave": wave,
        "dijkstra": dijkstra_result,
        "allShortestPaths": all_shortest_paths,
        "checks": {
            "sameDistance": wave["distance"] == dijkstra_result["distance"],
            "samePath": "->".join(wave["path"]) == "->".join(dijkstra_result["path"]),
        },
    }

    text = "\n".join(
        [
            "Практична робота №4. Варіант 14",
            "",
            f"Найкоротший шлях за хвильовим алгоритмом: {' -> '.join(wave['path'])}, довжина = {wave['distance']}",
            f"Найкоротший шлях за алгоритмом Дейкстри: {' -> '.join(dijkstra_result['path'])}, довжина = {dijkstra_result['distance']}",
            f"Кількість знайдених найкоротших шляхів довжини {dijkstra_result['distance']}: {len(all_shortest_paths)}",
            "",
            "Фінальні відстані:",
            *[
                f"{vertex}: {format_distance(dijkstra_result['distances'][vertex])}"
                for vertex in VERTICES
            ],
        ]
    )

    (OUT_DIR / "variant14_results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "variant14_results.txt").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
