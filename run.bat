@echo off
REM Script de lancement Windows

echo ========================================
echo  Plateforme Oracle AI
echo ========================================
echo.

REM Vérifier l'environnement virtuel
if not exist "venv\" (
    echo Environnement virtuel non trouve
    echo Creez-le avec: python -m venv venv
    pause
    exit /b 1
)

REM Activer l'environnement
echo Activation de l'environnement...
call venv\Scripts\activate.bat

REM Installer les dépendances
echo Installation des dependances...
pip install -q -r requirements.txt

REM Vérifier .env
if not exist ".env" (
    echo Fichier .env non trouve
    echo Copiez .env.example vers .env
    pause
    exit /b 1
)

REM Créer les répertoires
echo Creation des repertoires...
if not exist "data\oracle_exports\" mkdir data\oracle_exports
if not exist "data\chroma_db\" mkdir data\chroma_db
if not exist "data\synthetic_data\" mkdir data\synthetic_data
if not exist "data\documents\" mkdir data\documents

REM Initialiser les données
if not exist "data\oracle_exports\audit_logs.csv" (
    echo Initialisation des donnees...
    cd src
    python mock_oracle.py
    python data_extractor.py
    cd ..
)

REM Initialiser ChromaDB
if not exist "data\chroma_db\chroma.sqlite3" (
    echo Initialisation ChromaDB...
    cd src
    python rag_setup.py
    cd ..
)

REM Générer logs synthétiques
if not exist "data\synthetic_data\audit_logs_synthetic.csv" (
    echo Generation logs synthetiques...
    cd src
    python synthetic_logs_generator.py
    cd ..
)

echo.
echo Pret a demarrer!
echo.
echo URL: http://localhost:8501
echo.
echo Appuyez sur Ctrl+C pour arreter
echo.

REM Lancer Streamlit
cd src
streamlit run dashboard.py --server.port=8501 --server.address=localhost

REM Désactiver l'environnement
call deactivate