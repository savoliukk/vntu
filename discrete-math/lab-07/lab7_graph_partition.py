from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


OUT_DIR = Path(os.path.relpath(Path(__file__).parent, Path.cwd()))


# Variant 6 from Table 1 of Lab 7. Every listed adjacency pair is treated as
# an undirected edge because the lab formulates the task for graph edges.
ADJACENCY_FROM_TABLE: dict[int, list[int]] = {
    1: [2, 3, 4, 5, 6, 7, 11, 12],
    2: [1, 3, 4, 5, 6, 7, 8],
    3: [1, 2, 4, 5, 7, 8, 9, 13],
    4: [1, 2, 3, 5, 8, 9, 10, 14],
    5: [1, 2, 3, 4, 10, 15],
    6: [1, 2, 7, 8, 9, 10, 11],
    7: [1, 2, 3, 6, 8, 9, 10, 12],
    8: [2, 3, 4, 6, 7, 9, 10, 13],
    9: [3, 4, 6, 7, 8, 10, 14],
    10: [4, 5, 6, 7, 8, 9, 15],
    11: [1, 6, 12, 13, 14, 15],
    12: [2, 7, 11, 13, 14, 15],
    13: [3, 8, 11, 12, 14, 15],
    14: [4, 9, 11, 12, 13, 15],
    15: [5, 10, 11, 12, 13, 14],
}

FORBIDDEN = [1, 6, 11]


@dataclass(frozen=True)
class Candidate:
    vertex: int
    rho: int
    aik: int
    delta: int


@dataclass
class StepLog:
    piece_number: int
    chosen: int
    candidates: list[Candidate]


def build_undirected_adjacency(source: dict[int, list[int]]) -> dict[int, set[int]]:
    graph = {vertex: set() for vertex in source}
    for left, neighbours in source.items():
        for right in neighbours:
            if right == left:
                continue
            graph.setdefault(left, set()).add(right)
            graph.setdefault(right, set()).add(left)
    return graph


def edge_list(graph: dict[int, set[int]]) -> list[tuple[int, int]]:
    return sorted((left, right) for left, neighbours in graph.items() for right in neighbours if left < right)


def local_degree(graph: dict[int, set[int]], vertex: int, remaining: set[int]) -> int:
    return len(graph[vertex] & remaining)


def select_candidate(
    graph: dict[int, set[int]],
    piece: list[int],
    remaining: set[int],
    reserved_forbidden: set[int],
) -> tuple[int, list[Candidate]]:
    piece_set = set(piece)
    candidates = set()
    for vertex in piece:
        candidates.update(graph[vertex])
    candidates &= remaining
    candidates -= piece_set
    candidates -= reserved_forbidden

    if not candidates:
        candidates = remaining - piece_set - reserved_forbidden

    candidate_rows = []
    for vertex in sorted(candidates):
        rho = local_degree(graph, vertex, remaining)
        aik = len(graph[vertex] & piece_set)
        candidate_rows.append(Candidate(vertex, rho, aik, rho - aik))

    chosen = min(candidate_rows, key=lambda row: (row.delta, -row.rho, row.vertex)).vertex
    return chosen, candidate_rows


def partition_graph(graph: dict[int, set[int]], forbidden: list[int]) -> tuple[list[list[int]], list[StepLog]]:
    vertices = set(graph)
    piece_count = len(forbidden)
    if len(vertices) % piece_count != 0:
        raise ValueError("The number of vertices must be divisible by the number of forbidden vertices.")

    piece_size = len(vertices) // piece_count
    remaining = set(vertices)
    pieces: list[list[int]] = []
    logs: list[StepLog] = []

    for piece_number, seed in enumerate(forbidden, start=1):
        if seed not in remaining:
            raise ValueError(f"Forbidden vertex x{seed} is already assigned.")
        piece = [seed]
        reserved_forbidden = set(forbidden[piece_number:])

        while len(piece) < piece_size:
            chosen, candidates = select_candidate(graph, piece, remaining, reserved_forbidden)
            piece.append(chosen)
            logs.append(StepLog(piece_number, chosen, candidates))

        pieces.append(piece)
        remaining -= set(piece)

    if remaining:
        raise ValueError(f"Unassigned vertices left: {sorted(remaining)}")
    return pieces, logs


def crossing_edges(edges: list[tuple[int, int]], pieces: list[list[int]]) -> list[tuple[int, int]]:
    membership = {}
    for index, piece in enumerate(pieces, start=1):
        for vertex in piece:
            membership[vertex] = index
    return [edge for edge in edges if membership[edge[0]] != membership[edge[1]]]


def format_candidate_table(candidates: list[Candidate]) -> str:
    return "; ".join(
        f"x{row.vertex}: rho={row.rho}, a={row.aik}, delta={row.delta}"
        for row in candidates
    )


