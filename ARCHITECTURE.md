# 🏗️ Architecture Technique - Plateforme Oracle AI

## Vue d'Ensemble

La plateforme est construite selon une architecture modulaire en 3 couches :

```
┌─────────────────────────────────────────────────────────┐
│                   COUCHE PRÉSENTATION                   │
│               Streamlit Dashboard (Module 9)            │
│          Interface Web + Chatbot Conversationnel        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                    COUCHE LOGIQUE                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ Security │  │  Query   │  │ Anomaly  │  │ Backup  ││
│  │  Audit   │  │Optimizer │  │ Detector │  │  Mgmt   ││
│  │(Module 4)│  │(Module 5)│  │(Module 6)│  │(Mod 7-8)││
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └────┬────┘│
│        └──────────────┼─────────────┴──────────── │     │
│                   ┌───▼────────────────────────┐  │     │
│                   │   LLM Engine (Module 3)    │  │     │
│                   │  Prompt Engineering Hub    │  │     │
│                   └───┬────────────────────────┘  │     │
│                       │                            │     │
│                   ┌───▼────┐              ┌───────▼───┐ │
│                   │  RAG   │              │Extracteur │ │
│                   │ChromaDB│              │  Données  │ │
│                   │(Mod 2) │              │ (Module 1)│ │
│                   └────────┘              └───────────┘ │
└─────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────┐
│                    COUCHE DONNÉES                       │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  Oracle DB │  │ Vector Store │  │  Fichiers CSV   │ │
│  │ (Mock/Réel)│  │   ChromaDB   │  │  JSON, Reports  │ │
│  └────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Flux de Données

### 1. Flux d'Audit de Sécurité

```
Oracle DB → Data Extractor → CSV Files
                                  ↓
                            Security Auditor
                                  ↓
                    ┌─────────────┴──────────────┐
                    ↓                            ↓
              LLM Engine                    RAG System
              (Analyse)                  (Contexte docs)
                    ↓                            ↓
                    └─────────────┬──────────────┘
                                  ↓
                          Rapport JSON
                                  ↓
                           Dashboard UI
```

### 2. Flux d'Optimisation de Requêtes

```
V$SQLSTATS → Data Extractor → sql_stats.csv
                                    ↓
                             Query Optimizer
                                    ↓
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
            Récupération Plan              Analyse Métriques
            V$SQL_PLAN                     (Buffer Gets, etc.)
                    ↓                               ↓
                    └───────────────┬───────────────┘
                                    ↓
                              LLM Engine
                       (+ Context RAG index/perf)
                                    ↓
                    Recommandations JSON
                    (Index, Hints, Rewrites)
                                    ↓
                            Dashboard UI
```

### 3. Flux de Détection d'Anomalies

```
Logs Audit → Synthetic/Real Logs → audit_logs.csv
                                          ↓
                                   Anomaly Detector
                                          ↓
                        ┌─────────────────┴────────────────┐
                        ↓                                  ↓
                  Pour chaque log                    RAG Context
                        ↓                         (Patterns attaques)
                   LLM Engine                            ↓
              (Classification)                           ↓
                        └─────────────────┬──────────────┘
                                          ↓
                            Classification JSON
                            (Normal/Suspect/Critique)
                                          ↓
                              Alertes + Dashboard
```

### 4. Flux du Chatbot

```
User Question → Dashboard Input
                      ↓
              RAG System (retrieve_context)
              Recherche top-5 docs pertinents
                      ↓
                  LLM Engine
            (Prompt chatbot.general)
                      ↓
        Context + Question + Historique
                      ↓
              Claude/OpenAI API
                      ↓
                  Réponse
                      ↓
              Chat History + UI
```

---

## Composants Détaillés

### Module 1 : Data Extractor

**Responsabilités :**
- Connexion à Oracle (ou simulateur)
- Extraction de 4 sources de données
- Export en CSV normalisé

**Technologies :**
- `cx_Oracle` / `oracledb` pour la connexion
- `pandas` pour la manipulation
- Mock Oracle pour le développement

**API Publique :**
```python
extractor = OracleDataExtractor(use_mock=True)
extractor.connect()
results = extractor.extract_all(output_dir='data/oracle_exports')
# Retourne: dict avec audit_logs, sql_stats, security_config, performance_metrics
```

**Fichiers générés :**
- `audit_logs.csv` : 100+ logs d'audit
- `sql_stats.csv` : 50+ requêtes SQL avec métriques
- `security_config_users.csv` : Comptes utilisateurs
- `security_config_privileges.csv` : Privilèges système
- `security_config_roles.csv` : Rôles

---

### Module 2 : RAG Setup

**Responsabilités :**
- Gestion de la base de connaissances vectorielle
- Embedding de documents Oracle
- Recherche sémantique (top-k)

**Technologies :**
- ChromaDB : stockage vectoriel persistant
- Sentence Transformers (all-MiniLM-L6-v2) : embedding
- Cosine similarity pour la recherche

**Architecture ChromaDB :**
```
data/chroma_db/
  ├── chroma.sqlite3          # Métadonnées
  └── [UUID]/                 # Vecteurs
