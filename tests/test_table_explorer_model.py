from emzed.core.explorers.table_explorer_model import (TableModel,
                                                       MutableTableModel,
                                                       DeleteRowsAction,
                                                       SortTableAction,
                                                       ChangeValueAction,
                                                       IntegrateAction,
                                                       CloneRowAction)

import emzed.utils

from emzed.core.data_types import Spectrum, PeakMap, Table

from PyQt4.QtCore import QAbstractTableModel, Qt, QVariant



def buildTable():
    t = emzed.utils.toTable("mz", [1.0, 2.0, None])
    t.addColumn("mzmin", t.mz-0.025)
    t.addColumn("mzmax", t.mz+0.025)

    t.addColumn("rt", [10.0, 20.0, None])
    t.addColumn("rtmin", t.rt-1.0)
    t.addColumn("rtmax", t.rt+5.0)

    t.addColumn("peakmap", [None, (1, 2), None])
    return t


def buildTable2():
    t = emzed.utils.toTable("mz", [1.0, 2.0, None])
    t.addColumn("mzmin", t.mz-0.025)
    t.addColumn("mzmax", t.mz+0.025)

    t.addColumn("rt", [10.0, 20.0, None])
    t.addColumn("rtmin", t.rt-1.0)
    t.addColumn("rtmax", t.rt+5.0)

    t.addColumn("peakmap", [None, (1, 2), None])
    t._renameColumnsUnchecked(mz="mz__1", mzmin="mzmin__1", mzmax="mzmax__1",
                              rt="rt__1", rtmin="rtmin__1", rtmax="rtmax__1",
                              peakmap="peakmap__1")

    return t


def testTable2():
    t = buildTable2()
    model = TableModel(t, None)
    model.table.info()
    assert model.checkForAny("mz", "rt", "rtmin", "rtmax", "mzmin", "mzmax", "peakmap")
    assert model.checkForAny("mz__1")
    assert not model.checkForAny("mz__1", "rt__x")


def testSimpleTable():
    t = buildTable()
    t.info()
    t._print()
    model = MutableTableModel(t, None)
    model.addNonEditable("rtmax")

    assert model.checkForAny("mzmin")
    assert not model.checkForAny("xxx")

    def idx(r, c):
        return model.createIndex(r, c)

    assert model.rowCount() == 3
    assert model.columnCount() == 7

    for i in range(3):
        for j in range(6):
            val = t.rows[i][j]
            is_ = model.data(idx(i, j))
            tobe = t.colFormatters[j](val)
            assert is_ == tobe, (is_, tobe)

    for i in range(3):
        for j in range(6):
            val = t.rows[i][j]
            is_ = model.data(idx(i, j), Qt.EditRole)
            tobe = t.colFormatters[j](val)
            assert is_ == tobe, (is_, tobe)

    for j in range(6):
        is_ = model.headerData(j, Qt.Horizontal)
        tobe = t.getColNames()[j]
        assert is_ == tobe, (is_, tobe)

    for j in range(6):
        flag = model.flags(idx(0, j))
        if j == 5:
            assert flag & Qt.ItemIsEditable == Qt.NoItemFlags
        else:
            assert flag & Qt.ItemIsEditable == Qt.ItemIsEditable

    for i in range(3):
        for j in range(3):
            val = i+j+1.5
            assert model.setData(idx(i, j), QVariant(str(val)))
            is_ = model.data(idx(i, j))
            tobe = t.colFormatters[j](val)
            assert is_ == tobe, (is_, tobe)
        for j in range(3, 6):
            val = j*1.0+i
            sv = "%.1fm" % val
            assert model.setData(idx(i, j), QVariant(sv))
            is_ = model.data(idx(i, j))
            tobe = t.colFormatters[j](val*60.0)
            assert is_ == tobe, (is_, tobe)

    assert len(model.actions) == 3*6
    model.emptyActionStack()

    before = model.data(idx(0, 0))
    model.setData(idx(0, 0), QVariant("-"))
    assert model.data(idx(0, 0)) == "-"
    assert model.table.rows[0][0] == None

    model.undoLastAction()
    assert before == model.data(idx(0, 0))
    assert len(model.actions) == 0

    model.redoLastAction()
    assert model.data(idx(0, 0)) == "-"
    assert model.table.rows[0][0] == None

    # here no undo !

    assert model.table.rows[0] != model.table.rows[1]
    assert model.rowCount() == 3
    model.cloneRow(0)
    assert model.table.rows[0] == model.table.rows[1]
    assert model.rowCount() == 4
    model.undoLastAction()
    assert model.table.rows[0] != model.table.rows[1]
    assert model.rowCount() == 3

    model.cloneRow(0)
    model.removeRows([0])
    assert model.table.rows[0] != model.table.rows[1]
    assert model.rowCount() == 3

    model.undoLastAction()
    model.undoLastAction()
    assert model.table.rows[0] != model.table.rows[1]
    assert model.rowCount() == 3

    assert len(model.actions) == 1  # 1 undo missing

    # we have to call sort three times, the first two are ingnored
    # for details look at the comment of the TableModel.sort method !
    model.sort(0, Qt.DescendingOrder)
    model.sort(0, Qt.DescendingOrder)
    model.sort(0, Qt.DescendingOrder)

    permutation = model.get_row_permutation()
    assert tuple(model.table.mz.values[pi] for pi in permutation) == (3.5, 2.5, None)
    # assert model.table.mz.values == (3.5, 2.5, None)


    model.undoLastAction()

    permutation = model.get_row_permutation()
    assert tuple(model.table.mz.values[pi] for pi in permutation) == (None, 2.5, 3.5)
    # assert model.table.mz.values == (None, 2.5, 3.5)

    #assert model.postfixes == [""]

    assert model.hasFeatures()
    assert not model.isIntegrated()


