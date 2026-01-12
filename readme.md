# 🗄️ Plateforme Intelligente de Gestion Oracle avec IA

Plateforme complète d'administration Oracle Database assistée par Intelligence Artificielle (LLM + RAG), développée dans le cadre d'un projet académique.

## 📋 Table des Matières

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Modes de Fonctionnement](#modes-de-fonctionnement)
- [Utilisation](#utilisation)
- [Modules](#modules)
- [Tests](#tests)
- [Technologies](#technologies)

---

## 🎯 Présentation

Cette plateforme combine l'optimisation des requêtes Oracle, l'audit de sécurité, la détection d'anomalies et la gestion intelligente des sauvegardes/restaurations, le tout assisté par un LLM (Large Language Model) via Prompt Engineering et RAG (Retrieval-Augmented Generation).

### Objectifs

- ✅ Optimiser les performances Oracle
- ✅ Détecter les failles de sécurité
- ✅ Alerter sur les comportements anormaux
- ✅ Automatiser la gestion des sauvegardes et restaurations
- ✅ Communiquer en langage naturel via un chatbot IA

---

## 🚀 Fonctionnalités

### 1. 🔒 Audit de Sécurité Automatisé
- Analyse des comptes utilisateurs, privilèges et profils
- Détection des risques selon les standards OWASP et CIS
- Score de sécurité global (0-100)
- Recommandations d'actions correctives

### 2. ⚡ Optimisation de Requêtes
- Identification automatique des requêtes lentes
- Analyse des plans d'exécution
- Suggestions d'index et d'optimisations
- Estimation des gains de performance

### 3. 🛡️ Détection d'Anomalies
- Analyse des logs d'audit en temps réel
- Détection d'injections SQL, escalades de privilèges
- Identification d'accès suspects et exfiltration de données
- Classification : Normal / Suspect / Critique

### 4. 💾 Gestion des Sauvegardes
- Recommandation de stratégies selon RPO/RTO
- Génération de scripts RMAN automatiques
- Planification cron des backups
- Estimation des coûts

### 5. 🔧 Guide de Restauration
- Playbooks détaillés pour 4 scénarios de récupération
- Restauration complète après crash
- Point-In-Time Recovery (PITR)
- Récupération de tables et tablespaces

### 6. 💬 Chatbot Conversationnel
- Assistant IA pour toutes les questions Oracle
- Contexte enrichi via RAG
- Historique de conversation
- Suggestions intelligentes

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Interface Streamlit (Web)           │
│      Dashboard + Chatbot Conversationnel    │
└────────────────┬────────────────────────────┘
                 │
     ┌───────────┼───────────┬────────────┐
     │           │           │            │
┌────▼────┐ ┌───▼───┐ ┌─────▼───┐  ┌────▼────┐
│Modules  │ │Ollama │ │Vector DB│  │ Oracle  │
│(9x)     │ │(Local)│ │(Chroma) │  │ Docker  │
└─────────┘ └───────┘ └─────────┘  └─────────┘
```

### 9 Modules Principaux

1. **Data Extractor** : Extraction des données Oracle
2. **RAG Setup** : Base de connaissances vectorielle
3. **LLM Engine** : Interface centralisée pour Ollama
4. **Security Auditor** : Audit de sécurité
5. **Query Optimizer** : Optimisation de requêtes
6. **Anomaly Detector** : Détection d'anomalies
7. **Backup Recommender** : Stratégies de sauvegarde
8. **Recovery Guide** : Procédures de restauration
9. **Dashboard** : Interface utilisateur web

---

## 📦 Installation

### Prérequis

- Python 3.9+
- Docker et Docker Compose (pour Oracle)
- Ollama installé localement
- 2 GB d'espace disque
- 8 GB RAM minimum (pour Oracle + Ollama)

### Installation Rapide

```bash
# 1. Cloner le projet
git clone <https://github.com/MinaBouzid1/oracle_ai_platform>
cd oracle-ai-platform

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Sur Linux/Mac :
source venv/bin/activate
# Sur Windows :
venv\Scripts\activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Installer Ollama
# Sur Linux/Mac :
curl -fsSL https://ollama.com/install.sh | sh
# Sur Windows : télécharger depuis https://ollama.com/download

# 6. Télécharger le modèle LLM
ollama pull llama2

# 7. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env selon vos besoins

# 8. Initialiser les données (mode Mock)
cd src
python mock_oracle.py
python data_extractor.py
python rag_setup.py
python synthetic_logs_generator.py
cd ..
```

### Installation d'Oracle avec Docker (Optionnel)

Pour utiliser une vraie base de données Oracle :

```bash
# 1. Créer le fichier docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'
services:
  oracle:
    image: container-registry.oracle.com/database/express:21.3.0-xe
    ports:
      - "1521:1521"
      - "5500:5500"
    environment:
      - ORACLE_PWD=YourStrongPassword123
    volumes:
      - oracle-data:/opt/oracle/oradata
volumes:
  oracle-data:
EOF

# 2. Lancer Oracle
docker-compose up -d

# 3. Attendre que Oracle soit prêt (2-3 minutes)
docker logs -f oracle-ai-platform-oracle-1

# 4. Configurer la connexion dans .env
# Voir section "Modes de Fonctionnement" ci-dessous
```

---

## 🔄 Modes de Fonctionnement

La plateforme supporte **deux modes** : **Mock** (simulateur) et **Oracle** (base réelle). C'est à l'utilisateur de choisir selon ses besoins.

### Mode 1 : Mock (Recommandé pour Tests Rapides)

**Avantages :**
- ✅ Pas besoin d'Oracle installé
- ✅ Démarrage instantané
- ✅ Parfait pour démonstrations et tests
- ✅ Données synthétiques réalistes

**Configuration `.env` :**
```bash
# Mode Mock
USE_MOCK=true
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2 ou mistral
```

**Initialisation :**
```bash
cd src
python mock_oracle.py          # Génère les données simulées
python data_extractor.py       # Extrait les données
python rag_setup.py            # Initialise RAG
python synthetic_logs_generator.py  # Génère les logs
```

### Mode 2 : Oracle (Production)

**Avantages :**
- ✅ Connexion à une vraie base Oracle
- ✅ Données réelles pour audits précis
- ✅ Tests en environnement réaliste

**Prérequis :**
- Oracle Database installé (Docker ou serveur)
- Droits DBA pour accès aux vues système

**Configuration `.env` :**
```bash
# Mode Oracle
USE_MOCK=false

# Connexion Oracle
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=XEPDB1
ORACLE_USER=system
ORACLE_PASSWORD=YourStrongPassword123
ORACLE_WALLET_PATH=/path/to/wallet  # Optionnel

# LLM
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2 ou mistral
```

**Fichier de connexion : `oracle_connector.py`**

Le module `oracle_connector.py` gère automatiquement la connexion selon le mode :

```python
from oracle_connector import OracleConnector

# Le mode est détecté automatiquement depuis .env
connector = OracleConnector()
connector.connect()

# Exécuter des requêtes
results = connector.execute_query("SELECT * FROM DBA_USERS")
```

**Basculer entre les modes :**

Il suffit de modifier `USE_MOCK` dans `.env` et relancer l'application :

```bash
# Passer en mode Oracle
sed -i 's/USE_MOCK=true/USE_MOCK=false/' .env

# Passer en mode Mock
sed -i 's/USE_MOCK=false/USE_MOCK=true/' .env

# Relancer
./run.sh
```

---

## 🎮 Utilisation

### Lancement Rapide

```bash
# Linux/Mac
chmod +x run.sh
./run.sh

# Windows
run.bat
```

L'application sera accessible à : **http://localhost:8501**

### Utilisation Manuelle

```bash
# Activer l'environnement
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Vérifier qu'Ollama est lancé
ollama list

# Lancer le dashboard
cd src
streamlit run dashboard.py
```

### Tests des Modules Individuels

Chaque module peut être testé indépendamment :

```bash
cd src

# Module 1 : Extraction
python data_extractor.py

# Module 2 : RAG
python rag_setup.py

# Module 3 : LLM Engine
python llm_engine.py

# Module 4 : Audit Sécurité
python security_audit.py

# Module 5 : Optimisation
python query_optimizer.py

# Module 6 : Détection Anomalies
python anomaly_detector.py

# Module 7 : Sauvegardes
python backup_recommender.py

# Module 8 : Restauration
python recovery_guide.py
```

---

## 📚 Modules Détaillés

### Module 1 : Data Extractor
**Fichier :** `src/data_extractor.py`

Extrait les données d'Oracle ou du simulateur :
- Logs d'audit (table AUD$)
- Statistiques SQL (V$SQLSTATS)
- Configuration sécurité (DBA_USERS, DBA_ROLES)
- Métriques de performance (V$SYSMETRIC)

**Usage :**
```python
from data_extractor import OracleDataExtractor

# Mode automatique (détecte depuis .env)
extractor = OracleDataExtractor()
extractor.connect()
results = extractor.extract_all()
```

### Module 2 : RAG Setup
**Fichier :** `src/rag_setup.py`

Gère la base de connaissances vectorielle :
- ChromaDB pour le stockage
- Sentence Transformers pour l'embedding
- 15-20 documents Oracle chargés

**Usage :**
```python
from rag_setup import OracleRAGSystem

rag = OracleRAGSystem()
rag.load_documents('data/documents')
context = rag.retrieve_context("optimisation index Oracle", top_k=5)
```

### Module 3 : LLM Engine
**Fichier :** `src/llm_engine.py`

Interface centralisée pour Ollama :
- Support Ollama (local)
- Gestion des prompts via `prompts.yaml`
- Retry automatique et gestion d'erreurs

**Usage :**
```python
from llm_engine import LLMEngine

engine = LLMEngine()
result = engine.analyze_query(sql_text, plan, metrics)
```

### Module 4 : Security Auditor
**Fichier :** `src/security_audit.py`

Audit automatisé de sécurité :
- Score global 0-100
- Détection des risques critiques
- Recommandations OWASP/CIS

**Usage :**
```python
from security_audit import SecurityAuditor

auditor = SecurityAuditor()
results = auditor.audit_full('data/oracle_exports')
auditor.print_summary()
```

### Module 5 : Query Optimizer
**Fichier :** `src/query_optimizer.py`

Optimisation intelligente des requêtes :
- Analyse des plans d'exécution
- Suggestions d'index
- Estimation des gains

**Usage :**
```python
from query_optimizer import QueryOptimizer

optimizer = QueryOptimizer()
results = optimizer.analyze_slow_queries(top_n=10)
optimizer.print_summary()
```

### Module 6 : Anomaly Detector
**Fichier :** `src/anomaly_detector.py`

Détection de menaces cybersécurité :
- SQL Injection
- Escalade de privilèges
- Exfiltration de données
- Accès hors heures

**Usage :**
```python
from anomaly_detector import AnomalyDetector

detector = AnomalyDetector()
results = detector.analyze_logs('data/synthetic_data/audit_logs_synthetic.csv')
detector.print_summary()
```

### Module 7 : Backup Recommender
**Fichier :** `src/backup_recommender.py`

Stratégies de sauvegarde sur mesure :
- Recommandations basées sur RPO/RTO
- Scripts RMAN automatiques
- Planification cron

**Usage :**
```python
from backup_recommender import BackupRecommender

recommender = BackupRecommender()
strategy = recommender.recommend_strategy(
    rpo="1 heure",
    rto="4 heures",
    db_size="500GB",
    criticality="haute",
    budget="moyen"
)
```

### Module 8 : Recovery Guide
**Fichier :** `src/recovery_guide.py`

Playbooks de récupération détaillés :
- 4 scénarios supportés
- Étapes numérotées avec validations
- Commandes RMAN exactes

**Usage :**
```python
from recovery_guide import RecoveryGuide

guide = RecoveryGuide()
playbook = guide.generate_playbook('complete_restore', details)
guide.print_playbook()
```

### Module 9 : Dashboard
**Fichier :** `src/dashboard.py`

Interface web Streamlit :
- 5 pages : Accueil, Sécurité, Performance, Sauvegardes, Chatbot
- Graphiques interactifs (Plotly)
- Chatbot conversationnel

**Lancement :**
```bash
streamlit run src/dashboard.py
```

---

## 🧪 Tests

### Tests Unitaires

```bash
# Installer pytest
pip install pytest pytest-cov

# Lancer tous les tests
pytest tests/ -v

# Avec couverture de code
pytest tests/ --cov=src --cov-report=html
```

### Tests d'Intégration

```bash
# Test du flux complet (mode Mock)
cd src
python -c "
from data_extractor import OracleDataExtractor
from security_audit import SecurityAuditor

extractor = OracleDataExtractor()
extractor.connect()
extractor.extract_all()

auditor = SecurityAuditor()
results = auditor.audit_full('data/oracle_exports')
print(f'Score: {results[\"score_global\"]}/100')
"
```

### Validation des Résultats

**Critères de succès :**
- ✅ Audit sécurité : Score calculé, 3+ risques détectés
- ✅ Optimisation : 5+ requêtes analysées avec recommandations
- ✅ Anomalies : Précision > 85%
- ✅ Dashboard : 5 pages fonctionnelles
- ✅ Chatbot : Répond à 15+ questions types

---

## 🛠️ Technologies Utilisées

### Backend
- **Python 3.11** : Langage principal
- **LangChain** : Framework LLM
- **ChromaDB** : Base vectorielle
- **Pandas** : Manipulation de données
- **cx_Oracle** : Connexion Oracle

### LLM & IA
- **Ollama** : Serveur LLM local (llama2)
- **Sentence Transformers** : Embeddings
- **RAG** : Retrieval-Augmented Generation

### Base de Données
- **Oracle Database XE 21c** : Base de données (via Docker)
- **Mock Oracle** : Simulateur pour tests rapides

### Frontend
- **Streamlit** : Interface web
- **Plotly** : Visualisations interactives

### DevOps
- **Docker** : Conteneurisation Oracle
- **pytest** : Tests unitaires
- **loguru** : Logging
- **python-dotenv** : Gestion des variables d'environnement

---

## 📁 Structure du Projet

```
oracle-ai-platform/
├── src/                          # Code source
│   ├── oracle_connector.py       # Connecteur Oracle/Mock
│   ├── data_extractor.py         # Module 1
│   ├── rag_setup.py              # Module 2
│   ├── llm_engine.py             # Module 3
│   ├── security_audit.py         # Module 4
│   ├── query_optimizer.py        # Module 5
│   ├── anomaly_detector.py       # Module 6
│   ├── backup_recommender.py     # Module 7
│   ├── recovery_guide.py         # Module 8
│   ├── dashboard.py              # Module 9
│   ├── mock_oracle.py            # Simulateur Oracle
│   └── synthetic_logs_generator.py
├── data/                         # Données
│   ├── chroma_db/                # Base vectorielle
│   ├── documents/                # Documents RAG
│   ├── oracle_exports/           # Exports Oracle
│   └── synthetic_data/           # Logs synthétiques
├── tests/                        # Tests unitaires
├── requirements.txt              # Dépendances
├── .env                          # Configuration (à créer)
├── run.sh                        # Script Linux/Mac
├── run.bat                       # Script Windows
└── README.md                     # Cette documentation
```

---

## 🔧 Configuration Avancée

### Personnalisation des Prompts

Éditez `data/prompts.yaml` pour personnaliser les prompts :

```yaml
security.analyze_users:
  system: "Tu es un expert en sécurité Oracle..."
  user: "Analyse cette configuration : {users_data}"
```

### Ajout de Documents RAG

Ajoutez vos propres documents dans `data/documents/` :

```bash
# Ajouter un document
echo "Contenu du document" > data/documents/mon_doc.txt

# Réindexer
cd src
python rag_setup.py
```

### Optimisation d'Ollama

Pour améliorer les performances :

```bash
# Augmenter la mémoire allouée
export OLLAMA_MAX_LOADED_MODELS=2
export OLLAMA_NUM_PARALLEL=4

# Utiliser un modèle plus rapide
ollama pull llama2:7b-chat

# Modifier .env
OLLAMA_MODEL=llama2:7b-chat
```

---

## 📊 Métriques de Performance

### Temps d'Exécution Typiques

| Module | Mode Mock | Mode Oracle | Remarques |
|--------|-----------|-------------|-----------|
| Extraction données | 5-10s | 30-60s | Vues système |
| Audit sécurité | 3-5 min | 8-12 min | Analyse IA complexe |
| Optimisation requêtes | 4-6 min | 8-15 min | Plans d'exécution |
| Détection anomalies | 5-8 min | 10-15 min | 70+ logs |
| Génération stratégie | 1-2 min | 1-2 min | Identique |
| Playbook restauration | 30-60s | 30-60s | Identique |

**Note :** Les temps d'exécution dépendent fortement de :
- La puissance CPU/GPU (Ollama)
- La taille de la base de données (mode Oracle)
- Le modèle LLM utilisé (llama2:7b vs llama2:13b)
- La complexité des analyses demandées

### Coûts

- **Ollama (Local)** : Gratuit, mais nécessite 8 GB+ RAM
- **Hébergement Oracle** : Docker local gratuit, ou cloud payant

---

## ❓ FAQ

**Q : L'application fonctionne sans Oracle installé ?**  
R : Oui ! Utilisez le mode Mock (`USE_MOCK=true`) qui génère des données réalistes. Parfait pour tests et démonstrations.

**Q : Comment choisir entre Mock et Oracle ?**  
R : 
- **Mock** : Tests rapides, démos, développement initial
- **Oracle** : Production, audits réels, données précises

**Q : Ollama est obligatoire ?**  
R : Oui, la plateforme utilise exclusivement Ollama pour le LLM. Installation simple et gratuite.

**Q : Puis-je utiliser un Oracle distant ?**  
R : Oui, configurez `ORACLE_HOST` dans `.env` avec l'IP/hostname du serveur Oracle.

**Q : Les analyses sont-elles sauvegardées ?**  
R : Oui, tous les rapports sont dans `data/oracle_exports/reports/` au format JSON.

**Q : Comment améliorer la vitesse d'analyse ?**  
R : 
- Utilisez un modèle plus léger (`llama2:7b` au lieu de `13b`)
- Augmentez la RAM allouée à Ollama
- Utilisez un GPU si disponible

**Q : Le chatbot garde-t-il la mémoire ?**  
R : Oui, l'historique est conservé pendant la session Streamlit.

**Q : Comment ajouter de nouveaux prompts ?**  
R : Éditez `data/prompts.yaml` et ajoutez vos templates.

---

## 🤝 Contribution

Ce projet est développé dans un cadre académique. Pour contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/NewFeature`)
3. Committez vos changements (`git commit -m 'Add NewFeature'`)
4. Push vers la branche (`git push origin feature/NewFeature`)
5. Ouvrez une Pull Request

---


## 🚀 Démarrage Rapide (Résumé)

```bash
# 1. Installation
git clone <https://github.com/MinaBouzid1/oracle_ai_platform> && cd oracle-ai-platform
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Installer Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama2

# 3. Configuration (mode Mock)
cp .env.example .env
# Vérifier que USE_MOCK=true

# 4. Initialisation
cd src && python mock_oracle.py && python data_extractor.py
python rag_setup.py && python synthetic_logs_generator.py

# 5. Lancement
streamlit run dashboard.py
```

**Développé  pour l'administration Oracle intelligente**