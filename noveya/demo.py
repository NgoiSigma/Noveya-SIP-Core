"""Сквозной демонстрационный цикл по Николаеву. Все входные числа — ИЛЛЮСТРАТИВНЫЕ."""
from __future__ import annotations

from matrix_144.cycles_sync import CyclesSynchronizer
from matrix_144.grid_allocator import GridAllocator

from .avatarus import SigmaAvatarus
from .fdl import ContraryRegistry, DialecticCycle, Judgement, Modality
from .octahedron import Octahedron
from .priorities import PriorityCourse
from .sip import Role, SipSession
from .svet import ActOfCreation


def run() -> None:
    bar = "=" * 64
    print(bar, "\n", SigmaAvatarus().awaken(), "\n", bar, sep="")

    grid = GridAllocator()
    lat, lon = 46.97, 31.99
    cell = grid.locate(lat, lon)
    print(f"1. Среда: Николаев → ячейка {cell} {grid.calculate_cell_coordinates(cell)['lat_range']} "
          f"{grid.calculate_cell_coordinates(cell)['lon_range']}; путь {grid.locate_path(lat, lon, 3)}")
    rep = CyclesSynchronizer().evaluate()
    print(f"   Циклы: индекс={rep['friction_index']} → {rep['session_status']} ({rep['note']})")

    print("\n2. Октаэдр (демо-радиусы):")
    octa = Octahedron({"D": .9, "T": .4, "S": .9, "V": .5, "I": .6, "N": .8})
    print(f"   гармония={octa.harmony():.2f} — {octa.state()}")
    for c in octa.suggest_cycles():
        print("   ▸", c["question"])

    print("\n3. Цикл ФДЛ:")
    cyc = DialecticCycle(ContraryRegistry([("централизованно", "децентрализованно")]))
    t = Judgement("координация развития", "эффективна", conditions={"масштаб": "национальный"},
                  modality=Modality.DESCRIPTIVE, credibility=.7)
    a = Judgement("координация развития", "эффективна", affirmed=False,
                  conditions={"масштаб": "громада"}, modality=Modality.DESCRIPTIVE, credibility=.7)
    print(cyc.run(t, a).render())
    t2 = Judgement("платформа", "повышает доверие", modality=Modality.SUPPOSITION, credibility=.4)
    a2 = Judgement("платформа", "повышает доверие", affirmed=False, modality=Modality.DETECTION, credibility=.8)
    print(cyc.run(t2, a2).render())

    print("\n4. Акт Творения:")
    act = ActOfCreation("Развитие громады (демо)", creator="Творец")
    for no, txt in enumerate(["Хочу согласованного развития", "Создать платформу координации громад",
                              "Как согласовать решения без потери автономии?"], start=1):
        act.complete(no, txt)
    print(act.report().split("\n")[0], "→ следующий:", act.next_step().title)

    print("\n5. Курс приоритетов, ПР1:", [PriorityCourse().focus(1, s) for s in range(1, 3)], "…")

    print("\n6. Сессия СИП:")
    s = SipSession(cell_id=cell, mode=rep["session_status"])
    for r, e in ((Role.LOGOS, 50), (Role.CHAOS, 40), (Role.COSMOS, 2)):
        s.triad.record(r, e)
    print("   доли:", {k.value: round(v, 1) for k, v in s.triad.shares().items()},
          "| сбалансировано:", s.triad.balanced(), "| не хватает:", s.triad.hint())
    s.note("черновик")
    print("   очистка буфера, удалено записей:", s.clear_buffer())
