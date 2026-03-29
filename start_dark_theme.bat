@echo off
echo ================================================
echo Starting Antibiotic Resistance Dashboard
echo DARK THEME with Colorful Metrics
echo ================================================
echo.

REM Create .streamlit directory if it doesn't exist
if not exist ".streamlit" mkdir .streamlit

REM Create config.toml with DARK theme
(
echo [theme]
echo base="dark"
echo primaryColor="#a78bfa"
echo backgroundColor="#0f172a"
echo secondaryBackgroundColor="#1e293b"
echo textColor="#f1f5f9"
echo font="sans serif"
echo.
echo [server]
echo headless = true
echo address = "0.0.0.0"
echo port = 8501
) > .streamlit\config.toml

echo ✓ Dark Theme configuration created
echo ✓ Starting Streamlit...
echo.

streamlit run antibiotic_app_dark.py
