import emzed


def test_apply_with_nones():
    t = emzed.utils.toTable("a", [1, None])
    t.addColumn("b", t.a.apply(lambda v: 0 if v is None else v))
    assert t.b.values == (1, None)
    t.addColumn("c", t.a.apply(lambda v: 0 if v is None else v, filter_nones=False))
    assert t.c.values == (1, 0)


def test_insert_before_and_after():
    t = emzed.utils.toTable("b", [1])
    t.addColumn("d", [3], insertAfter="b")
    t.addColumn("a", [0], insertBefore="b")
    t.addColumn("c", [2], insertAfter="b")
    assert t.getColNames() == ["a", "b", "c", "d"]
    (a, b, c, d), = t.rows
    assert (a, b, c, d) == (0, 1, 2, 3)


def test_col_with_tuples(regtest):
    t = emzed.utils.toTable("b", [(1, 2)])
    t.print_(out=regtest)


def test_evalsize_of_grouped_aggregate_values():
    # tests a bug fixed in commit 843144a
    t = emzed.utils.toTable("v", [1, 1, 2])
    assert (t.v.count.group_by(t.v) == 1).values == (False, False, True)


def test_grouped_aggregate_with_None_in_group():
    import emzed
    # tests a bug fixed in commit 843144a
    t = emzed.utils.toTable("v", [1, 1, 2, None])
    assert (t.v.count.group_by(t.v)).values == (2, 2, 1, None)

    t.addColumn("u", (1, 1, None, None))
    assert (t.v.count.group_by(t.v, t.u)).values == (2, 2, None, None)


def test_apply_to_empty_col():
    t = emzed.utils.toTable("b", (1,))
    t.addColumn("a", t.b.apply(lambda x: None))


def test_stack_tables_with_empty_list():
    t = emzed.utils.stackTables([])
    assert len(t) == 0
    assert len(t.getColNames()) == 0


def test_invalidated_peakmaps():
    import numpy as np

    peaks = np.zeros((0, 2), dtype="float64")
    spec = emzed.core.data_types.ms_types.Spectrum(peaks, 0.0, 1, "+", [])
    pm = emzed.core.data_types.ms_types.PeakMap([spec])

    t = emzed.utils.toTable("peakmap", [pm, None])

    before = t.uniqueId()
    spec.rt += 1
    assert t.uniqueId() != before
