from __future__ import print_function

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

    peaks = np.ones((1, 2), dtype="float64")
    spec = emzed.core.data_types.ms_types.Spectrum(peaks, 0.0, 1, "+", [])
    pm = emzed.core.data_types.ms_types.PeakMap([spec])

    t = emzed.utils.toTable("peakmap", [pm, None])

    before = t.uniqueId()
    spec.rt += 1
    assert t.uniqueId() != before


def test_excel_io(tmpdir, regtest):
    t = emzed.utils.toTable("a", (0, 2, 3, None), type_=int)
    t.addColumn("b", t.a.apply(str) + "_", type_=str)
    t.addColumn("c", t.a.apply(unicode) + "_", type_=unicode)
    t.addColumn("d", t.a + .1, type_=float)
    t.addColumn("e", t.a.apply(bool), type_=bool)

    print(t, file=regtest)

    path = tmpdir.join("table.xlsx").strpath
    emzed.io.storeExcel(t, path)

    types = {"a": int, "e": bool, "b": str, "d": float}
    formats = {"d": "%+.1f"}
    tn = emzed.io.loadExcel(path, types=types, formats=formats)
    print(tn, file=regtest)


def test_excel_io_2(tmpdir, regtest):

    CheckState = emzed.core.CheckState
    PeakMap = emzed.core.PeakMap
    TimeSeries = emzed.core.TimeSeries
    Blob = emzed.core.Blob

    t = emzed.utils.toTable("a", (0, 2, 3, None), type_=int)
    t.addColumn("checked", (t.a < 2), type_=CheckState)
    t.addColumn("checked2", (t.a < 2), type_=CheckState)
    t.addColumn("pm", PeakMap([]), type_=PeakMap)
    t.addColumn("ts", TimeSeries([], []), type_=TimeSeries)
    t.addColumn("blob", Blob(""), type_=Blob)

    print(t, file=regtest)

    path = tmpdir.join("table.xlsx").strpath
    emzed.io.storeExcel(t, path)

    types = {"a": int, "checked": bool, "checked2": CheckState}
    tn = emzed.io.loadExcel(path, types=types)
    print(tn, file=regtest)


def test_collapse_stuff(tmpdir, regtest):
    t = emzed.utils.toTable("group_id", (1, 1, 2, 2, 3), type_=int)
    t.addColumn("data", range(5), type_=float)
    tn = t.collapse("group_id")

    print(tn, file=regtest)
    for subt in tn.collapsed:
        subt.data
        subt.data.values
        print(subt, file=regtest)

    tn.collapsed[0].replaceColumn("data", 1.0, type_=float)

    print(tn, file=regtest)
    for subt in tn.collapsed:
        print(subt, file=regtest)

    for row in tn.collapsed[0]:
        row.data = 2

    print(tn, file=regtest)
    for subt in tn.collapsed:
        print(subt, file=regtest)
        print(subt.data.values, file=regtest)


def test_special_col_conversion(regtest):
    from emzed.core import CheckState, PeakMap, TimeSeries, Blob

    pm = PeakMap([])
    ts = TimeSeries([], [])
    blob = Blob("")

    t = emzed.utils.toTable("group_id", (1, 1, 2, 2, 3), type_=int)
    t.addColumn("data", range(5), type_=float)
    t.addColumn("checked", (t.group_id == 1).thenElse(None, t.group_id == 2), type_=CheckState)
    t.addColumn("pm", (t.group_id == 1).thenElse(None, pm), type_=PeakMap)
    t.addColumn("ts", (t.group_id == 2).thenElse(None, ts), type_=TimeSeries)
    t.addColumn("blob", (t.group_id == 3).thenElse(None, blob), type_=Blob)

    print(t, file=regtest)
    df = t.to_pandas(do_format=True)
    print(df, file=regtest)
