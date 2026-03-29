@echo off
echo ================================================
echo Starting Antibiotic Resistance Dashboard
echo Osun State, Nigeria
echo ================================================
echo.

REM Create .streamlit directory if it doesn't exist
if not exist ".streamlit" mkdir .streamlit

REM Create config.toml with light theme
(
echo [theme]
echo base="light"
echo primaryColor="#667eea"
echo backgroundColor="#ffffff"
echo secondaryBackgroundColor="#f0f2f6"
echo textColor="#262730"
echo font="sans serif"
echo.
echo [server]
echo headless = true
echo address = "0.0.0.0"
echo port = 8501
) > .streamlit\config.toml

echo ✓ Theme configuration created
echo ✓ Starting Streamlit with LIGHT THEME...
echo.

REM Run streamlit with explicit theme parameter
streamlit run antibiotic_app.py --theme.base="light" --theme.backgroundColor="#ffffff" --theme.textColor="#262730"