def testMixedRows():
    names = """rt rtmin rtmax rt__1 rtmin__1 rtmax__1
               mz mzmin mzmax mz__1 mzmin__1 mzmax__1
               rt__0 rtmin__0 rtmax__0
               mz__0 mzmin__0 mzmax__0
               rt__2 rtmin__2""".split()

    names = [n.strip() for n in names]

    tab = Table._create(names, [float]*len(names), ["%f"] * len(names))

    model = TableModel(tab, None)

    #assert model.postfixes == [ "", "__0", "__1", "__2"], model.postfixes

    assert model.table.supportedPostfixes(["rtmin", "rt"]) == ["", "__0", "__1", "__2"]
    assert model.table.supportedPostfixes(["mz", "rt", "mzmin"]) == ["", "__0", "__1"]
    assert model.table.supportedPostfixes(["mz", "rt", "x"]) == []


def testActions():

    t = buildTable()
    n = len(t)
    model = TableModel(t, None)
    t_orig = t.copy()

    action = DeleteRowsAction(model, [0], [0])
    action.do()
    assert len(model.table) == len(t_orig)-1
    assert model.table.rows[0] == t_orig.rows[1]
    action.undo()
    assert len(model.table) == len(t_orig)
    assert model.table.rows[0] == t_orig.rows[0]

    action = CloneRowAction(model, 0, 0)
    action.do()
    assert model.table.rows[0] == t_orig.rows[0]
    assert model.table.rows[1] == t_orig.rows[0]
    assert model.table.rows[2] == t_orig.rows[1]
    assert len(model.table) == n+1
    action.undo()
    assert len(model.table) == n
    assert model.table.rows[0] == t_orig.rows[0]
    assert model.table.rows[1] == t_orig.rows[1]

    orig_permutation = model.get_row_permutation()
    action = SortTableAction(model, [("mz", True)])
    action.do()
    permutation = model.get_row_permutation()
    assert tuple(model.table.mz.values[pi] for pi in permutation) == (None, 1.0, 2.0)
    action.undo()
    permutation = model.get_row_permutation()
    assert permutation == orig_permutation

    orig_permutation = model.get_row_permutation()
    action = SortTableAction(model, [("mz", False)])
    action.do()
    permutation = model.get_row_permutation()
    assert tuple(model.table.mz.values[pi] for pi in permutation) == (2.0, 1.0, None)
    action.undo()
    permutation = model.get_row_permutation()
    assert permutation == orig_permutation

    class Index(object):

        def row(self):
            return 0

        def column(self):
            return 0

    action = ChangeValueAction(model, Index(), 0, 0, 3.0)
    action.do()
    assert model.table.rows[0][0] == 3.0
    action.undo()
    assert model.table.rows[0][0] == 1.0

    t = buildTable()
    import numpy
    peak = numpy.array(((1.0, 100.0),))
    specs = [Spectrum(peak, rt, 1, "+") for rt in range(9, 15)]
    pm = PeakMap(specs)

    t.replaceColumn("peakmap", pm)

    model.table = emzed.utils.integrate(t, "no_integration")

    action = IntegrateAction(model, 0, "", "trapez", 0, 100, 0)
    action.do()
    assert model.table.area.values[0] == 500.0
    action.undo()

    assert model.table.area.values[0] == None
