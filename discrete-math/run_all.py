from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LABS = [
    ("lab-01", "lab1_sets.py"),
    ("lab-02", "lab2_covering.py"),
    ("lab-03", "lab3_boolean.py"),
    ("lab-04", "lab4_minimization.py"),
    ("lab-05", "lab5_shortest_path.py"),
    ("lab-06", "lab6_spanning_tree.py"),
    ("lab-07", "lab7_graph_partition.py"),
    ("lab-08", "lab8_max_flow.py"),
]


def main() -> None:
    for lab_dir, script_name in LABS:
        workdir = ROOT / lab_dir
        print(f"==> Running {lab_dir}/{script_name}", flush=True)
        subprocess.run([sys.executable, script_name], cwd=workdir, check=True)

    print("All discrete mathematics labs completed successfully.")


if __name__ == "__main__":
    main()
