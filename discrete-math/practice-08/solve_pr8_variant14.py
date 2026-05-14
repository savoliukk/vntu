from __future__ import annotations

import json
import os
from collections import deque
from pathlib import Path


OUT_DIR = Path(os.path.relpath(Path(__file__).parent, Path.cwd()))
VARIANT = 14
SOURCE = 1
SINK = 13
VERTEX_COUNT = 13

EDGES = [
    {"from": 1, "to": 2, "capacity": 3},
    {"from": 1, "to": 3, "capacity": 4},
    {"from": 1, "to": 4, "capacity": 4},
    {"from": 2, "to": 5, "capacity": 1},
    {"from": 2, "to": 6, "capacity": 2},
    {"from": 3, "to": 5, "capacity": 2},
    {"from": 3, "to": 7, "capacity": 1},
    {"from": 4, "to": 6, "capacity": 2},
    {"from": 4, "to": 7, "capacity": 2},
    {"from": 4, "to": 8, "capacity": 3},
    {"from": 5, "to": 9, "capacity": 2},
    {"from": 5, "to": 11, "capacity": 2},
    {"from": 6, "to": 10, "capacity": 1},
    {"from": 6, "to": 12, "capacity": 1},
    {"from": 7, "to": 9, "capacity": 1},
    {"from": 7, "to": 10, "capacity": 1},
    {"from": 8, "to": 11, "capacity": 1},
    {"from": 8, "to": 12, "capacity": 2},
    {"from": 9, "to": 13, "capacity": 3},
    {"from": 10, "to": 13, "capacity": 2},
    {"from": 11, "to": 13, "capacity": 2},
    {"from": 12, "to": 13, "capacity": 3},
]

EXPECTED_PATHS = [
    {"path": [1, 2, 5, 9, 13], "theta": 1},
    {"path": [1, 2, 6, 10, 13], "theta": 1},
    {"path": [1, 2, 6, 12, 13], "theta": 1},
    {"path": [1, 3, 5, 9, 13], "theta": 1},
    {"path": [1, 3, 5, 11, 13], "theta": 1},
    {"path": [1, 3, 7, 9, 13], "theta": 1},
    {"path": [1, 4, 7, 10, 13], "theta": 1},
    {"path": [1, 4, 8, 11, 13], "theta": 1},
    {"path": [1, 4, 8, 12, 13], "theta": 2},
]


def vertex_name(vertex: int) -> str:
    return f"X{vertex}"


def path_name(vertices: list[int]) -> str:
    return " -> ".join(vertex_name(vertex) for vertex in vertices)


def edge_name(edge: dict[str, int]) -> str:
    return f"{vertex_name(edge['from'])} -> {vertex_name(edge['to'])}"


def make_matrix(fill: int = 0) -> list[list[int]]:
    return [[fill for _ in range(VERTEX_COUNT + 1)] for _ in range(VERTEX_COUNT + 1)]


def add_neighbor(adjacency: list[list[int]], from_vertex: int, to_vertex: int) -> None:
    if to_vertex not in adjacency[from_vertex]:
        adjacency[from_vertex].append(to_vertex)


def build_network() -> tuple[list[list[int]], list[list[int]], list[list[int]]]:
    capacity = make_matrix()
    residual = make_matrix()
    adjacency = [[] for _ in range(VERTEX_COUNT + 1)]

    for edge in EDGES:
        from_vertex = edge["from"]
        to_vertex = edge["to"]
        capacity[from_vertex][to_vertex] += edge["capacity"]
        residual[from_vertex][to_vertex] += edge["capacity"]
        add_neighbor(adjacency, from_vertex, to_vertex)
        add_neighbor(adjacency, to_vertex, from_vertex)

    return capacity, residual, adjacency


def bfs(residual: list[list[int]], adjacency: list[list[int]]) -> dict[str, object]:
    parent = [-1 for _ in range(VERTEX_COUNT + 1)]
    bottleneck = [0 for _ in range(VERTEX_COUNT + 1)]
    queue: deque[int] = deque([SOURCE])
    parent[SOURCE] = SOURCE
    bottleneck[SOURCE] = 10**9

    while queue:
        current = queue.popleft()
        for next_vertex in adjacency[current]:
            if parent[next_vertex] != -1 or residual[current][next_vertex] <= 0:
                continue
            parent[next_vertex] = current
            bottleneck[next_vertex] = min(bottleneck[current], residual[current][next_vertex])
            if next_vertex == SINK:
                return {"found": True, "parent": parent, "theta": bottleneck[next_vertex]}
            queue.append(next_vertex)

    return {"found": False, "parent": parent, "theta": 0}


def reconstruct_path(parent: list[int]) -> list[int]:
    result = []
    current = SINK
    while current != SOURCE:
        result.append(current)
        current = parent[current]
    result.append(SOURCE)
    return list(reversed(result))


