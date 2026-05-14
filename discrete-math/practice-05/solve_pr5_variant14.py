from __future__ import annotations

import json
from collections import deque
import os
from pathlib import Path


OUT_DIR = Path(os.path.relpath(Path(__file__).parent, Path.cwd()))


def edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def edge_key(item: tuple[int, int]) -> str:
    return f"{min(item)}-{max(item)}"


def unique_edges(edges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    seen = set()
    result = []
    for item in [edge(a, b) for a, b in edges]:
        key = edge_key(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return sorted(result)


def adjacency(edges: list[tuple[int, int]]) -> dict[int, list[int]]:
    adj: dict[int, list[int]] = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    for values in adj.values():
        values.sort()
    return adj


def component_count(vertices: list[int], edges: list[tuple[int, int]]) -> int:
    adj = adjacency(edges)
    seen = set()
    components = 0
    for start in vertices:
        if start in seen:
            continue
        components += 1
        stack = [start]
        seen.add(start)
        while stack:
            vertex = stack.pop()
            for next_vertex in adj.get(vertex, []):
                if next_vertex not in seen:
                    seen.add(next_vertex)
                    stack.append(next_vertex)
    return components


def path_in_tree(tree_edges: list[tuple[int, int]], start: int, finish: int) -> list[int]:
    adj = adjacency(tree_edges)
    queue = deque([start])
    previous: dict[int, int | None] = {start: None}
    while queue:
        vertex = queue.popleft()
        if vertex == finish:
            break
        for next_vertex in adj.get(vertex, []):
            if next_vertex not in previous:
                previous[next_vertex] = vertex
                queue.append(next_vertex)
    if finish not in previous:
        raise ValueError(f"No tree path from X{start} to X{finish}")
    result = []
    current: int | None = finish
    while current is not None:
        result.append(current)
        current = previous[current]
    return list(reversed(result))


def fundamental_cycles(
    edges: list[tuple[int, int]], tree_edges: list[tuple[int, int]]
) -> list[dict[str, object]]:
    tree_keys = {edge_key(item) for item in tree_edges}
    result = []
    for item in edges:
        if edge_key(item) in tree_keys:
            continue
        a, b = item
        tree_path = path_in_tree(tree_edges, a, b)
        result.append({"chord": [a, b], "treePath": tree_path, "cycle": [*tree_path, a]})
    return result


def kruskal(vertices: list[int], weighted_edges: list[dict[str, int]]) -> dict[str, object]:
    parent = {vertex: vertex for vertex in vertices}
    rank = {vertex: 0 for vertex in vertices}

    def find(vertex: int) -> int:
        if parent[vertex] != vertex:
            parent[vertex] = find(parent[vertex])
        return parent[vertex]

    def union(a: int, b: int) -> bool:
        pa, pb = find(a), find(b)
        if pa == pb:
            return False
        if rank[pa] < rank[pb]:
            parent[pa] = pb
        elif rank[pa] > rank[pb]:
            parent[pb] = pa
        else:
            parent[pb] = pa
            rank[pa] += 1
        return True

    sorted_edges = sorted(weighted_edges, key=lambda item: (item["w"], item["a"], item["b"]))
    selected = []
    trace = []
    for item in sorted_edges:
        accepted = union(item["a"], item["b"])
        if accepted:
            selected.append(item)
        trace.append(
            {
                "edge": [item["a"], item["b"]],
                "weight": item["w"],
                "action": "додати" if accepted else "не додавати",
                "reason": "цикл не утворюється" if accepted else "утворюється цикл",
            }
        )
        if len(selected) == len(vertices) - 1:
            break
    return {
        "edges": selected,
        "total": sum(item["w"] for item in selected),
        "trace": trace,
        "sorted": sorted_edges,
    }


def assert_spanning_tree(vertices: list[int], tree_edges: list[tuple[int, int]]) -> None:
    if len(tree_edges) != len(vertices) - 1:
        raise ValueError(f"Tree has {len(tree_edges)} edges, expected {len(vertices) - 1}")
    if component_count(vertices, tree_edges) != 1:
        raise ValueError("Tree is not connected")


def format_edge(item: tuple[int, int] | list[int]) -> str:
    a, b = item
    return f"X{a}X{b}"


def format_cycle(cycle: list[int]) -> str:
    return " - ".join(f"X{vertex}" for vertex in cycle)


def main() -> None:
    table_vertices = [1, 2, 3, 4, 5, 6]
    table_edges = unique_edges([(1, 3), (1, 5), (1, 6), (2, 3), (2, 4), (2, 5), (3, 6), (4, 5)])
    table_tree = unique_edges([(1, 3), (1, 5), (1, 6), (2, 3), (2, 4)])
    weighted_table_edges = [
        {"a": 1, "b": 3, "w": 1},
        {"a": 1, "b": 5, "w": 3},
        {"a": 1, "b": 6, "w": 2},
        {"a": 2, "b": 3, "w": 2},
        {"a": 2, "b": 4, "w": 3},
        {"a": 2, "b": 5, "w": 3},
        {"a": 3, "b": 6, "w": 2},
        {"a": 4, "b": 5, "w": 5},
    ]
    fig2_vertices = list(range(1, 14))
    fig2_edges = unique_edges([
        (1, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 5), (3, 7), (4, 6),
        (4, 7), (4, 8), (5, 9), (5, 11), (6, 10), (6, 12), (7, 9),
        (7, 10), (8, 11), (8, 12), (9, 13), (10, 13), (11, 13), (12, 13),
    ])
    fig3_vertices = list(range(1, 10))
    fig3_edges = unique_edges([
        (1, 2), (1, 4), (1, 5), (1, 7), (2, 3), (2, 4), (2, 8), (2, 9),
        (3, 6), (3, 8), (3, 9), (4, 7), (4, 8), (5, 6), (5, 7), (5, 8),
        (6, 8), (7, 8), (8, 9),
    ])
    fig3_tree = unique_edges([(1, 2), (1, 4), (1, 5), (1, 7), (2, 3), (5, 6), (7, 8), (8, 9)])

    assert_spanning_tree(table_vertices, table_tree)
    assert_spanning_tree(fig3_vertices, fig3_tree)

    table_components = component_count(table_vertices, table_edges)
    fig2_components = component_count(fig2_vertices, fig2_edges)
    fig3_components = component_count(fig3_vertices, fig3_edges)
    table_cycles = fundamental_cycles(table_edges, table_tree)
    fig3_cycles = fundamental_cycles(fig3_edges, fig3_tree)
    mst = kruskal(table_vertices, weighted_table_edges)
    if len(mst["edges"]) != len(table_vertices) - 1:
        raise ValueError("Kruskal did not build a full spanning tree")

    result = {
        "variant": 14,
        "tableGraph": {
            "vertices": len(table_vertices),
            "edgeCount": len(table_edges),
            "components": table_components,
            "cyclomaticNumber": len(table_edges) - len(table_vertices) + table_components,
            "edgeList": [format_edge(item) for item in table_edges],
            "spanningTree": [format_edge(item) for item in table_tree],
            "fundamentalCycles": [
                {
                    "chord": format_edge(item["chord"]),
                    "treePath": format_cycle(item["treePath"]),
                    "cycle": format_cycle(item["cycle"]),
                }
                for item in table_cycles
            ],
        },
        "minimumSpanningTree": {
            "weightedEdges": [
                {"edge": format_edge((item["a"], item["b"])), "weight": item["w"]}
                for item in weighted_table_edges
            ],
            "sortedEdges": [
                {"edge": format_edge((item["a"], item["b"])), "weight": item["w"]}
                for item in mst["sorted"]
            ],
            "trace": [
                {
                    "step": index + 1,
                    "edge": format_edge(item["edge"]),
                    "weight": item["weight"],
                    "action": item["action"],
                    "reason": item["reason"],
                }
                for index, item in enumerate(mst["trace"])
            ],
            "edges": [
                {"edge": format_edge((item["a"], item["b"])), "weight": item["w"]}
                for item in mst["edges"]
            ],
            "totalWeight": mst["total"],
        },
        "figure2": {
            "vertices": len(fig2_vertices),
            "edgeCount": len(fig2_edges),
            "components": fig2_components,
            "cyclomaticNumber": len(fig2_edges) - len(fig2_vertices) + fig2_components,
            "edgeList": [format_edge(item) for item in fig2_edges],
        },
        "figure3": {
            "vertices": len(fig3_vertices),
            "edgeCount": len(fig3_edges),
            "components": fig3_components,
            "cyclomaticNumber": len(fig3_edges) - len(fig3_vertices) + fig3_components,
            "edgeList": [format_edge(item) for item in fig3_edges],
            "spanningTree": [format_edge(item) for item in fig3_tree],
            "fundamentalCycles": [
                {
                    "chord": format_edge(item["chord"]),
                    "treePath": format_cycle(item["treePath"]),
                    "cycle": format_cycle(item["cycle"]),
                }
                for item in fig3_cycles
            ],
        },
    }

    mst_edges_summary = ", ".join(
        f"{item['edge']}({item['weight']})"
        for item in result["minimumSpanningTree"]["edges"]
    )

    summary = "\n".join(
        [
            "Практична робота 5, варіант 14",
            "",
            f"Граф з таблиці 1: n={result['tableGraph']['vertices']}, m={result['tableGraph']['edgeCount']}, p={result['tableGraph']['components']}, ν={result['tableGraph']['cyclomaticNumber']}",
            f"Остов таблиці 1: {', '.join(result['tableGraph']['spanningTree'])}",
            f"Мінімальний остов: {mst_edges_summary}, сума={result['minimumSpanningTree']['totalWeight']}",
            f"Рисунок 2: n={result['figure2']['vertices']}, m={result['figure2']['edgeCount']}, p={result['figure2']['components']}, ν={result['figure2']['cyclomaticNumber']}",
            f"Рисунок 3: n={result['figure3']['vertices']}, m={result['figure3']['edgeCount']}, p={result['figure3']['components']}, ν={result['figure3']['cyclomaticNumber']}",
            "",
            "Фундаментальні цикли графа з таблиці 1:",
            *[
                f"{index + 1}. {item['cycle']} (хорда {item['chord']})"
                for index, item in enumerate(result["tableGraph"]["fundamentalCycles"])
            ],
            "",
            "Фундаментальні цикли графа з рисунка 3:",
            *[
                f"{index + 1}. {item['cycle']} (хорда {item['chord']})"
                for index, item in enumerate(result["figure3"]["fundamentalCycles"])
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
