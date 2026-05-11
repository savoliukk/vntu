from __future__ import annotations

import heapq
from collections import deque
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
START = "x1"
FINISH = "x14"
INF = 10**9


# Variant 18. The first number on each edge is used as the length.
# The number in parentheses belongs to flow-capacity tasks and is not used here.
EDGES = [
    ("x1", "x2", 3),
    ("x1", "x3", 2),
    ("x1", "x4", 2),
    ("x1", "x5", 3),
    ("x1", "x6", 4),
    ("x2", "x7", 2),
    ("x2", "x8", 1),
    ("x3", "x8", 1),
    ("x4", "x7", 2),
    ("x4", "x9", 3),
    ("x5", "x10", 1),
    ("x5", "x11", 2),
    ("x6", "x9", 1),
    ("x6", "x10", 2),
    ("x7", "x11", 2),
    ("x7", "x12", 2),
    ("x8", "x13", 3),
    ("x9", "x11", 1),
    ("x9", "x12", 1),
    ("x9", "x13", 1),
    ("x10", "x12", 3),
    ("x10", "x13", 4),
    ("x11", "x14", 3),
    ("x12", "x14", 6),
    ("x13", "x14", 3),
]

POSITIONS = {
    "x1": (70, 285),
    "x2": (170, 80),
    "x3": (205, 170),
    "x4": (215, 270),
    "x5": (245, 355),
    "x6": (290, 520),
    "x7": (610, 70),
    "x8": (455, 210),
    "x9": (455, 330),
    "x10": (640, 520),
    "x11": (820, 195),
    "x12": (760, 290),
    "x13": (810, 450),
    "x14": (940, 290),
}


def nodes() -> list[str]:
    return [f"x{i}" for i in range(1, 15)]


def build_graph() -> dict[str, list[tuple[str, int]]]:
    graph = {node: [] for node in nodes()}
    for left, right, weight in EDGES:
        graph[left].append((right, weight))
        graph[right].append((left, weight))
    for value in graph.values():
        value.sort(key=lambda item: int(item[0][1:]))
    return graph


def format_distances(distances: dict[str, int]) -> str:
    values = []
    for node in nodes():
        value = distances[node]
        values.append("∞" if value >= INF else str(value))
    return ", ".join(values)


def weighted_wave(graph: dict[str, list[tuple[str, int]]]) -> tuple[dict[str, int], dict[str, set[str]], list[dict[str, str]]]:
    distances = {node: INF for node in nodes()}
    parents = {node: set() for node in nodes()}
    distances[START] = 0
    queue: deque[str] = deque([START])
    in_queue = {START}
    log: list[dict[str, str]] = [
        {
            "step": "0",
            "vertex": "-",
            "updates": f"{START}=0",
            "queue": ", ".join(queue),
            "distances": format_distances(distances),
        }
    ]
    step = 0

    while queue:
        current = queue.popleft()
        in_queue.discard(current)
        updates: list[str] = []
        for neighbor, weight in graph[current]:
            candidate = distances[current] + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                parents[neighbor] = {current}
                updates.append(f"{neighbor}={candidate} через {current}")
                if neighbor not in in_queue:
                    queue.append(neighbor)
                    in_queue.add(neighbor)
            elif candidate == distances[neighbor] and current not in parents[neighbor] and neighbor != START:
                parents[neighbor].add(current)
                updates.append(f"{neighbor}={candidate}: додано попередник {current}")
        step += 1
        log.append(
            {
                "step": str(step),
                "vertex": current,
                "updates": "; ".join(updates) if updates else "-",
                "queue": ", ".join(queue) if queue else "∅",
                "distances": format_distances(distances),
            }
        )

    return distances, parents, log


def dijkstra(graph: dict[str, list[tuple[str, int]]]) -> tuple[dict[str, int], dict[str, set[str]], list[dict[str, str]]]:
    distances = {node: INF for node in nodes()}
    parents = {node: set() for node in nodes()}
    used: set[str] = set()
    distances[START] = 0
    heap: list[tuple[int, int, str]] = [(0, 1, START)]
    log: list[dict[str, str]] = []
    step = 0

    while heap:
        distance, _, current = heapq.heappop(heap)
        if current in used:
            continue
        used.add(current)
        updates: list[str] = []
        for neighbor, weight in graph[current]:
            if neighbor in used:
                continue
            candidate = distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                parents[neighbor] = {current}
                heapq.heappush(heap, (candidate, int(neighbor[1:]), neighbor))
                updates.append(f"{neighbor}={candidate} через {current}")
            elif candidate == distances[neighbor]:
                parents[neighbor].add(current)
                updates.append(f"{neighbor}={candidate}: додано попередник {current}")
        step += 1
        log.append(
            {
                "step": str(step),
                "vertex": current,
                "updates": "; ".join(updates) if updates else "-",
                "fixed": ", ".join(sorted(used, key=lambda item: int(item[1:]))),
                "distances": format_distances(distances),
            }
        )
        if current == FINISH:
            break

    return distances, parents, log