def edmonds_karp() -> dict[str, object]:
    capacity, residual, adjacency = build_network()
    max_flow = 0
    augmenting_paths = []

    while True:
        step = bfs(residual, adjacency)
        if not step["found"]:
            break

        vertices = reconstruct_path(step["parent"])
        theta = int(step["theta"])
        for index in range(len(vertices) - 1):
            u = vertices[index]
            v = vertices[index + 1]
            residual[u][v] -= theta
            residual[v][u] += theta

        max_flow += theta
        augmenting_paths.append(
            {
                "step": len(augmenting_paths) + 1,
                "vertices": vertices,
                "path": path_name(vertices),
                "theta": theta,
                "flowAfterStep": max_flow,
            }
        )

    final_flow = [
        {
            "index": index + 1,
            "from": edge["from"],
            "to": edge["to"],
            "edge": edge_name(edge),
            "flow": capacity[edge["from"]][edge["to"]] - residual[edge["from"]][edge["to"]],
            "capacity": edge["capacity"],
        }
        for index, edge in enumerate(EDGES)
    ]

    return {
        "maxFlow": max_flow,
        "augmentingPaths": augmenting_paths,
        "finalFlow": final_flow,
        "capacity": capacity,
        "residual": residual,
    }


def verify(result: dict[str, object]) -> None:
    assert result["maxFlow"] == 10, f"Expected max flow 10, received {result['maxFlow']}"
    augmenting_paths = result["augmentingPaths"]
    final_flow = result["finalFlow"]
    assert len(augmenting_paths) == len(EXPECTED_PATHS), "Unexpected augmenting path count"

    for index, expected in enumerate(EXPECTED_PATHS):
        actual = augmenting_paths[index]
        assert actual["theta"] == expected["theta"], f"Unexpected theta at step {index + 1}"
        assert actual["vertices"] == expected["path"], f"Unexpected augmenting path at step {index + 1}: {actual['path']}"

    for row in final_flow:
        assert row["flow"] >= 0, f"Negative flow on {row['edge']}"
        assert row["flow"] <= row["capacity"], f"Capacity exceeded on {row['edge']}"

    for vertex in range(2, 13):
        inflow = sum(row["flow"] for row in final_flow if row["to"] == vertex)
        outflow = sum(row["flow"] for row in final_flow if row["from"] == vertex)
        assert inflow == outflow, f"Flow conservation failed at X{vertex}: in={inflow}, out={outflow}"

    for from_vertex, to_vertex in [(9, 13), (10, 13), (11, 13), (12, 13)]:
        row = next(
            item
            for item in final_flow
            if item["from"] == from_vertex and item["to"] == to_vertex
        )
        assert row["flow"] == row["capacity"], f"{vertex_name(from_vertex)}->{vertex_name(to_vertex)} is not saturated"

    source_out = sum(row["flow"] for row in final_flow if row["from"] == SOURCE)
    sink_in = sum(row["flow"] for row in final_flow if row["to"] == SINK)
    assert source_out == result["maxFlow"], "Source outgoing flow differs from max flow"
    assert sink_in == result["maxFlow"], "Sink incoming flow differs from max flow"


def write_artifacts(result: dict[str, object]) -> None:
    payload = {
        "practicalWork": 8,
        "variant": VARIANT,
        "source": vertex_name(SOURCE),
        "sink": vertex_name(SINK),
        "maxFlow": result["maxFlow"],
        "augmentingPaths": result["augmentingPaths"],
        "finalFlow": result["finalFlow"],
        "upperBoundCut": {
            "left": [vertex_name(index + 1) for index in range(12)],
            "right": [vertex_name(13)],
            "capacity": 10,
            "cutArcs": ["X9 -> X13", "X10 -> X13", "X11 -> X13", "X12 -> X13"],
        },
    }
    (OUT_DIR / "variant14_results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    text = "\n".join(
        [
            "Практична робота №8. Варіант №14",
            "Максимальний потік у мережі",
            "",
            f"Джерело: {vertex_name(SOURCE)}",
            f"Стік: {vertex_name(SINK)}",
            f"Максимальний потік: {result['maxFlow']}",
            "",
            "Збільшувальні шляхи:",
            *[
                f"{row['step']}. {row['path']}; theta={row['theta']}; F={row['flowAfterStep']}"
                for row in result["augmentingPaths"]
            ],
            "",
            "Фінальний потік:",
            *[
                f"{row['edge']}: {row['flow']}/{row['capacity']}"
                for row in result["finalFlow"]
            ],
            "",
            "Перевірка оптимальності: розріз {X1..X12} | {X13} має місткість 10.",
            "",
        ]
    )
    (OUT_DIR / "variant14_results.txt").write_text(text, encoding="utf-8")


def main() -> None:
    result = edmonds_karp()
    verify(result)
    write_artifacts(result)
    print(f"PR8 variant {VARIANT}: max flow = {result['maxFlow']}")
    print(f"Augmenting paths: {len(result['augmentingPaths'])}")


if __name__ == "__main__":
    main()