def write_results(
    graph: dict[int, set[int]],
    edges: list[tuple[int, int]],
    pieces: list[list[int]],
    logs: list[StepLog],
    cuts: list[tuple[int, int]],
) -> None:
    lines: list[str] = []
    lines.append("Лабораторна робота №7. Варіант 6")
    lines.append("Задача: розріз графа на рівні шматки послідовним алгоритмом.")
    lines.append("")
    lines.append(f"Заборонені вершини Q: {', '.join(f'x{item}' for item in FORBIDDEN)}")
    lines.append(f"Кількість вершин: {len(graph)}")
    lines.append(f"Кількість шматків: {len(FORBIDDEN)}")
    lines.append(f"Розмір одного шматка: {len(graph) // len(FORBIDDEN)}")
    lines.append(f"Кількість ребер після усунення дублікатів: {len(edges)}")
    lines.append("")
    lines.append("Список суміжності, використаний у програмі:")
    for vertex in sorted(graph):
        lines.append(f"x{vertex}: " + ", ".join(f"x{item}" for item in sorted(graph[vertex])))
    lines.append("")
    lines.append("Покрокове виконання:")
    for log in logs:
        lines.append(f"Шматок G{log.piece_number}: обрано x{log.chosen}")
        lines.append("  Кандидати: " + format_candidate_table(log.candidates))
    lines.append("")
    lines.append("Отримані шматки:")
    for index, piece in enumerate(pieces, start=1):
        lines.append(f"G{index}: " + ", ".join(f"x{vertex}" for vertex in piece))
    lines.append("")
    lines.append(f"Кількість ребер у розрізі: {len(cuts)}")
    lines.append("Ребра розрізу: " + ", ".join(f"(x{left}, x{right})" for left, right in cuts))
    lines.append("")
    (OUT_DIR / "lab7_results.txt").write_text("\n".join(lines), encoding="utf-8")


def node_positions() -> dict[int, tuple[int, int]]:
    return {
        1: (130, 130),
        2: (270, 80),
        3: (410, 80),
        4: (550, 80),
        5: (690, 130),
        6: (190, 290),
        7: (330, 245),
        8: (470, 245),
        9: (610, 245),
        10: (750, 290),
        11: (210, 470),
        12: (350, 520),
        13: (490, 520),
        14: (630, 520),
        15: (770, 470),
    }


def write_svg(edges: list[tuple[int, int]], pieces: list[list[int]], cuts: list[tuple[int, int]]) -> None:
    positions = node_positions()
    colors = ["#4f86c6", "#2f9d78", "#d9822b"]
    membership = {}
    for index, piece in enumerate(pieces):
        for vertex in piece:
            membership[vertex] = index

    cut_set = {tuple(sorted(edge)) for edge in cuts}
    svg: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="620" viewBox="0 0 920 620">',
        '<rect width="920" height="620" fill="#ffffff"/>',
        '<style>text{font-family:Arial,sans-serif}.label{font-size:16px;font-weight:700;fill:#1f2933}.legend{font-size:14px;fill:#1f2933}</style>',
    ]

    for left, right in edges:
        x1, y1 = positions[left]
        x2, y2 = positions[right]
        if tuple(sorted((left, right))) in cut_set:
            svg.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                'stroke="#c23030" stroke-width="2.4" stroke-dasharray="7 5" opacity="0.9"/>'
            )
        else:
            svg.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                'stroke="#9aa5b1" stroke-width="1.4" opacity="0.42"/>'
            )

    for vertex in sorted(positions):
        x, y = positions[vertex]
        fill = colors[membership[vertex]]
        svg.append(f'<circle cx="{x}" cy="{y}" r="24" fill="{fill}" stroke="#1f2933" stroke-width="1.5"/>')
        svg.append(f'<text x="{x}" y="{y + 6}" text-anchor="middle" class="label">x{vertex}</text>')

    legend_x = 35
    legend_y = 575
    for index, color in enumerate(colors, start=1):
        x = legend_x + (index - 1) * 180
        svg.append(f'<rect x="{x}" y="{legend_y - 16}" width="24" height="16" rx="3" fill="{color}"/>')
        svg.append(f'<text x="{x + 32}" y="{legend_y - 3}" class="legend">G{index}</text>')
    svg.append('<line x1="600" y1="570" x2="655" y2="570" stroke="#c23030" stroke-width="2.4" stroke-dasharray="7 5"/>')
    svg.append('<text x="665" y="575" class="legend">ребро розрізу</text>')
    svg.append("</svg>")
    (OUT_DIR / "variant6_partition.svg").write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    graph = build_undirected_adjacency(ADJACENCY_FROM_TABLE)
    edges = edge_list(graph)
    pieces, logs = partition_graph(graph, FORBIDDEN)
    cuts = crossing_edges(edges, pieces)
    write_results(graph, edges, pieces, logs, cuts)
    write_svg(edges, pieces, cuts)

    print("Pieces:")
    for index, piece in enumerate(pieces, start=1):
        print(f"G{index}: {piece}")
    print(f"Cut edges: {len(cuts)}")


if __name__ == "__main__":
    main()
