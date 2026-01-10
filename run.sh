#!/bin/bash

# Script de lancement de la Plateforme Oracle AI
# Usage: ./run.sh

echo "🗄️  Plateforme Intelligente de Gestion Oracle avec IA"
echo "======================================================"
echo ""

# Vérifier l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé"
    echo "💡 Créez-le avec: python -m venv venv"
    exit 1
fi

# Activer l'environnement virtuel
echo "🔌 Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier les dépendances
echo "📦 Vérification des dépendances..."
pip install -q -r requirements.txt

# Vérifier la configuration
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé"
    echo "💡 Copiez .env.example vers .env et configurez vos clés API"
    exit 1
fi

# Créer les répertoires nécessaires
echo "📁 Création des répertoires..."
mkdir -p data/oracle_exports data/chroma_db data/synthetic_data data/documents
mkdir -p data/oracle_exports/reports data/oracle_exports/backup_strategies
mkdir -p data/oracle_exports/recovery_playbooks

# Vérifier si les données sont initialisées
if [ ! -f "data/oracle_exports/audit_logs.csv" ]; then
    echo "🔧 Initialisation des données..."
    cd src
    python mock_oracle.py
    python data_extractor.py
    cd ..
fi

# Vérifier si ChromaDB est initialisé
if [ ! -d "data/chroma_db/chroma.sqlite3" ]; then
    echo "📚 Initialisation de la base de connaissances..."
    cd src
    python rag_setup.py
    cd ..
fi

# Vérifier si les logs synthétiques existent
if [ ! -f "data/synthetic_data/audit_logs_synthetic.csv" ]; then
    echo "🧪 Génération des logs synthétiques..."
    cd src
    python synthetic_logs_generator.py
    cd ..
fi

echo ""
echo "✅ Prêt à démarrer!"
echo ""
echo "🚀 Lancement du dashboard..."
echo "📍 URL: http://localhost:8501"
echo ""
echo "💡 Appuyez sur Ctrl+C pour arrêter"
echo ""

# Lancer Streamlit
cd src
streamlit run dashboard.py --server.port=8501 --server.address=localhost

# Désactiver l'environnement à la sortie
deactivate