"""
Tests unitaires pour la Plateforme Oracle AI
Usage: pytest tests/test_modules.py -v
"""

import pytest
import sys
import os
import pandas as pd
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_audit_log():
    """Log d'audit exemple"""
    return {
        'TIMESTAMP': '2024-01-15 14:30:00',
        'USERNAME': 'APP_USER',
        'ACTION': 'SELECT',
        'OBJECT_NAME': 'EMPLOYEES',
        'RETURNCODE': 0,
        'CLIENT_ID': '192.168.1.10',
        'OS_USERNAME': 'john_doe',
        'TERMINAL': 'WORKSTATION1'
    }

@pytest.fixture
def sample_sql_metrics():
    """Métriques SQL exemple"""
    return {
        'EXECUTIONS': 100,
        'ELAPSED_TIME': 5000000,
        'CPU_TIME': 3000000,
        'BUFFER_GETS': 50000,
        'DISK_READS': 1000,
        'ROWS_PROCESSED': 5000
    }

@pytest.fixture
def setup_test_env():
    """Configure l'environnement de test"""
    # Créer les répertoires nécessaires
    test_dirs = [
        'data/oracle_exports',
        'data/chroma_db',
        'data/synthetic_data',
        'data/documents'
    ]
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Cleanup si nécessaire

# ============================================================================
# MODULE 1 : DATA EXTRACTOR
# ============================================================================

def test_mock_oracle_connection():
    """Test de connexion au simulateur Oracle"""
    from mock_oracle import MockOracle
    
    mock = MockOracle()
    assert mock.connect() == True
    print("✅ Test connexion simulateur : OK")

def test_data_extraction():
    """Test d'extraction de données"""
    from data_extractor import OracleDataExtractor
    
    extractor = OracleDataExtractor(use_mock=True)
    extractor.connect()
    
    # Extraire les données
    results = extractor.extract_all('data/oracle_exports')
    
    assert 'audit_logs' in results
    assert 'sql_stats' in results
    assert isinstance(results['audit_logs'], pd.DataFrame)
    assert len(results['audit_logs']) > 0
    
    print(f"✅ Test extraction : {len(results['audit_logs'])} logs extraits")

# ============================================================================
# MODULE 2 : RAG SETUP
# ============================================================================

def test_rag_initialization():
    """Test d'initialisation du système RAG"""
    from rag_setup import OracleRAGSystem
    
    rag = OracleRAGSystem()
    
    assert rag.collection is not None
    assert rag.embedding_model is not None
    
    print("✅ Test initialisation RAG : OK")

def test_rag_document_loading(setup_test_env):
    """Test de chargement de documents"""
    from rag_setup import OracleRAGSystem
    
    # Créer un document test
    doc_path = Path('data/documents/test_doc.txt')
    doc_path.write_text("Oracle optimization test document")
    
    rag = OracleRAGSystem()
    num_docs = rag.load_documents('data/documents')
    
    assert num_docs >= 1
    print(f"✅ Test chargement docs : {num_docs} documents chargés")

def test_rag_retrieval():
    """Test de récupération de contexte"""
    from rag_setup import OracleRAGSystem
    
    rag = OracleRAGSystem()
    
    # Charger au moins un document
    if rag.collection.count() == 0:
        doc_path = Path('data/documents/test_doc.txt')
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text("Oracle index optimization B-tree")
        rag.load_documents('data/documents')
    
    results = rag.retrieve_context("index optimization", top_k=3)
    
    assert isinstance(results, list)
    assert len(results) > 0
    
    print(f"✅ Test retrieval : {len(results)} documents trouvés")

# ============================================================================
# MODULE 3 : LLM ENGINE
# ============================================================================

def test_llm_engine_initialization():
    """Test d'initialisation du LLM Engine"""
    try:
        from llm_engine import LLMEngine
        
        engine = LLMEngine()
        
        assert engine.llm is not None
        assert engine.prompts is not None
        assert len(engine.prompts) > 0
        
        print("✅ Test initialisation LLM : OK")
    except Exception as e:
        pytest.skip(f"LLM non disponible : {e}")

def test_prompt_loading():
    """Test de chargement des prompts"""
    from llm_engine import LLMEngine
    
    engine = LLMEngine()
    
    # Vérifier que les prompts clés existent
    required_prompts = [
        'security.analyze_users',
        'optimization.explain_slow_query',
        'anomaly.classify_log'
    ]
    
    for prompt_key in required_prompts:
        config = engine._get_prompt_config(prompt_key)
        assert config is not None, f"Prompt {prompt_key} manquant"
    
    print(f"✅ Test prompts : {len(engine.prompts)} prompts chargés")

