from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Arc:
    start: str
    end: str
    label: str
    capacity: int


@dataclass
class Augmentation:
    path: list[str]
    bottleneck: int
    residuals: list[int]


# Variant 5 from Lab 5. For a label a(b), b is used as capacity.
# If a label has no parentheses, the only visible number is used.
ARCS = [
    Arc("x1", "x2", "5(3)", 3),
    Arc("x1", "x3", "5(3)", 3),
    Arc("x1", "x4", "3(3)", 3),
    Arc("x2", "x5", "2(2)", 2),
    Arc("x2", "x9", "3(1)", 1),
    Arc("x3", "x5", "2(2)", 2),
    Arc("x3", "x6", "2(1)", 1),
    Arc("x3", "x7", "7", 7),
    Arc("x4", "x6", "3(3)", 3),
    Arc("x4", "x7", "2", 2),
    Arc("x5", "x8", "4(4)", 4),
    Arc("x6", "x8", "2(2)", 2),
    Arc("x6", "x9", "1(1)", 1),
    Arc("x6", "x10", "1(1)", 1),
    Arc("x7", "x10", "3", 3),
    Arc("x8", "x11", "4(4)", 4),
    Arc("x8", "x14", "5(2)", 2),
    Arc("x9", "x11", "2", 2),
    Arc("x9", "x12", "2(2)", 2),
    Arc("x10", "x12", "2", 2),
    Arc("x10", "x13", "1(1)", 1),
    Arc("x11", "x14", "4(4)", 4),
    Arc("x12", "x14", "5(2)", 2),
    Arc("x13", "x14", "2(1)", 1),
]

SOURCE = "x1"
SINK = "x14"


def vertices() -> list[str]:
    ordered = sorted({arc.start for arc in ARCS} | {arc.end for arc in ARCS}, key=lambda item: int(item[1:]))
    return ordered


def build_residual() -> tuple[dict[str, dict[str, int]], dict[tuple[str, str], int], dict[str, list[str]]]:
    residual = {vertex: {} for vertex in vertices()}
    original = {}
    adjacency = {vertex: [] for vertex in vertices()}

    for arc in ARCS:
        residual[arc.start][arc.end] = residual[arc.start].get(arc.end, 0) + arc.capacity
        residual[arc.end].setdefault(arc.start, 0)
        original[(arc.start, arc.end)] = original.get((arc.start, arc.end), 0) + arc.capacity
        if arc.end not in adjacency[arc.start]:
            adjacency[arc.start].append(arc.end)
        if arc.start not in adjacency[arc.end]:
            adjacency[arc.end].append(arc.start)

    return residual, original, adjacency


def find_augmenting_path(
    residual: dict[str, dict[str, int]],
    adjacency: dict[str, list[str]],
) -> tuple[list[str], list[int]] | None:
    parent: dict[str, str | None] = {SOURCE: None}
    queue: deque[str] = deque([SOURCE])

    while queue:
        current = queue.popleft()
        for neighbour in adjacency[current]:
            if neighbour not in parent and residual[current].get(neighbour, 0) > 0:
                parent[neighbour] = current
                if neighbour == SINK:
                    path = [SINK]
                    while path[-1] != SOURCE:
                        path.append(parent[path[-1]])  # type: ignore[arg-type]
                    path.reverse()
                    residuals = [residual[path[index]][path[index + 1]] for index in range(len(path) - 1)]
                    return path, residuals
                queue.append(neighbour)

    return None


def ford_fulkerson() -> tuple[int, dict[tuple[str, str], int], list[Augmentation], set[str], list[Arc]]:
    residual, original, adjacency = build_residual()
    augmentations: list[Augmentation] = []

    while True:
        found = find_augmenting_path(residual, adjacency)
        if found is None:
            break
        path, residuals = found
        bottleneck = min(residuals)
        augmentations.append(Augmentation(path=path, bottleneck=bottleneck, residuals=residuals))

        for index in range(len(path) - 1):
            start = path[index]
            end = path[index + 1]
            residual[start][end] -= bottleneck
            residual[end][start] = residual[end].get(start, 0) + bottleneck

    flows = {}
    for edge, capacity in original.items():
        start, end = edge
        flows[edge] = capacity - residual[start][end]

    reachable = reachable_vertices(residual, adjacency)
    min_cut = [arc for arc in ARCS if arc.start in reachable and arc.end not in reachable]
    value = sum(flows[(SOURCE, arc.end)] for arc in ARCS if arc.start == SOURCE)
    return value, flows, augmentations, reachable, min_cut


def reachable_vertices(residual: dict[str, dict[str, int]], adjacency: dict[str, list[str]]) -> set[str]:
    reached = {SOURCE}
    queue: deque[str] = deque([SOURCE])
    while queue:
        current = queue.popleft()
        for neighbour in adjacency[current]:
            if neighbour not in reached and residual[current].get(neighbour, 0) > 0:
                reached.add(neighbour)
                queue.append(neighbour)
    return reached


def path_to_text(path: list[str]) -> str:
    return " -> ".join(path)


