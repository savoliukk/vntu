from __future__ import annotations

import os
from pathlib import Path


OUT_DIR = Path(os.path.relpath(Path(__file__).parent, Path.cwd()))


# Variant 6 from Lab 5. The first number on each edge is used as the edge weight.
EDGES = [
    ("x1", "x2", 3),
    ("x1", "x3", 3),
    ("x1", "x4", 3),
    ("x1", "x5", 3),
    ("x2", "x6", 2),
    ("x2", "x8", 2),
    ("x3", "x6", 1),
    ("x3", "x7", 2),
    ("x4", "x6", 1),
    ("x4", "x7", 2),
    ("x5", "x7", 1),
    ("x5", "x8", 3),
    ("x6", "x9", 3),
    ("x6", "x10", 2),
    ("x7", "x9", 1),
    ("x7", "x11", 2),
    ("x7", "x12", 1),
    ("x8", "x10", 2),
    ("x8", "x11", 1),
    ("x8", "x12", 3),
    ("x9", "x13", 4),
    ("x10", "x13", 3),
    ("x11", "x13", 4),
    ("x12", "x13", 3),
]

POSITIONS = {
    "x1": (70, 285),
    "x2": (170, 80),
    "x3": (205, 170),
    "x4": (215, 270),
    "x5": (245, 355),
    "x6": (455, 70),
    "x7": (580, 245),
    "x8": (660, 430),
    "x9": (805, 90),
    "x10": (815, 170),
    "x11": (830, 320),
    "x12": (895, 440),
    "x13": (995, 245),
}


class DisjointSet:
    def __init__(self, items: list[str]) -> None:
        self.parent = {item: item for item in items}
        self.rank = {item: 0 for item in items}

    def find(self, item: str) -> str:
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, left: str, right: str) -> bool:
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left == root_right:
            return False
        if self.rank[root_left] < self.rank[root_right]:
            root_left, root_right = root_right, root_left
        self.parent[root_right] = root_left
        if self.rank[root_left] == self.rank[root_right]:
            self.rank[root_left] += 1
        return True


def nodes() -> list[str]:
    return [f"x{i}" for i in range(1, 14)]


def edge_key(edge: tuple[str, str, int]) -> tuple[int, int, int]:
    left, right, weight = edge
    return (weight, int(left[1:]), int(right[1:]))


def build_spanning_tree(edge_order: list[tuple[str, str, int]]) -> tuple[list[tuple[str, str, int]], list[dict[str, str]]]:
    dsu = DisjointSet(nodes())
    tree: list[tuple[str, str, int]] = []
    log: list[dict[str, str]] = []

    for index, (left, right, weight) in enumerate(edge_order, start=1):
        if len(tree) == len(nodes()) - 1:
            break
        accepted = dsu.union(left, right)
        if accepted:
            tree.append((left, right, weight))
        log.append(
            {
                "step": str(index),
                "edge": f"{left}-{right}",
                "weight": str(weight),
                "decision": "включено" if accepted else "відхилено, створює цикл",
                "tree_size": str(len(tree)),
            }
        )
    return tree, log


def total_weight(tree: list[tuple[str, str, int]]) -> int:
    return sum(weight for _, _, weight in tree)


def is_tree(tree: list[tuple[str, str, int]]) -> bool:
    if len(tree) != len(nodes()) - 1:
        return False
    dsu = DisjointSet(nodes())
    return all(dsu.union(left, right) for left, right, _ in tree)


def prufer_code(tree: list[tuple[str, str, int]]) -> list[str]:
    adjacency = {node: set() for node in nodes()}
    for left, right, _ in tree:
        adjacency[left].add(right)
        adjacency[right].add(left)

    code: list[str] = []
    for _ in range(len(nodes()) - 2):
        leaf = min((node for node, neighbors in adjacency.items() if len(neighbors) == 1), key=lambda item: int(item[1:]))
        neighbor = next(iter(adjacency[leaf]))
        code.append(neighbor)
        adjacency[neighbor].remove(leaf)
        adjacency[leaf].clear()
    return code


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    align = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, align, *body])


def edge_rows(edges: list[tuple[str, str, int]]) -> list[list[str]]:
    return [[left, right, str(weight)] for left, right, weight in edges]


def log_rows(log: list[dict[str, str]]) -> list[list[str]]:
    return [[item["step"], item["edge"], item["weight"], item["decision"], item["tree_size"]] for item in log]


def write_graph_svg(path: Path, title: str, selected_edges: list[tuple[str, str, int]]) -> None:
    selected = {tuple(sorted((left, right), key=lambda item: int(item[1:]))) for left, right, _ in selected_edges}
    width, height = 1040, 610
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,Helvetica,sans-serif;fill:#172033}",
        ".node{fill:#ffffff;stroke:#172033;stroke-width:2}",
        ".edge{stroke:#9aa5b5;stroke-width:1.8}",
        ".tree{stroke:#1f7a3f;stroke-width:4}",
        ".label{font-size:13px;font-weight:700;paint-order:stroke;stroke:#fff;stroke-width:4px;stroke-linejoin:round}",
        ".nodeText{font-size:15px;font-weight:700}",
        "</style>",
        f'<text x="28" y="28" class="nodeText">{title}</text>',
    ]

    for left, right, weight in EDGES:
        x1, y1 = POSITIONS[left]
        x2, y2 = POSITIONS[right]
        key = tuple(sorted((left, right), key=lambda item: int(item[1:])))
        cls = "tree" if key in selected else "edge"
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
    arbitrary_tree, arbitrary_log = build_spanning_tree(EDGES)
    mst_edges, mst_log = build_spanning_tree(sorted(EDGES, key=edge_key))

    write_graph_svg(OUT_DIR / "variant6_arbitrary_spanning_tree.svg", "Variant 6: arbitrary spanning tree", arbitrary_tree)
    write_graph_svg(OUT_DIR / "variant6_minimum_spanning_tree.svg", "Variant 6: minimum spanning tree", mst_edges)

    results = "\n\n".join(
        [
            "ЛР6. Побудова стовбура графа",
            "Варіант 6",
            "Список ребер графа:",
            markdown_table(["Вершина 1", "Вершина 2", "Вага"], edge_rows(EDGES)),
            "Довільний стовбур, побудований у порядку перегляду ребер з варіанта:",
            markdown_table(["Крок", "Ребро", "Вага", "Рішення", "К-сть ребер у стовбурі"], log_rows(arbitrary_log)),
            markdown_table(["Вершина 1", "Вершина 2", "Вага"], edge_rows(arbitrary_tree)),
            f"Сума ваг довільного стовбура: {total_weight(arbitrary_tree)}",
            f"Перевірка: ребер {len(arbitrary_tree)}, дерево = {is_tree(arbitrary_tree)}",
            "Мінімальний стовбур, побудований у порядку зростання ваг ребер:",
            markdown_table(["Крок", "Ребро", "Вага", "Рішення", "К-сть ребер у стовбурі"], log_rows(mst_log)),
            markdown_table(["Вершина 1", "Вершина 2", "Вага"], edge_rows(mst_edges)),
            f"Сума ваг мінімального стовбура: {total_weight(mst_edges)}",
            f"Перевірка: ребер {len(mst_edges)}, дерево = {is_tree(mst_edges)}",
            f"Код Прюфера мінімального стовбура: {', '.join(prufer_code(mst_edges))}",
        ]
    )
    (OUT_DIR / "lab6_results.txt").write_text(results + "\n", encoding="utf-8")
    print(results)


if __name__ == "__main__":
    main()