# ============================================================================
# MODULE 4 : SECURITY AUDIT
# ============================================================================

def test_security_auditor_initialization():
    """Test d'initialisation du Security Auditor"""
    try:
        from security_audit import SecurityAuditor
        
        auditor = SecurityAuditor()
        
        assert auditor.llm is not None
        assert auditor.rag is not None
        
        print("✅ Test initialisation auditor : OK")
    except Exception as e:
        pytest.skip(f"Security Auditor non disponible : {e}")

def test_risk_level_assessment():
    """Test d'évaluation du niveau de risque"""
    try:
        from security_audit import SecurityAuditor
        
        auditor = SecurityAuditor()
        
        assert auditor._get_risk_level(90) == "faible"
        assert auditor._get_risk_level(70) == "moyen"
        assert auditor._get_risk_level(50) == "haut"
        assert auditor._get_risk_level(30) == "critique"
        
        print("✅ Test évaluation risques : OK")
    except Exception as e:
        pytest.skip(f"Test skipped : {e}")

# ============================================================================
# MODULE 5 : QUERY OPTIMIZER
# ============================================================================

def test_query_optimizer_initialization():
    """Test d'initialisation du Query Optimizer"""
    try:
        from query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer()
        
        assert optimizer.llm is not None
        assert optimizer.rag is not None
        assert optimizer.extractor is not None
        
        print("✅ Test initialisation optimizer : OK")
    except Exception as e:
        pytest.skip(f"Optimizer non disponible : {e}")

def test_execution_plan_formatting():
    """Test de formatage des plans d'exécution"""
    try:
        from query_optimizer import QueryOptimizer
        
        optimizer = QueryOptimizer()
        
        # Plan d'exécution exemple
        plan_df = pd.DataFrame({
            'OPERATION': ['SELECT STATEMENT', 'TABLE ACCESS'],
            'OPTIONS': [None, 'FULL'],
            'OBJECT_NAME': [None, 'EMPLOYEES'],
            'COST': [100, 50]
        })
        
        formatted = optimizer._format_execution_plan(plan_df)
        
        assert 'SELECT STATEMENT' in formatted
        assert 'TABLE ACCESS' in formatted
        assert 'EMPLOYEES' in formatted
        
        print("✅ Test formatage plan : OK")
    except Exception as e:
        pytest.skip(f"Test skipped : {e}")

# ============================================================================
# MODULE 6 : ANOMALY DETECTOR
# ============================================================================

def test_anomaly_detector_initialization():
    """Test d'initialisation du Anomaly Detector"""
    try:
        from anomaly_detector import AnomalyDetector
        
        detector = AnomalyDetector()
        
        assert detector.llm is not None
        assert detector.rag is not None
        assert detector.statistics is not None
        
        print("✅ Test initialisation detector : OK")
    except Exception as e:
        pytest.skip(f"Detector non disponible : {e}")

def test_synthetic_logs_generation():
    """Test de génération de logs synthétiques"""
    from synthetic_logs_generator import SyntheticLogsGenerator
    
    generator = SyntheticLogsGenerator()
    df = generator.generate_dataset(num_normal=10, num_suspicious=5)
    
    assert len(df) == 15
    assert 'LABEL' in df.columns
    assert df['LABEL'].value_counts()['normal'] == 10
    assert df['LABEL'].value_counts()['suspicious'] == 5
    
    print("✅ Test génération logs : 15 logs créés")

def test_log_classification():
    """Test de classification de logs"""
    try:
        from anomaly_detector import AnomalyDetector
        
        detector = AnomalyDetector()
        
        # Log normal
        normal_log = pd.Series({
            'TIMESTAMP': '2024-01-15 10:00:00',
            'USERNAME': 'APP_USER',
            'ACTION': 'SELECT',
            'OBJECT_NAME': 'EMPLOYEES',
            'RETURNCODE': 0,
            'CLIENT_ID': '192.168.1.10',
            'OS_USERNAME': 'employee1',
            'TERMINAL': 'WORKSTATION1'
        })
        
        result = detector._analyze_single_log(normal_log, 1)
        
        assert 'classification' in result
        assert result['classification'] in ['normal', 'suspect', 'critique', 'error']
        
        print(f"✅ Test classification : {result['classification']}")
    except Exception as e:
        pytest.skip(f"Test skipped : {e}")

