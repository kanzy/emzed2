set PYTHONHOME=%~dp1
set INSTALLTARGET=%APPDATA%\emzed2
@echo.

%PYTHONHOME%\python.exe ez_setup.py
@echo.

rem on some machines we find the python script on others the exe, so we try both:
%PYTHONHOME%\python.exe -m pip install virtualenv

@echo.
%PYTHONHOME%\python.exe -m virtualenv --system-site-packages %INSTALLTARGET%
@echo.
call %INSTALLTARGET%\Scripts\activate
@echo.
pip install -U setuptools
@echo.

rem "pip install" will download a binary package if available, but when
rem resolving dependencies pip will download source packages. This causes
rem trouble on most machines having no appropriate microsoft compiler
rem installed.  so we first install all pre compiled binary packages and the
rem final "pip install emzed" will only install source distributed stuff:

rem upate numpy first, pyopenms needs this to work:
pip install -U "numpy<1.12"
@echo.
pip install pyopenms
@echo.
python -c "import pyopenms"
@echo.
pip install emzed_optimizations
@echo.
pip install -U ipython==0.10
@echo.
pip install -U dill
@echo.
pip install "pycryptodome<=3.3"
@echo.

:: create unique url to bypass potential cache:
set datetime=%date:~7,2%-%date:~4,2%-%date:~10,4%_%time:~0,2%_%time:~3,2%_%time:~6,2%
pip install http://emzed.ethz.ch/downloads/emzed.zip?%datetime%

REM sometimes matplotlib setup is broken, this should fix this:
set MPLCONFIGDIR=%APPDATA%\matplotlib_config
python -c "import matplotlib"
python -c "import matplotlib"

REM boostrap libs:
emzed.workbench.debug
