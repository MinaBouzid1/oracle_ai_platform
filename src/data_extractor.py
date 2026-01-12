"""
Module 1 : Data Extractor - Version Production
Extraction depuis Oracle Database réel via Docker
"""

import os
import pandas as pd
from dotenv import load_dotenv
from loguru import logger
import sys
from pathlib import Path
import json

# Import du connecteur Oracle
from oracle_connector import OracleConnector

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

load_dotenv()


class OracleDataExtractor:
    """Extraction de données depuis Oracle Database"""
    
    def __init__(self, use_mock: bool = False):
        """
        Args:
            use_mock: Si True, utilise le simulateur, sinon Oracle réel
        """
        self.use_mock = use_mock
        self.export_dir = Path("data/oracle_exports")
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        if not use_mock:
            # Configuration Oracle depuis .env ou valeurs par défaut
            self.oracle = OracleConnector(
                host=os.getenv("ORACLE_HOST", "localhost"),
                port=int(os.getenv("ORACLE_PORT", 1521)),
                service_name=os.getenv("ORACLE_SERVICE", "XEPDB1"),
                user=os.getenv("ORACLE_USER", "system"),
                password=os.getenv("ORACLE_PASSWORD", "oracle")
            )
        else:
            from mock_oracle import MockOracle
            self.oracle = MockOracle()
    
    def extract_all(self):
        """Extrait toutes les données Oracle"""
        logger.info("🚀 Démarrage de l'extraction Oracle Database")
        logger.info("=" * 60)
        
        # Connexion
        if not self.use_mock:
            if not self.oracle.connect():
                logger.error("❌ Impossible de se connecter à Oracle")
                return False
        
        try:
            # 1. Logs d'audit
            audit_logs = self.oracle.get_audit_logs(limit=100)
            audit_path = self.export_dir / "audit_logs.csv"
            audit_logs.to_csv(audit_path, index=False)
            logger.success(f"✅ Logs d'audit : {len(audit_logs)} lignes → {audit_path}")
            
            # 2. Statistiques SQL
            sql_stats = self.oracle.get_sql_statistics(limit=50)
            sql_path = self.export_dir / "sql_stats.csv"
            sql_stats.to_csv(sql_path, index=False)
            logger.success(f"✅ Stats SQL : {len(sql_stats)} lignes → {sql_path}")
            
            # 3. Requêtes lentes
            slow_queries = self.oracle.get_slow_queries(min_elapsed_sec=0.1, limit=20)
            slow_path = self.export_dir / "slow_queries.csv"
            slow_queries.to_csv(slow_path, index=False)
            logger.success(f"✅ Requêtes lentes : {len(slow_queries)} lignes → {slow_path}")
            
            # 4. Utilisateurs et rôles
            users_data = self.oracle.get_users_and_roles()
            
            users_path = self.export_dir / "users.csv"
            users_data['users'].to_csv(users_path, index=False)
            logger.success(f"✅ Utilisateurs : {len(users_data['users'])} lignes → {users_path}")
            
            roles_path = self.export_dir / "user_roles.csv"
            users_data['roles'].to_csv(roles_path, index=False)
            logger.success(f"✅ Rôles : {len(users_data['roles'])} lignes → {roles_path}")
            
            # 5. Privilèges système
            sys_privs = self.oracle.get_system_privileges()
            privs_path = self.export_dir / "system_privileges.csv"
            sys_privs.to_csv(privs_path, index=False)
            logger.success(f"✅ Privilèges : {len(sys_privs)} lignes → {privs_path}")
            
            # 6. Tablespaces
            tablespaces = self.oracle.get_tablespace_usage()
            ts_path = self.export_dir / "tablespaces.csv"
            tablespaces.to_csv(ts_path, index=False)
            logger.success(f"✅ Tablespaces : {len(tablespaces)} lignes → {ts_path}")
            
            # 7. Taille de la base
            db_size = self.oracle.get_database_size()
            size_path = self.export_dir / "database_metrics.json"
            with open(size_path, 'w') as f:
                json.dump(db_size, f, indent=2)
            logger.success(f"✅ Métriques DB → {size_path}")
            
            logger.success("=" * 60)
            logger.success("✅ EXTRACTION TERMINÉE")
            logger.info("\n📊 RÉSUMÉ:")
            logger.info(f"   - Logs d'audit: {len(audit_logs)}")
            logger.info(f"   - Statistiques SQL: {len(sql_stats)}")
            logger.info(f"   - Requêtes lentes: {len(slow_queries)}")
            logger.info(f"   - Utilisateurs: {len(users_data['users'])}")
            logger.info(f"   - Rôles: {len(users_data['roles'])}")
            logger.info(f"   - Privilèges: {len(sys_privs)}")
            logger.info(f"   - Tablespaces: {len(tablespaces)}")
            logger.info(f"   - Taille DB: {db_size['total_size_gb']:.2f} GB")
            
            return True
            
        finally:
            if not self.use_mock:
                self.oracle.disconnect()


if __name__ == "__main__":
    # Extraction depuis Oracle réel
    extractor = OracleDataExtractor(use_mock=False)
    extractor.extract_all()