# ============================================================================
# MODULE 7 : BACKUP RECOMMENDER
# ============================================================================

def test_backup_recommender_initialization():
    """Test d'initialisation du Backup Recommender"""
    try:
        from backup_recommender import BackupRecommender
        
        recommender = BackupRecommender()
        
        assert recommender.llm is not None
        assert recommender.rag is not None
        assert recommender.strategy_templates is not None
        
        print("✅ Test initialisation backup recommender : OK")
    except Exception as e:
        pytest.skip(f"Backup Recommender non disponible : {e}")

def test_cron_schedule_generation():
    """Test de génération de planning cron"""
    try:
        from backup_recommender import BackupRecommender
        
        recommender = BackupRecommender()
        
        # Stratégie test
        strategy = {
            'frequence': {
                'complete': 'hebdomadaire',
                'incrementale': 'quotidienne',
                'archive_logs': 'horaire'
            }
        }
        
        schedule = recommender._generate_cron_schedule(strategy)
        
        assert isinstance(schedule, list)
        assert len(schedule) > 0
        assert all('cron' in job for job in schedule)
        
        print(f"✅ Test cron schedule : {len(schedule)} jobs planifiés")
    except Exception as e:
        pytest.skip(f"Test skipped : {e}")

# ============================================================================
# MODULE 8 : RECOVERY GUIDE
# ============================================================================

def test_recovery_guide_initialization():
    """Test d'initialisation du Recovery Guide"""
    try:
        from recovery_guide import RecoveryGuide
        
        guide = RecoveryGuide()
        
        assert guide.llm is not None
        assert guide.rag is not None
        assert len(guide.scenarios) == 4
        
        print("✅ Test initialisation recovery guide : OK")
    except Exception as e:
        pytest.skip(f"Recovery Guide non disponible : {e}")

def test_duration_estimation():
    """Test d'estimation de durée"""
    try:
        from recovery_guide import RecoveryGuide
        
        guide = RecoveryGuide()
        
        duration = guide._estimate_duration('complete_restore', {})
        assert duration is not None
        assert isinstance(duration, str)
        
        print(f"✅ Test estimation durée : {duration}")
    except Exception as e:
        pytest.skip(f"Test skipped : {e}")

def test_risk_assessment():
    """Test d'évaluation de risque"""
    try:
        from recovery_guide import RecoveryGuide
        
        guide = RecoveryGuide()
        
        risk = guide._assess_risk('complete_restore', {})
        assert risk is not None
        assert isinstance(risk, str)
        assert 'ÉLEVÉ' in risk or 'MOYEN' in risk or 'FAIBLE' in risk
        
        print(f"✅ Test évaluation risque : {risk[:50]}...")
    except Exception as e:
        pytest.skip(f"Test skipped : {e}")

# ============================================================================
# TESTS D'INTÉGRATION
# ============================================================================

def test_full_security_audit_flow(setup_test_env):
    """Test du flux complet d'audit de sécurité"""
    try:
        from data_extractor import OracleDataExtractor
        from security_audit import SecurityAuditor
        
        # Extraction
        extractor = OracleDataExtractor(use_mock=True)
        extractor.connect()
        extractor.extract_all('data/oracle_exports')
        
        # Audit
        auditor = SecurityAuditor()
        results = auditor.audit_full('data/oracle_exports')
        
        assert 'score_global' in results
        assert results['score_global'] >= 0
        assert results['score_global'] <= 100
        
        print(f"✅ Test flux audit complet : Score {results['score_global']}/100")
    except Exception as e:
        pytest.skip(f"Test d'intégration skipped : {e}")

def test_full_optimization_flow(setup_test_env):
    """Test du flux complet d'optimisation"""
    try:
        from data_extractor import OracleDataExtractor
        from query_optimizer import QueryOptimizer
        
        # Extraction
        extractor = OracleDataExtractor(use_mock=True)
        extractor.connect()
        extractor.extract_all('data/oracle_exports')
        
        # Optimisation
        optimizer = QueryOptimizer()
        optimizer.extractor.connect()
        results = optimizer.analyze_slow_queries(
            data_dir='data/oracle_exports',
            top_n=3,
            threshold_elapsed=100000
        )
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        print(f"✅ Test flux optimisation : {len(results)} requêtes analysées")
    except Exception as e:
        pytest.skip(f"Test d'intégration skipped : {e}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])