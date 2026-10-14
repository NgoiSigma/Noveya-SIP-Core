from __future__ import annotations

import argparse
import json

from matrix_144.cycles_sync import CyclesSynchronizer
from matrix_144.grid_allocator import GridAllocator

from .priorities import PriorityCourse
from .svet import STEPS


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="noveya", description="НОВЕЯ-СИП Core")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cell", help="ячейка 144 по координатам")
    c.add_argument("lat", type=float); c.add_argument("lon", type=float)
    c.add_argument("--depth", type=int, default=1)
    y = sub.add_parser("cycles", help="условный индекс циклов")
    y.add_argument("--year", type=int, default=2026); y.add_argument("--spots", type=float, default=120)
    y.add_argument("--kwave", type=float, default=-0.5)
    sub.add_parser("steps", help="22 шага Акта Творения")
    sub.add_parser("priorities", help="матрица Курса Приоритетов 6×6")
    sub.add_parser("demo", help="сквозной демонстрационный цикл")
    a = p.parse_args(argv)

    if a.cmd == "cell":
        g = GridAllocator()
        path = g.locate_path(a.lat, a.lon, a.depth)
        print(json.dumps({"path": path, "top": g.calculate_cell_coordinates(path[0])}, ensure_ascii=False))
    elif a.cmd == "cycles":
        print(json.dumps(CyclesSynchronizer(a.year, a.spots, a.kwave).evaluate(), ensure_ascii=False, indent=2))
    elif a.cmd == "steps":
        for s in STEPS:
            print(f"{s.no:>2} ({s.letter}) {s.title} — {s.description}")
    elif a.cmd == "priorities":
        for i, row in enumerate(PriorityCourse().matrix(), 1):
            print(f"ПР{i}:", " | ".join(".".join(map(str, g)) for g in row))
    else:
        from .demo import run
        run()
    return 0
