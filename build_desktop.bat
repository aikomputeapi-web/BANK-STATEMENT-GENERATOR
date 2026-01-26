@echo off
echo ============================================
echo Building Bank Statement Generator Desktop App
echo ============================================
echo.

REM Install PyInstaller if not present
pip install pyinstaller --quiet

REM Build the executable
echo Building executable...
pyinstaller build_exe.spec --clean --noconfirm

echo.
echo ============================================
echo Build complete!
echo.
echo Executable location: dist\BankStatementGenerator.exe
echo ============================================
pause
