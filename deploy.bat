@echo off
rem deploy.bat - Update repo, activate venv, and run the app

cd /d "%~dp0"

rem Pull latest changes
if exist ".git" (
    echo Pulling latest changes...
    git pull --ff-only
) else (
    echo Not inside a git repository.
    exit /b 1
)

rem Activate virtual environment or create it if missing
if exist "venv\Scripts\activate.bat" (
    echo Activating existing virtual environment...
    call "venv\Scripts\activate.bat"
) else (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call "venv\Scripts\activate.bat"
    if exist requirements.txt (
        pip install -r requirements.txt
    ) else (
        pip install flask
    )
)

rem Start the Flask application
python app.py
