import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from clipper.follow import (
    build_x_expr,
    merge_short,
    plan_switches,
    plan_to_shots,
    segments,
    track_centers,
)


def test_segments_basic():
    assert segments(0, 10, [3, 7]) == [(0, 3), (3, 7), (7, 10)]


def test_segments_merges_tiny_shot():
    assert segments(0, 10, [5.0, 5.3]) == [(0, 5.3), (5.3, 10)]


def test_segments_ignores_out_of_range_cuts():
    assert segments(0, 10, [-1, 3, 99]) == [(0, 3), (3, 10)]


def test_track_centers_single_column():
    assert track_centers([0.5, 0.51, 0.49]) == [0.5]


def test_track_centers_two_columns():
    c = track_centers([0.2, 0.22, 0.7, 0.72, 0.21])
    assert len(c) == 2
    assert abs(c[0] - 0.21) < 0.02
    assert abs(c[1] - 0.71) < 0.02


def test_track_centers_empty():
    assert track_centers([]) == []


def test_plan_switches_single_track():
    assert plan_switches([0, 1, 2], [[1.0], [1.0], [1.0]], 1) == [(0, 2, 0)]


def test_plan_switches_to_active_track():
    times = [0, 0.5, 1.0, 1.5, 2.0, 2.5]
    acts = [[5, 0], [5, 0], [0, 5], [0, 5], [0, 5], [0, 5]]
    assert plan_switches(times, acts, 2, min_dwell=1.0) == [
        (0, 1.5, 0),
        (1.5, 2.5, 1),
    ]


def test_plan_switches_starts_on_active_track():
    times = [0, 0.5, 1.0]
    acts = [[2, 18], [5, 18], [3, 15]]
    assert plan_switches(times, acts, 2, min_dwell=1.0) == [(0, 1.0, 1)]


def test_plan_switches_respects_min_dwell():
    times = [0, 0.5, 1.0, 1.5, 2.0, 2.5]
    acts = [[5, 0], [5, 0], [0, 5], [0, 5], [0, 5], [0, 5]]
    assert plan_switches(times, acts, 2, min_dwell=5.0) == [(0, 2.5, 0)]


def test_build_x_expr_step():
    shots = [
        {"start": 0, "end": 5, "x": 0.25},
        {"start": 5, "end": 10, "x": 0.75},
    ]
    assert build_x_expr(shots, 0, 1000, 400) == "if(lt(t,5.0),50,550)"


def test_build_x_expr_single_and_clamp():
    assert build_x_expr([{"start": 0, "end": 5, "x": 0.0}], 0, 1000, 400) == "0"
    assert build_x_expr([], 0, 1000, 400) is None


def test_merge_short_absorbs_tail():
    shots = [
        {"start": 0, "end": 5, "x": 0.3},
        {"start": 5, "end": 5.5, "x": 0.7},
        {"start": 5.5, "end": 9, "x": 0.7},
    ]
    assert merge_short(shots, min_seg=0.6) == [
        {"start": 0, "end": 5.5, "x": 0.3},
        {"start": 5.5, "end": 9, "x": 0.7},
    ]


def test_plan_to_shots_snaps_to_shot_bounds():
    out = plan_to_shots([(515.5, 523.5, 1)], 515.0, 524.0, [0.25, 0.67])
    assert out == [{"start": 515.0, "end": 524.0, "x": 0.67}]


def test_plan_to_shots_first_and_last_only():
    plan = [(546.0, 549.0, 0), (549.0, 556.0, 1)]
    out = plan_to_shots(plan, 545.5, 556.5, [0.25, 0.67])
    assert out[0]["start"] == 545.5
    assert out[-1]["end"] == 556.5
    assert [sh["x"] for sh in out] == [0.25, 0.67]