def write_results(
    value: int,
    flows: dict[tuple[str, str], int],
    augmentations: list[Augmentation],
    reachable: set[str],
    min_cut: list[Arc],
) -> None:
    lines: list[str] = []
    lines.append("Лабораторна робота №8. Варіант 5")
    lines.append("Алгоритм Форда-Фалкерсона для пошуку максимального потоку.")
    lines.append("")
    lines.append(f"Джерело: {SOURCE}")
    lines.append(f"Стік: {SINK}")
    lines.append("")
    lines.append("Вхідні дуги:")
    for arc in ARCS:
        lines.append(f"{arc.start} -> {arc.end}: підпис {arc.label}, r={arc.capacity}")
    lines.append("")
    lines.append("Ітерації збільшення потоку:")
    for index, augmentation in enumerate(augmentations, start=1):
        residual_text = ", ".join(str(item) for item in augmentation.residuals)
        lines.append(
            f"{index}. {path_to_text(augmentation.path)}; "
            f"залишкові спроможності: [{residual_text}]; theta={augmentation.bottleneck}"
        )
    lines.append("")
    lines.append("Фінальні потоки x_ij / r_ij:")
    for arc in ARCS:
        flow = flows[(arc.start, arc.end)]
        lines.append(f"{arc.start} -> {arc.end}: {flow}/{arc.capacity}")
    lines.append("")
    lines.append(f"Максимальний потік: {value}")
    lines.append("Позначені вершини в останній ітерації: " + ", ".join(sorted(reachable, key=lambda item: int(item[1:]))))
    lines.append("Мінімальний розріз: " + ", ".join(f"({arc.start}, {arc.end})" for arc in min_cut))
    lines.append("Пропускна спроможність мінімального розрізу: " + str(sum(arc.capacity for arc in min_cut)))
    (OUT_DIR / "lab8_results.txt").write_text("\n".join(lines), encoding="utf-8")


def node_positions() -> dict[str, tuple[int, int]]:
    return {
        "x1": (70, 315),
        "x2": (205, 105),
        "x3": (210, 300),
        "x4": (250, 530),
        "x5": (390, 105),
        "x6": (425, 300),
        "x7": (430, 530),
        "x8": (590, 105),
        "x9": (625, 295),
        "x10": (650, 530),
        "x11": (790, 190),
        "x12": (790, 370),
        "x13": (805, 530),
        "x14": (930, 315),
    }


def write_svg(value: int, flows: dict[tuple[str, str], int], min_cut: list[Arc]) -> None:
    positions = node_positions()
    cut_edges = {(arc.start, arc.end) for arc in min_cut}
    saturated_edges = {edge for edge, flow in flows.items() if flow > 0}
    svg: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="620" viewBox="0 0 1000 620">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,4 L0,8 z" fill="#40556f"/></marker><marker id="arrowRed" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,4 L0,8 z" fill="#c23030"/></marker></defs>',
        '<rect width="1000" height="620" fill="#ffffff"/>',
        '<style>text{font-family:Arial,sans-serif}.node{font-size:16px;font-weight:700;fill:#111827}.edge{font-size:13px;fill:#111827}.title{font-size:18px;font-weight:700;fill:#111827}.small{font-size:13px;fill:#334155}</style>',
        f'<text x="35" y="34" class="title">Варіант 5: максимальний потік d* = {value}</text>',
    ]

    for arc in ARCS:
        x1, y1 = positions[arc.start]
        x2, y2 = positions[arc.end]
        is_cut = (arc.start, arc.end) in cut_edges
        stroke = "#c23030" if is_cut else "#40556f"
        width = "3.2" if (arc.start, arc.end) in saturated_edges else "1.7"
        dash = ' stroke-dasharray="7 5"' if is_cut else ""
        marker = "arrowRed" if is_cut else "arrow"
        svg.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{width}" opacity="0.82"{dash} marker-end="url(#{marker})"/>'
        )

    label_offsets = {
        ("x1", "x2"): (-20, -6),
        ("x1", "x3"): (-18, -12),
        ("x1", "x4"): (-20, 8),
        ("x2", "x9"): (0, -24),
        ("x8", "x14"): (0, -18),
        ("x11", "x14"): (20, -5),
        ("x13", "x14"): (22, 10),
    }
    for arc in ARCS:
        x1, y1 = positions[arc.start]
        x2, y2 = positions[arc.end]
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        dx, dy = label_offsets.get((arc.start, arc.end), (0, -8))
        flow = flows[(arc.start, arc.end)]
        svg.append(
            f'<rect x="{mx + dx - 19}" y="{my + dy - 14}" width="38" height="18" rx="3" fill="#ffffff" opacity="0.82"/>'
        )
        svg.append(f'<text x="{mx + dx}" y="{my + dy}" text-anchor="middle" class="edge">{flow}/{arc.capacity}</text>')

    for vertex, (x, y) in positions.items():
        fill = "#f4c95d" if vertex == SOURCE else "#8fd0a9" if vertex == SINK else "#dbeafe"
        svg.append(f'<circle cx="{x}" cy="{y}" r="23" fill="{fill}" stroke="#111827" stroke-width="1.5"/>')
        svg.append(f'<text x="{x}" y="{y + 6}" text-anchor="middle" class="node">{vertex}</text>')

    svg.append('<line x1="735" y1="575" x2="800" y2="575" stroke="#c23030" stroke-width="3.2" stroke-dasharray="7 5" marker-end="url(#arrowRed)"/>')
    svg.append('<text x="815" y="580" class="small">дуги мінімального розрізу</text>')
    svg.append("</svg>")
    (OUT_DIR / "variant5_max_flow.svg").write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    value, flows, augmentations, reachable, min_cut = ford_fulkerson()
    write_results(value, flows, augmentations, reachable, min_cut)
    write_svg(value, flows, min_cut)
    print(f"Max flow: {value}")
    print("Min cut:", [(arc.start, arc.end, arc.capacity) for arc in min_cut])


if __name__ == "__main__":
    main()
