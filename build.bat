@echo off
echo Building Spaghetti Bandit...

pyinstaller ^
  --onedir ^
  --noconsole ^
  --name "SpaghettiBandit" ^
  --add-data "assets;assets" ^
  --add-data "idle.png;." ^
  --add-data "jump.png;." ^
  --add-data "run.png;." ^
  --collect-all ursina ^
  --collect-all panda3d ^
  game.py

echo.
echo Done! Executable is in dist\SpaghettiBandit\SpaghettiBandit.exe
pause