def shortest_paths(parents: dict[str, set[str]], node: str = FINISH) -> list[list[str]]:
    if node == START:
        return [[START]]
    result: list[list[str]] = []
    for parent in sorted(parents[node], key=lambda item: int(item[1:])):
        for path in shortest_paths(parents, parent):
            result.append([*path, node])
    return result


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    align = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, align, *body])


def edge_list_table() -> str:
    rows = [[left, right, str(weight)] for left, right, weight in EDGES]
    return markdown_table(["Вершина 1", "Вершина 2", "Довжина"], rows)


def log_table(log: list[dict[str, str]], algorithm: str) -> str:
    if algorithm == "wave":
        rows = [[item["step"], item["vertex"], item["updates"], item["queue"], item["distances"]] for item in log]
        return markdown_table(["Крок", "Вершина", "Оновлення", "M", "V(x1)..V(x14)"], rows)
    rows = [[item["step"], item["vertex"], item["updates"], item["fixed"], item["distances"]] for item in log]
    return markdown_table(["Крок", "Обрана вершина", "Оновлення", "Зафіксовані", "V(x1)..V(x14)"], rows)


def write_graph_svg(path: Path, shortest: list[str]) -> None:
    path_edges = {tuple(sorted((a, b), key=lambda item: int(item[1:]))) for a, b in zip(shortest, shortest[1:])}
    width, height = 1040, 610
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,Helvetica,sans-serif;fill:#172033}",
        ".node{fill:#ffffff;stroke:#172033;stroke-width:2}",
        ".edge{stroke:#5a6578;stroke-width:2.2}",
        ".path{stroke:#d92727;stroke-width:4}",
        ".label{font-size:13px;font-weight:700;paint-order:stroke;stroke:#fff;stroke-width:4px;stroke-linejoin:round}",
        ".nodeText{font-size:15px;font-weight:700}",
        "</style>",
        '<text x="28" y="28" class="nodeText">Варіант 18: найкоротший шлях x1 → x14</text>',
    ]

    for left, right, weight in EDGES:
        x1, y1 = POSITIONS[left]
        x2, y2 = POSITIONS[right]
        key = tuple(sorted((left, right), key=lambda item: int(item[1:])))
        cls = "path" if key in path_edges else "edge"
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"/>')
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        parts.append(f'<text x="{mx}" y="{my - 5}" text-anchor="middle" class="label">{weight}</text>')

    for node, (x, y) in POSITIONS.items():
        parts.append(f'<circle cx="{x}" cy="{y}" r="15" class="node"/>')
        parts.append(f'<text x="{x}" y="{y + 5}" text-anchor="middle" class="nodeText">{node}</text>')

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    graph = build_graph()
    wave_distances, wave_parents, wave_log = weighted_wave(graph)
    dijkstra_distances, dijkstra_parents, dijkstra_log = dijkstra(graph)
    wave_paths = shortest_paths(wave_parents)
    dijkstra_paths = shortest_paths(dijkstra_parents)
    selected_path = dijkstra_paths[0]
    write_graph_svg(OUT_DIR / "variant18_shortest_path.svg", selected_path)

    results = "\n\n".join(
        [
            "ЛР5. Найкоротший шлях у графі",
            "Варіант 18",
            f"Початкова вершина: {START}; кінцева вершина: {FINISH}",
            "Список ребер:",
            edge_list_table(),
            "Хвильовий алгоритм для зваженого графа:",
            log_table(wave_log, "wave"),
            f"Найкоротша довжина хвильовим алгоритмом: {wave_distances[FINISH]}",
            "Найкоротші маршрути хвильовим алгоритмом:",
            "\n".join(" -> ".join(path) for path in wave_paths),
            "Алгоритм Дейкстри:",
            log_table(dijkstra_log, "dijkstra"),
            f"Найкоротша довжина алгоритмом Дейкстри: {dijkstra_distances[FINISH]}",
            "Найкоротші маршрути алгоритмом Дейкстри:",
            "\n".join(" -> ".join(path) for path in dijkstra_paths),
        ]
    )
    (OUT_DIR / "lab5_results.txt").write_text(results + "\n", encoding="utf-8")
    print(results)


if __name__ == "__main__":
    main()
