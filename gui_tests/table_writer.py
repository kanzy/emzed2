import emzed
import copy
from numpy.random import randint, random as np_random
import random
import contextlib
import time


from emzed.io import atomic_hdf5_writer, to_hdf5
from emzed.core import CheckState, Table
from emzed.ff import  runMetaboFeatureFinder
from emzed.utils import  integrate

try:
    profile
except NameError:
    def profile(fun):
        return fun


@contextlib.contextmanager
def measure(title=""):
    if title:
        title = " " + title
    print("start%s" % title)
    started = time.time()
    yield
    needed = time.time() - started
    print("running%s needed %.2f seconds" % (title, needed))



@profile
def main():

    with measure("load pm"):
        # pm = emzed.io.loadPeakMap("141208_pos001.mzXML")
        pm = emzed.io.loadPeakMap("Danu.mzML")

    t0 = emzed.utils.toTable("peakmap", (pm,), type_=object)
    path = "pm_only.hdf5"
    with atomic_hdf5_writer(path) as add:
        add(t0)

    peaks = runMetaboFeatureFinder(pm)
    peaks = integrate(peaks)
    peaks.info()
    with atomic_hdf5_writer("peaks.hdf5") as add:
        add(peaks)

    # return

@profile
def main():

    with measure("load pm"):
        # pm = emzed.io.loadPeakMap("141208_pos001.mzXML")
        pm = emzed.io.loadPeakMap("Danu.mzML")

    pm2 = copy.deepcopy(pm)
    # create modified copy
    pm2.spectra = pm2.spectra[1:]

    rtmin, rtmax = pm.rtRange()

    pms = [pm, pm2]

    n = 10000
    integers = list(reversed(range(n)))
    for k in range(0, n, 10):
        integers[k] = None

    flags = [i % 2 == 0 for i in range(n)]

    tuples = [tuple(randint(0, 1000, size=10)) for _ in range(100)]

    tsub = emzed.utils.toTable("a", (1, 2, 3), type_=int)

    with measure("create table"):
        t = emzed.utils.toTable("integers", integers, type_=int)
        t.addColumn("check", flags, type_=CheckState)
        t.addColumn("sub_table", tsub, type_=Table, format_="%r")
        t.addColumn(
            "mzmin", t.apply(lambda: 100 + 900 * np_random() + np_random(), ()), type_=float)
        t.addColumn(
            "mzmax", t.apply(lambda mzmin: mzmin + 0.1 * np_random(), (t.mzmin,)), type_=float)

        t.addColumn("rtmin", t.apply(lambda: rtmin + (rtmax - rtmin) * np_random(), ()), type_=float)
        t.addColumn(
            "rtmax", t.apply(lambda rtmin: rtmin + 30 + 300 * np_random(), (t.rtmin,)), type_=float)
        t.addColumn("peakmap", t.apply(lambda: random.choice(pms), ()), type_=object)

        for i in range(10):
            print(i)
            t.addColumn("floats_%d" % i, t.integers + 1.1, type_=float)
            t.addColumn("strings_%d" % i, t.integers.apply(str) * (i % 3), type_=str)
            t.addColumn("tuples_%d" % i, t.apply(lambda: random.choice(tuples), ()), type_=object)
            t.addColumn("peakmaps_%d" % i, pms[i % 2], type_=object)

        target_ids = [None] * n
        for i in range(0, n, 100):
            target_ids[i] = "target_%d" % i
            target_ids[i + 1] = "target_%d" % i
            target_ids[i + 2] = "target_%d" % i
            target_ids[i + 3] = "target_%d" % i

        t.addColumn("target_id", target_ids, type_=str)

    n, m = t.shape
    #for fac in (1, 10):
    for fac in (1, ):
        n0 = n * fac
        with measure("write hdf5 table with %d rows and %d cols" % (n0, m)):
            path = "test_%d.hdf5" % (n * fac)
            with atomic_hdf5_writer(path) as add:
                for i in range(fac):
                    print(i, "out of", fac)
                    add(t)

if __name__ == "__main__":
    main()
