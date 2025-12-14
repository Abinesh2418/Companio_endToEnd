@echo off
echo ============================================
echo Companio Admin Dashboard - Setup Script
echo ============================================
echo.

echo [1/3] Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Please check your Node.js installation.
    pause
    exit /b 1
)

echo.
echo [2/3] Verifying installation...
call npm list --depth=0
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some dependencies may have issues.
)

echo.
echo [3/3] Setup complete!
echo.
echo ============================================
echo Next steps:
echo ============================================
echo 1. Run: npm run dev
echo 2. Open: http://localhost:5173
echo 3. Start coding!
echo.
echo For help, see:
echo - README.md (full documentation)
echo - QUICKSTART.md (quick reference)
echo - CONTRIBUTING.md (team guide)
echo ============================================
echo.
pause