```

**API Publique :**
```python
rag = OracleRAGSystem()
rag.load_documents('data/documents')  # Charge 15-20 docs
context = rag.retrieve_context(query, top_k=5)
# Retourne: list[{document, metadata, distance}]
```

**Documents types :**
- `oracle_optimization_basics.txt` : Index, hints, joins
- `oracle_security_best_practices.txt` : OWASP, CIS
- `anomaly_patterns.txt` : SQL injection, escalades
- `backup_strategies.txt` : RMAN, RPO/RTO
- `recovery_procedures.txt` : Restore, PITR

---

### Module 3 : LLM Engine

**Responsabilités :**
- Interface unifiée pour tous les LLM
- Gestion centralisée des prompts (prompts.yaml)
- Retry logic et error handling
- Support multi-provider (Claude, OpenAI, Ollama)

**Architecture Prompts :**
```yaml
module.action:
  system: "System prompt..."
  user: "User prompt avec {variables}"
  examples:  # Few-shot learning
    - input: "..."
      output: "..."
```

**Méthodes spécialisées :**
```python
engine = LLMEngine()

# Optimisation
engine.analyze_query(sql_text, plan, metrics, context)

# Sécurité
engine.assess_security(config_data, config_type, context)

# Anomalies
engine.detect_anomaly(log_entry, historical_context, rag_context)

# Backup
engine.recommend_backup(requirements, context)

# Recovery
engine.guide_recovery(scenario, details, context)

# Chat
engine.chat(user_question, chat_history, context)
```

**Gestion des erreurs :**
- Max 3 retries avec exponential backoff
- Fallback sur erreur JSON parsing
- Logging détaillé (loguru)

---

### Module 4 : Security Auditor

**Responsabilités :**
- Audit de 3 catégories (users, privileges, profiles)
- Scoring 0-100
- Classification des risques (critique/haut/moyen/faible)

**Algorithme de scoring :**
```
Score = 100 - (risques_critiques * 15) - (risques_hauts * 10) 
            - (risques_moyens * 5) - (risques_faibles * 2)
Score = max(0, min(100, Score))
```

**Détection de patterns :**
- Profil DEFAULT sans restrictions
- Privilèges DROP ANY, ALTER SYSTEM
- Comptes inactifs avec privilèges élevés
- Mots de passe sans expiration

**Output :**
```json
{
  "score_global": 72,
  "niveau_risque_global": "moyen",
  "audits": {
    "users": {...},
    "privileges": {...},
    "profiles": {...}
  },
  "resume": {
    "total_risques": 15,
    "risques_critiques": 2,
    "top_3_risques": [...]
  }
}
```

---

### Module 5 : Query Optimizer

**Responsabilités :**
- Identification des requêtes lentes
- Analyse des plans d'exécution
- Suggestions d'optimisations concrètes

**Critères de détection :**
- `ELAPSED_TIME > threshold` (défaut 500ms)
- `BUFFER_GETS / ROWS_PROCESSED > 100`
- `DISK_READS` élevés

**Optimisations proposées :**
1. **Index Suggestions**
   - B-tree pour haute cardinalité
   - Bitmap pour basse cardinalité
   - Composite pour WHERE multi-colonnes

2. **Query Rewrites**
   - Remplacement SELECT * par colonnes spécifiques
   - Ajout de hints (INDEX, PARALLEL)
   - Refactoring des sous-requêtes

3. **Schema Changes**
   - Partitionnement de tables
   - Statistiques à mettre à jour

**Output :**
```json
{
  "sql_id": "sql_0001",
  "resume": "Table full scan sur 1M lignes",
  "optimisations": [
    {
      "titre": "Créer un index sur DEPARTMENT_ID",
      "priorite": "haute",
      "implementation": "CREATE INDEX idx_dept ON employees(department_id);",
      "gain_estime": "80% réduction temps"
    }
  ]
}
```

---

### Module 6 : Anomaly Detector

**Responsabilités :**
- Classification de logs (normal/suspect/critique)
- Détection de 5 types d'attaques
- Calcul de confiance et sévérité

**Types d'anomalies détectées :**

1. **SQL Injection**
   - Patterns : `OR 1=1`, `'; DROP`, `UNION SELECT`
   - Sévérité : 8-10/10

