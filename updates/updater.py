# encoding: utf-8
from __future__ import print_function


def version():
    return (2, 28, 6)


def version_string():
    v = version()
    if len(v) == 4:
        v_str = "%d.%d.%dpost%d" % v
    else:
        v_str = "%d.%d.%d" % v
    return v_str


is_experimental = False


def description():
    msg = """

    ! EXPERIMENTAL UPDATE !
    ! ONLY INSTALL THIS UPDATE IF YOU WERE ASKED TO INSTALL IT !

    release notes:
        - fixed bug when loading presets for visible table columns
        - "-" in csv files are read as 'None' now
    """
    return msg


def run_update(locally=True):
    import pip

    pip.main("install pycryptodome<=3.3".split())
    pip.main("install emzed_optimizations>=0.6.0".split())

    pip.main("install xlwt".split())
    pip.main("install xlrd".split())

    pip.main("install jdcal".split())
    pip.main("install et-xmlfile".split())
    pip.main("install openpyxl".split())

    pip.main(["install", "emzed==%s" % version_string()])


if __name__ == "__main__":
    import os
    is_venv = os.getenv("VIRTUAL_ENV") is not None
    run_update(locally=not is_venv)
