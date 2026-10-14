import json
from pathlib import Path

import pytest

from matrix_144.cycles_sync import CyclesSynchronizer
from matrix_144.grid_allocator import GridAllocator
from noveya.fdl import ContraryRegistry, DialecticCycle, Judgement, Modality, Relation, SynthesisKind, classify
from noveya.octahedron import Octahedron
from noveya.priorities import PriorityCourse
from noveya.sip import DialogGate, Role, Triad
from noveya.svet import STEPS, ActOfCreation, OrderError, inverse_proportionality_score

ROOT = Path(__file__).resolve().parents[1]


# --- ФДЛ ---
def J(aff=True, **kw):
    return Judgement("X", "эффективен", affirmed=aff, **kw)


def test_conditional_split():
    s = DialecticCycle().run(J(conditions={"масштаб": "страна"}), J(False, conditions={"масштаб": "громада"}))
    assert s.kind is SynthesisKind.CONDITIONAL_SPLIT and s.resolved


def test_contradiction_provisional_prefers_stronger():
    weak = J(modality=Modality.SUPPOSITION, credibility=.4)
    strong = J(False, modality=Modality.DETECTION, credibility=.8)
    s = DialecticCycle().run(weak, strong)
    assert s.kind is SynthesisKind.PROVISIONAL and not s.resolved and strong.text() in s.statement


def test_contraries_need_bridge():
    reg = ContraryRegistry([("добро", "зло")])
    a, b = Judgement("мир", "добро"), Judgement("мир", "зло")
    assert classify(a, b, reg) is Relation.CONTRARY
    cyc = DialecticCycle(reg)
    assert not cyc.run(a, b).resolved
    assert cyc.run(a, b, bridge="мера").resolved


def test_correctness_needs_validity_and_credibility():
    assert not J(credibility=.2).is_correct
    assert not J(valid=False, credibility=.9).is_correct
    assert J(credibility=.9).is_correct
    with pytest.raises(ValueError):
        J(credibility=1.5)


# --- СВЕТ ---
def test_act_order_and_reopen():
    act = ActOfCreation("t")
    with pytest.raises(OrderError):
        act.complete(2, "x")
    act.complete(1, "a"); act.complete("б", "b")
    assert act.next_step().no == 3
    assert act.reopen(1) == ["wish_unspoken", "wish_spoken"]
    assert act.next_step().no == 1


def test_act_priority_course_from_variants_and_roundtrip():
    act = ActOfCreation("t")
    for s in STEPS[:14]:
        act.complete(s.no, f"data{s.no}")
    act.complete(15, ["A", "B"])
    with pytest.raises(ValueError):
        act.complete(16, "C")
    act.complete(16, "B")
    clone = ActOfCreation.from_json(act.to_json())
    assert clone.next_step().no == 17


def test_inverse_proportionality():
    assert inverse_proportionality_score([(1, 12), (2, 6), (3, 4), (4, 3)]) < 1e-9
    assert inverse_proportionality_score([(1, 1), (2, 2), (3, 3)]) > .25


# --- Приоритеты / октаэдр ---
def test_priority_matrix_is_latin_and_matches_source_table():
    pc = PriorityCourse()
    assert pc.is_latin()
    assert pc.focus(1, 1) == (7, 10, 15, 24) and pc.focus(4, 6) == (4, 13, 16, 18)


def test_octahedron():
    ideal = Octahedron({k: 1.0 for k in "DTSVIN"})
    assert ideal.harmony() == 1.0 and ideal.state().startswith("белый")
    dark = Octahedron({"D": 0, "T": 1, "S": 1, "V": 1, "I": 1, "N": 1})
    assert dark.state().startswith("темень")
    assert Octahedron({"D": .9, "T": .4, "S": .9, "V": .5, "I": .6, "N": .8}).suggest_cycles()


# --- Сетка 144 ---
def test_grid_locates_mykolaiv():
    g = GridAllocator()
    cid = g.locate(46.97, 31.99)
    c = g.calculate_cell_coordinates(cid)
    assert cid == 116 and c["lat_range"] == (45.0, 60.0) and c["lon_range"] == (30.0, 60.0)
    assert g.locate_path(46.97, 31.99, 2)[0] == 116


def test_grid_roundtrip_and_area():
    g = GridAllocator()
    for cid in range(1, 145):
        assert g.locate(*g.center(cid)) == cid
    assert abs(sum(g.area_weight(i) for i in range(1, 145)) - 1) < 1e-9
    assert abs(sum(g.distribute(100).values()) - 100) < 1e-9
    assert len(set(g.neighbors(1))) == 3 and len(g.neighbors(80)) == 4


def test_cycles_validation():
    r = CyclesSynchronizer(2026, 10, 0.5).evaluate()
    assert r["session_status"] == "AUTONOMOUS"
    with pytest.raises(ValueError):
        CyclesSynchronizer(kondratiev_phase=2)


# --- СИП ---
def test_triad_and_gate_and_manifesto():
    t = Triad.from_manifesto(str(ROOT / "sip_rules" / "manifesto_sovereignty.json"))
    t.record(Role.LOGOS, 49); t.record(Role.CHAOS, 49); t.record(Role.COSMOS, 2)
    assert t.balanced() and t.hint() is None
    t.record(Role.LOGOS, 100)
    assert not t.balanced() and t.hint() in (Role.CHAOS, Role.COSMOS)
    assert not DialogGate().admit("", "x").admitted and DialogGate().admit("цель", "предмет").admitted
    m = json.loads((ROOT / "sip_rules" / "manifesto_sovereignty.json").read_text(encoding="utf-8"))
    assert m["balance"]["logos"] + m["balance"]["chaos"] + m["balance"]["cosmos"] == 100
