"""
Module 1 : Data Extractor
Extraction des données depuis Oracle (ou simulateur)
"""

import os
import pandas as pd
from dotenv import load_dotenv
from loguru import logger
import sys

# Configuration du logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

load_dotenv()

class OracleDataExtractor:
    """Extracteur de données Oracle avec fallback sur simulateur"""
    
    def __init__(self, use_mock=True):
        """
        Args:
            use_mock: Si True, utilise le simulateur au lieu d'Oracle réel
        """
        self.use_mock = use_mock
        self.connection = None
        self.data_cache = {}
        
        logger.info("🚀 Initialisation de l'extracteur de données")
        
    def connect(self):
        """Établit la connexion à Oracle ou au simulateur"""
        if self.use_mock:
            logger.info("📦 Utilisation du simulateur Oracle")
            from mock_oracle import MockOracle
            self.connection = MockOracle()
            self.connection.connect()
        else:
            logger.info("🔌 Connexion à Oracle réel")
            try:
                import oracledb
                self.connection = oracledb.connect(
                    user=os.getenv('ORACLE_USER'),
                    password=os.getenv('ORACLE_PASSWORD'),
                    host=os.getenv('ORACLE_HOST'),
                    port=os.getenv('ORACLE_PORT'),
                    service_name=os.getenv('ORACLE_SERVICE')
                )
                logger.success("✅ Connecté à Oracle")
            except Exception as e:
                logger.error(f"❌ Erreur de connexion : {e}")
                logger.warning("🔄 Basculement vers le simulateur")
                self.use_mock = True
                return self.connect()
        
        return True
    
    def extract_all(self, output_dir='data/oracle_exports'):
        """Extrait toutes les données nécessaires"""
        logger.info("📊 Début de l'extraction complète")
        
        if not self.connection:
            self.connect()
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Extraction des différentes sources
        extractions = {
            'audit_logs': self._extract_audit_logs,
            'sql_stats': self._extract_sql_stats,
            'security_config': self._extract_security,
            'performance_metrics': self._extract_performance
        }
        
        results = {}
        for name, func in extractions.items():
            try:
                logger.info(f"  📥 Extraction : {name}")
                data = func()
                results[name] = data
                
                # Sauvegarde CSV
                if isinstance(data, pd.DataFrame):
                    filepath = f"{output_dir}/{name}.csv"
                    data.to_csv(filepath, index=False)
                    logger.success(f"    ✅ Sauvegardé : {filepath} ({len(data)} lignes)")
                elif isinstance(data, dict):
                    for key, df in data.items():
                        filepath = f"{output_dir}/{name}_{key}.csv"
                        df.to_csv(filepath, index=False)
                        logger.success(f"    ✅ Sauvegardé : {filepath} ({len(df)} lignes)")
                        
            except Exception as e:
                logger.error(f"    ❌ Erreur : {e}")
                results[name] = None
        
        self.data_cache = results
        logger.success("✅ Extraction complète terminée")
        return results
    
    def _extract_audit_logs(self):
        """Extrait les logs d'audit"""
        if self.use_mock:
            return self.connection.get_audit_logs(100)
        else:
            query = """
            SELECT TIMESTAMP, USERNAME, ACTION_NAME as ACTION, 
                   OBJ_NAME as OBJECT_NAME, RETURNCODE, 
                   USERHOST as CLIENT_ID, OS_USERNAME, TERMINAL
            FROM DBA_AUDIT_TRAIL
            WHERE TIMESTAMP > SYSDATE - 30
            ORDER BY TIMESTAMP DESC
            """
            return pd.read_sql(query, self.connection)
    
    def _extract_sql_stats(self):
        """Extrait les statistiques SQL"""
        if self.use_mock:
            return self.connection.get_sql_stats(50)
        else:
            query = """
            SELECT SQL_ID, SQL_TEXT, EXECUTIONS, ELAPSED_TIME,
                   CPU_TIME, BUFFER_GETS, DISK_READS, ROWS_PROCESSED
            FROM V$SQLSTATS
            WHERE EXECUTIONS > 10
            ORDER BY ELAPSED_TIME DESC
            FETCH FIRST 50 ROWS ONLY
            """
            return pd.read_sql(query, self.connection)
    
    def _extract_security(self):
        """Extrait la configuration de sécurité"""
        if self.use_mock:
            return self.connection.get_security_config()
        else:
            users_query = """
            SELECT USERNAME, ACCOUNT_STATUS, PROFILE, 
                   DEFAULT_TABLESPACE, CREATED
            FROM DBA_USERS
            WHERE USERNAME NOT IN ('SYS', 'SYSTEM')
            """
            
            roles_query = "SELECT ROLE FROM DBA_ROLES"
            
            privs_query = """
            SELECT GRANTEE, PRIVILEGE, ADMIN_OPTION
            FROM DBA_SYS_PRIVS
            WHERE GRANTEE NOT IN ('SYS', 'SYSTEM')
            """
            
            return {
                'users': pd.read_sql(users_query, self.connection),
                'roles': pd.read_sql(roles_query, self.connection),
                'privileges': pd.read_sql(privs_query, self.connection)
            }
    
    def _extract_performance(self):
        """Extrait les métriques de performance"""
        if self.use_mock:
            # Métriques simulées
            return pd.DataFrame({
                'METRIC_NAME': ['CPU Usage', 'Memory Usage', 'IO Wait', 'Active Sessions'],
                'VALUE': [45.2, 67.8, 12.3, 23],
                'UNIT': ['%', '%', '%', 'count']
            })
        else:
            query = """
            SELECT METRIC_NAME, VALUE, METRIC_UNIT as UNIT
            FROM V$SYSMETRIC
            WHERE GROUP_ID = 2
            """
            return pd.read_sql(query, self.connection)
    
    def get_execution_plan(self, sql_id):
        """Récupère le plan d'exécution d'une requête"""
        if self.use_mock:
            return self.connection.get_execution_plan(sql_id)
        else:
            query = f"""
            SELECT OPERATION, OPTIONS, OBJECT_NAME, COST, CARDINALITY
            FROM V$SQL_PLAN
            WHERE SQL_ID = '{sql_id}'
            ORDER BY ID
            """
            return pd.read_sql(query, self.connection)
    
    def close(self):
        """Ferme la connexion"""
        if self.connection and not self.use_mock:
            self.connection.close()
        logger.info("🔌 Connexion fermée")


def main():
    """Fonction principale de test"""
    logger.info("="*60)
    logger.info("MODULE 1 : EXTRACTION DE DONNÉES ORACLE")
    logger.info("="*60)
    
    # Créer l'extracteur
    extractor = OracleDataExtractor(use_mock=True)
    
    # Extraire toutes les données
    results = extractor.extract_all()
    
    # Afficher un résumé
    logger.info("\n" + "="*60)
    logger.info("📊 RÉSUMÉ DE L'EXTRACTION")
    logger.info("="*60)
    
    for name, data in results.items():
        if isinstance(data, pd.DataFrame):
            logger.info(f"  📁 {name}: {len(data)} lignes")
        elif isinstance(data, dict):
            for key, df in data.items():
                logger.info(f"  📁 {name}.{key}: {len(df)} lignes")
    
    logger.info("\n✅ MODULE 1 TERMINÉ")
    logger.info("📂 Fichiers disponibles dans : data/oracle_exports/")
    
    extractor.close()


if __name__ == "__main__":
    main()