2. **Privilege Escalation**
   - Actions : GRANT SYSDBA, CREATE USER par non-DBA
   - Sévérité : 9-10/10

3. **Data Exfiltration**
   - SELECT massif sur tables sensibles
   - Accès hors heures
   - Sévérité : 7-9/10

4. **Off-Hours Access**
   - Connexions 0h-6h ou week-end
   - Sur objets critiques
   - Sévérité : 5-7/10

5. **Brute Force**
   - Multiples FAILED LOGIN
   - Même IP, différents users
   - Sévérité : 6-8/10

**Métriques de performance :**
- Accuracy : 85-95%
- Precision : 80-90%
- Recall : 85-95%
- F1-Score : 85-92%

---

### Module 7 : Backup Recommender

**Responsabilités :**
- Recommandation de stratégies personnalisées
- Génération de scripts RMAN
- Planification cron

**Paramètres de décision :**
```
RPO + RTO → Type de backup
Criticité → Fréquence
DB Size → Parallélisme RMAN
Budget → Compression, stockage
```

**Matrice de stratégies :**

| RPO | RTO | Type | Fréquence Complete | Fréquence Incr. | Archive Logs |
|-----|-----|------|-------------------|-----------------|--------------|
| 15min | 1h | Incr | Quotidienne | Horaire | 15 min |
| 1h | 4h | Incr | Hebdomadaire | Quotidienne | Horaire |
| 4h | 8h | Diff | Hebdomadaire | Quotidienne | Quotidienne |
| 1j | 1j | Full | Hebdomadaire | - | - |

**Scripts générés :**
- Configuration RMAN
- Full backup script
- Incremental backup script
- Archive log backup script
- Crontab entries

---

### Module 8 : Recovery Guide

**Responsabilités :**
- Playbooks de récupération détaillés
- 4 scénarios supportés
- Estimation de durée et risques

**Scénarios :**

1. **Complete Restore** (2-6h, risque élevé)
   - Crash total de la base
   - Restore from backup + apply archive logs
   - Commandes : STARTUP NOMOUNT, RESTORE DATABASE, RECOVER DATABASE

2. **Point-In-Time Recovery** (1-4h, risque moyen)
   - Récupération à une date/heure précise
   - Commandes : RECOVER DATABASE UNTIL TIME

3. **Table Recovery** (15-60min, risque faible)
   - Table DROP/TRUNCATE par erreur
   - Flashback Table ou RMAN Table Recovery

4. **Tablespace Recovery** (30min-2h, risque moyen)
   - Corruption ou suppression de tablespace
   - Commandes : RESTORE TABLESPACE, RECOVER TABLESPACE

**Structure Playbook :**
```json
{
  "scenario": "complete_restore",
  "metadata": {
    "estimated_duration": "2-6 heures",
    "risk_level": "ÉLEVÉ",
    "prerequisites": [...]
  },
  "content": "Étapes numérotées avec validations..."
}
```

---

### Module 9 : Dashboard

**Responsabilités :**
- Interface utilisateur web
- 5 pages fonctionnelles
- Chatbot conversationnel

**Pages :**

1. **🏠 Accueil**
   - Métriques clés (score, requêtes lentes, anomalies, backup)
   - Alertes critiques
   - Graphiques de tendances (7 jours)
   - Activité récente

2. **🔒 Sécurité**
   - Lancement d'audit
   - Jauge de score
   - Top 3 risques détaillés
   - Détails par catégorie (tabs)

3. **⚡ Performance**
   - Analyse de requêtes lentes
   - Plans d'exécution formatés
   - Optimisations prioritaires
   - Scripts SQL prêts à exécuter

4. **💾 Sauvegardes**
   - Formulaire exigences (RPO/RTO)
   - Stratégie recommandée
   - Scripts RMAN
   - Playbooks de restauration

5. **💬 Chatbot**
   - Questions suggérées
   - Historique de conversation
   - Context enrichi via RAG
   - Réponses en temps réel

**Technologies UI :**
- Streamlit : framework web
- Plotly : graphiques interactifs
- CSS personnalisé : styling
- Session state : état de l'application

---

## Patterns de Conception

### 1. Singleton Pattern (LLM Engine, RAG)
```python
@st.cache_resource
def init_components():
    return {
        'llm': LLMEngine(),  # Instancié une seule fois
        'rag': OracleRAGSystem()
    }
```

### 2. Strategy Pattern (LLM Providers)
```python
if provider == 'claude':
    response = self.client.messages.create(...)
elif provider == 'openai':
    response = self.client.chat.completions.create(...)
elif provider == 'ollama':
    response = requests.post(...)
```

