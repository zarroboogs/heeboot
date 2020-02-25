
@echo off

python -m venv .venv

call .\.venv\scripts\activate.bat

pip install pyinstaller
pip install -r requirements.txt

rmdir /s /q .\build\
rmdir /s /q .\dist\
del heeboot.spec

pyinstaller ^
    --onefile ^
    --icon jack.ico ^
    --hidden-import ruamel.yaml ^
    --hidden-import elftools.elf.elffile ^
    .\heeboot.py

ie4uinit -show

pause
