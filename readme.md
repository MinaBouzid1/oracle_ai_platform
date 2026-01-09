# 🗄️ Plateforme Intelligente de Gestion Oracle avec IA

Plateforme complète d'administration Oracle Database assistée par Intelligence Artificielle (LLM + RAG), développée dans le cadre d'un projet académique.

## 📋 Table des Matières

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
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
│Modules  │ │ LLM   │ │Vector DB│  │ Oracle  │
│(9x)     │ │Engine │ │(Chroma) │  │ Mock/DB │
└─────────┘ └───────┘ └─────────┘  └─────────┘
```

### 9 Modules Principaux

1. **Data Extractor** : Extraction des données Oracle
2. **RAG Setup** : Base de connaissances vectorielle
3. **LLM Engine** : Interface centralisée pour le LLM
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
- Clé API : Claude (Anthropic) OU OpenAI OU Ollama (local)
- 2 GB d'espace disque
- 4 GB RAM minimum

### Installation Rapide

```bash
# 1. Cloner le projet
git clone <votre-repo>
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

# 5. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et ajouter votre clé API

# 6. Initialiser les données
cd src
python mock_oracle.py
python data_extractor.py
python rag_setup.py
python synthetic_logs_generator.py
cd ..
```

### Configuration du LLM

Éditez `.env` et choisissez votre provider :

**Option A : Claude (Recommandé)**
```bash
ANTHROPIC_API_KEY=sk-ant-votre-cle-ici
LLM_PROVIDER=claude
```

**Option B : OpenAI**
```bash
OPENAI_API_KEY=sk-votre-cle-ici
LLM_PROVIDER=openai
```

**Option C : Ollama (Local gratuit)**
```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
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

Extrait les données d'Oracle (ou simulateur) :
- Logs d'audit (table AUD$)
- Statistiques SQL (V$SQLSTATS)
- Configuration sécurité (DBA_USERS, DBA_ROLES)
- Métriques de performance (V$SYSMETRIC)

**Usage :**
```python
from data_extractor import OracleDataExtractor

extractor = OracleDataExtractor(use_mock=True)
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

Interface centralisée pour tous les appels LLM :
- Support Claude, OpenAI, Ollama
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
# Test du flux complet
cd src
python -c "
from data_extractor import OracleDataExtractor
from security_audit import SecurityAuditor

extractor = OracleDataExtractor(use_mock=True)
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
- **Claude Sonnet 4** : LLM principal (Anthropic)
- **Sentence Transformers** : Embeddings
- **RAG** : Retrieval-Augmented Generation

### Frontend
- **Streamlit** : Interface web
- **Plotly** : Visualisations interactives

### DevOps
- **pytest** : Tests unitaires
- **loguru** : Logging
- **python-dotenv** : Gestion des variables d'environnement

---

## 📁 Structure du Projet

```
oracle-ai-platform/
├── src/                          # Code source
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

### Connexion à un Oracle Réel

Éditez `.env` :

```bash
ORACLE_HOST=votre-host
ORACLE_PORT=1521
ORACLE_SERVICE=ORCL
ORACLE_USER=system
ORACLE_PASSWORD=votre-mot-de-passe
```

Dans le code :
```python
extractor = OracleDataExtractor(use_mock=False)  # Utiliser Oracle réel
```

---

## 📊 Métriques de Performance

### Temps d'Exécution Typiques

| Module | Temps moyen | Remarques |
|--------|-------------|-----------|
| Extraction données | 5-10s | Simulateur |
| Audit sécurité | 30-45s | 3 catégories |
| Optimisation requêtes | 1-2 min | 10 requêtes |
| Détection anomalies | 2-3 min | 70 logs |
| Génération stratégie | 15-30s | 1 stratégie |
| Playbook restauration | 10-20s | 1 scénario |

### Coûts API (estimés)

- **Claude Sonnet 4** : ~$0.50-2.00 par session complète
- **OpenAI GPT-3.5** : ~$0.30-1.50 par session
- **Ollama** : Gratuit (local)

---

## ❓ FAQ

**Q : L'application fonctionne sans Oracle installé ?**  
R : Oui ! Le simulateur `mock_oracle.py` génère des données réalistes.

**Q : Puis-je utiliser sans clé API ?**  
R : Oui, avec Ollama (local). Installez Ollama et configurez `LLM_PROVIDER=ollama`.

**Q : Les données sont-elles sauvegardées ?**  
R : Oui, tous les rapports sont dans `data/oracle_exports/reports/`.

**Q : Comment ajouter de nouveaux prompts ?**  
R : Éditez `data/prompts.yaml` et ajoutez vos templates.

**Q : Le chatbot garde-t-il la mémoire ?**  
R : Oui, l'historique est conservé pendant la session Streamlit.

---

## 🤝 Contribution

Ce projet est développé dans un cadre académique. Pour contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier `LICENSE` pour plus de détails.

---

## 👥 Auteurs

- **[Votre Nom]** - Développement complet
- **Encadrant** : [Nom de l'encadrant]
- **Institution** : [Nom de l'université/école]

---

## 🙏 Remerciements

- Anthropic pour l'API Claude
- Oracle Corporation pour la documentation
- Communauté Streamlit
- Professeurs et encadrants du projet

---

## 📞 Support

Pour toute question ou problème :
- 📧 Email : votre-email@example.com
- 🐛 Issues : [GitHub Issues](https://github.com/votre-repo/issues)
- 📚 Documentation : Ce README

---

**Développé avec ❤️ pour l'administration Oracle intelligente**