### 3. Template Method (Module Analysis)
```python
def analyze():
    data = extract_data()
    context = retrieve_context(data)
    result = llm_analyze(data, context)
    save_result(result)
    return result
```

### 4. Observer Pattern (Dashboard Updates)
```python
if st.button("Lancer Audit"):
    st.session_state.run_audit = True
    st.rerun()
```

---

## Sécurité

### 1. Gestion des Clés API
- Fichier `.env` (gitignored)
- Variables d'environnement
- Jamais hardcodées

### 2. Validation des Inputs
```python
# Validation SQL
if ';' in user_input or '--' in user_input:
    raise ValueError("Input suspect")

# Validation paths
if '..' in filepath:
    raise ValueError("Path traversal détecté")
```

### 3. Logging
- Pas de logs de données sensibles
- Masquage des clés API dans les logs
- Utilisation de loguru avec niveaux (INFO/WARNING/ERROR)

---

## Performance

### 1. Caching
```python
@st.cache_resource  # Composants (LLM, RAG)
@st.cache_data      # Données (CSV, JSON)
```

### 2. Lazy Loading
- Documents RAG chargés à la demande
- Plans d'exécution fetchés au besoin

### 3. Batching
- Analyse de logs par batch de 10
- Requêtes SQL analysées séquentiellement (éviter rate limits)

### 4. Optimisations
- Embeddings pré-calculés (ChromaDB)
- Requêtes SQL avec FETCH FIRST N ROWS
- Compression des backups RMAN

---

## Scalabilité

### Limitations Actuelles
- SQLite ChromaDB : ~100K documents max
- Streamlit : 1 instance = 1 utilisateur concurrent
- LLM API : rate limits (RPM/TPM)

### Évolutions Possibles
1. **ChromaDB → Pinecone/Weaviate** (millions de vecteurs)
2. **Streamlit → FastAPI + React** (multi-utilisateurs)
3. **LLM local (Ollama)** → Pas de rate limits
4. **Base Oracle réelle** → Connexion production
5. **Kubernetes deployment** → Haute disponibilité

---

## Monitoring & Observabilité

### Logs
```
logs/
  ├── app.log           # Logs application
  ├── llm_calls.log     # Appels LLM (debug)
  └── errors.log        # Erreurs uniquement
```

### Métriques à Suivre
- Temps de réponse LLM (p50, p95, p99)
- Taux d'erreur par module
- Nombre d'audits/optimisations par jour
- Précision détection anomalies

### Alertes
- Score sécurité < 50
- Anomalie critique détectée
- Échec de backup
- Erreur LLM répétée

---

## Déploiement

### Environnements

1. **Développement** (local)
   - Mock Oracle
   - Ollama (LLM local)
   - ChromaDB SQLite

2. **Test** (staging)
   - Oracle test
   - Claude API (quota limité)
   - ChromaDB partagé

3. **Production** (si déployé)
   - Oracle production (read-only)
   - Claude API (quota élevé)
   - Pinecone/Weaviate
   - Load balancer

### CI/CD (Proposition)
```yaml
# .github/workflows/ci.yml
- name: Tests
  run: pytest tests/ --cov=src
- name: Linting
  run: flake8 src/
- name: Deploy
  run: |
    docker build -t oracle-ai .
    docker push registry/oracle-ai:latest
```

---

## Conclusion

Cette architecture modulaire permet :
- ✅ Séparation des responsabilités
- ✅ Testabilité indépendante des modules
- ✅ Extensibilité (nouveaux modules facilement intégrables)
- ✅ Maintenabilité (code organisé, documenté)
- ✅ Scalabilité (évolutions possibles identifiées)

**Diagramme de dépendances :**
```
Dashboard (9)
    ├─> LLM Engine (3)
    │       └─> Prompts YAML
    ├─> RAG System (2)
    │       └─> ChromaDB
    ├─> Data Extractor (1)
    │       └─> Oracle DB
    ├─> Security Auditor (4)
    │       ├─> LLM Engine (3)
    │       └─> RAG System (2)
    ├─> Query Optimizer (5)
    │       ├─> LLM Engine (3)
    │       ├─> RAG System (2)
    │       └─> Data Extractor (1)
    ├─> Anomaly Detector (6)
    │       ├─> LLM Engine (3)
    │       └─> RAG System (2)
    ├─> Backup Recommender (7)
    │       ├─> LLM Engine (3)
    │       └─> RAG System (2)
    └─> Recovery Guide (8)
            ├─> LLM Engine (3)
            └─> RAG System (2)
```

**Modules centraux utilisés par tous :**
- Module 3 (LLM Engine) : 6 dépendances
- Module 2 (RAG System) : 6 dépendances
- Module 1 (Data Extractor) : 2 dépendances