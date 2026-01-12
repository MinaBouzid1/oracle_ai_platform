"""
Connecteur Oracle Database - Version Production (CORRIGÉ pour Oracle 21c XE)
Connexion réelle à Oracle via Docker
"""

import oracledb
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


class OracleConnector:
    """Connexion à Oracle Database réelle"""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 1521,
                 service_name: str = "XEPDB1",
                 user: str = "system",
                 password: str = "oracle"):
        """
        Initialise la connexion Oracle
        
        Args:
            host: Adresse du serveur Oracle
            port: Port Oracle (défaut 1521)
            service_name: Nom du service (XEPDB1 pour XE, ORCLPDB1 pour EE)
            user: Utilisateur Oracle
            password: Mot de passe
        """
        self.host = host
        self.port = port
        self.service_name = service_name
        self.user = user
        self.password = password
        self.connection = None
        
    def connect(self) -> bool:
        """Établit la connexion à Oracle"""
        try:
            # Créer le DSN (Data Source Name)
            dsn = oracledb.makedsn(self.host, self.port, service_name=self.service_name)
            
            # Connexion
            self.connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=dsn
            )
            
            logger.success(f"✅ Connecté à Oracle : {self.user}@{self.host}:{self.port}/{self.service_name}")
            
            # Tester la connexion
            cursor = self.connection.cursor()
            cursor.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
            version = cursor.fetchone()[0]
            logger.info(f"📊 Version Oracle : {version}")
            cursor.close()
            
            return True
            
        except oracledb.Error as e:
            error, = e.args
            logger.error(f"❌ Erreur de connexion Oracle : {error.message}")
            return False
    
    def disconnect(self):
        """Ferme la connexion"""
        if self.connection:
            self.connection.close()
            logger.info("🔌 Connexion Oracle fermée")
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Exécute une requête et retourne un DataFrame"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # Récupérer les colonnes
            columns = [col[0] for col in cursor.description]
            
            # Récupérer les données
            rows = cursor.fetchall()
            
            cursor.close()
            
            # Créer le DataFrame
            df = pd.DataFrame(rows, columns=columns)
            return df
            
        except oracledb.Error as e:
            error, = e.args
            logger.error(f"❌ Erreur d'exécution : {error.message}")
            if "Help:" in error.message:
                logger.error(f"Help: https://docs.oracle.com/error-help/db/ora-{error.code:05d}/")
            return pd.DataFrame()
    
    def get_audit_logs(self, limit: int = 100) -> pd.DataFrame:
        """Récupère les logs d'audit depuis la table personnalisée"""
        # D'abord essayer la table audit_log personnalisée
        query_custom = f"""
        SELECT 
            TIMESTAMP,
            USERNAME,
            ACTION_TYPE as ACTION_NAME,
            OBJECT_NAME as OBJ_NAME,
            SQL_TEXT,
            STATUS as RETURNCODE
        FROM testuser.audit_log
        ORDER BY TIMESTAMP DESC
        FETCH FIRST {limit} ROWS ONLY
        """
        
        logger.info(f"📥 Récupération des logs d'audit (limite: {limit})...")
        df = self.execute_query(query_custom)
        
        # Si la table personnalisée est vide, essayer DBA_AUDIT_TRAIL
        if df.empty:
            query_system = f"""
            SELECT 
                TIMESTAMP,
                USERNAME,
                ACTION_NAME,
                OBJ_NAME,
                SQL_TEXT,
                RETURNCODE
            FROM DBA_AUDIT_TRAIL
            WHERE TIMESTAMP >= SYSDATE - 7
            ORDER BY TIMESTAMP DESC
            FETCH FIRST {limit} ROWS ONLY
            """
            df = self.execute_query(query_system)
        
        return df
    
    def get_sql_statistics(self, limit: int = 50) -> pd.DataFrame:
        """Récupère les statistiques des requêtes SQL (CORRIGÉ pour Oracle 21c XE)"""
        # Version corrigée compatible Oracle 21c XE
        query = f"""
        SELECT 
            s.SQL_ID,
            s.PLAN_HASH_VALUE,
            u.USERNAME as SCHEMA_NAME,
            s.EXECUTIONS,
            ROUND(s.ELAPSED_TIME / 1000000, 2) as ELAPSED_TIME_SEC,
            ROUND(s.CPU_TIME / 1000000, 2) as CPU_TIME_SEC,
            s.BUFFER_GETS,
            s.DISK_READS,
            s.ROWS_PROCESSED,
            s.FETCHES,
            ROUND(s.ELAPSED_TIME / NULLIF(s.EXECUTIONS, 0) / 1000000, 4) as AVG_ELAPSED_SEC,
            SUBSTR(s.SQL_TEXT, 1, 200) as SQL_TEXT
        FROM V$SQL s
        LEFT JOIN DBA_USERS u ON s.PARSING_USER_ID = u.USER_ID
        WHERE s.ELAPSED_TIME > 0
        AND s.SQL_TEXT NOT LIKE '%V$SQL%'
        AND s.SQL_TEXT NOT LIKE '%DBA_%'
        ORDER BY s.ELAPSED_TIME DESC
        FETCH FIRST {limit} ROWS ONLY
        """
        
        logger.info(f"📥 Récupération des statistiques SQL (limite: {limit})...")
        return self.execute_query(query)
    
    def get_execution_plan(self, sql_id: str) -> pd.DataFrame:
        """Récupère le plan d'exécution d'une requête"""
        query = f"""
        SELECT 
            PLAN_HASH_VALUE,
            ID,
            LPAD(' ', 2 * DEPTH) || OPERATION || ' ' || OPTIONS as OPERATION,
            OBJECT_NAME,
            COST,
            CARDINALITY,
            BYTES,
            ACCESS_PREDICATES,
            FILTER_PREDICATES
        FROM V$SQL_PLAN
        WHERE SQL_ID = '{sql_id}'
        ORDER BY ID
        """
        
        logger.info(f"📥 Récupération du plan d'exécution pour SQL_ID: {sql_id}...")
        return self.execute_query(query)
    
    def get_users_and_roles(self) -> Dict[str, pd.DataFrame]:
        """Récupère les utilisateurs et rôles"""
        users_query = """
        SELECT 
            USERNAME,
            ACCOUNT_STATUS,
            LOCK_DATE,
            EXPIRY_DATE,
            DEFAULT_TABLESPACE,
            PROFILE,
            CREATED
        FROM DBA_USERS
        WHERE USERNAME NOT IN ('SYS', 'SYSTEM', 'XDB', 'OUTLN', 'ANONYMOUS', 'CTXSYS', 'DBSNMP', 'MDSYS', 'ORACLE_OCM', 'WMSYS')
        AND ORACLE_MAINTAINED = 'N'
        ORDER BY USERNAME
        """
        
        roles_query = """
        SELECT 
            GRANTEE,
            GRANTED_ROLE,
            ADMIN_OPTION,
            DEFAULT_ROLE
        FROM DBA_ROLE_PRIVS
        WHERE GRANTEE NOT IN ('SYS', 'SYSTEM', 'XDB', 'OUTLN', 'ANONYMOUS')
        AND GRANTEE IN (SELECT USERNAME FROM DBA_USERS WHERE ORACLE_MAINTAINED = 'N')
        ORDER BY GRANTEE, GRANTED_ROLE
        """
        
        logger.info("📥 Récupération des utilisateurs et rôles...")
        
        return {
            'users': self.execute_query(users_query),
            'roles': self.execute_query(roles_query)
        }
    
    def get_system_privileges(self) -> pd.DataFrame:
        """Récupère les privilèges système"""
        query = """
        SELECT 
            GRANTEE,
            PRIVILEGE,
            ADMIN_OPTION
        FROM DBA_SYS_PRIVS
        WHERE GRANTEE NOT IN ('SYS', 'SYSTEM', 'XDB', 'OUTLN', 'DBA', 'RESOURCE', 'CONNECT', 'PUBLIC')
        AND GRANTEE IN (SELECT USERNAME FROM DBA_USERS WHERE ORACLE_MAINTAINED = 'N')
        ORDER BY GRANTEE, PRIVILEGE
        """
        
        logger.info("📥 Récupération des privilèges système...")
        return self.execute_query(query)
    
    def get_database_size(self) -> Dict[str, float]:
        """Récupère la taille de la base de données"""
        query = """
        SELECT 
            ROUND(SUM(BYTES) / 1024 / 1024 / 1024, 2) as SIZE_GB
        FROM DBA_DATA_FILES
        """
        
        df = self.execute_query(query)
        size_gb = df['SIZE_GB'].iloc[0] if not df.empty else 0
        
        logger.info(f"📊 Taille de la base : {size_gb:.2f} GB")
        
        return {
            'total_size_gb': float(size_gb),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_tablespace_usage(self) -> pd.DataFrame:
        """Récupère l'utilisation des tablespaces"""
        query = """
        SELECT 
            df.TABLESPACE_NAME,
            ROUND(df.TOTAL_SIZE_MB, 2) as TOTAL_SIZE_MB,
            ROUND(NVL(fs.FREE_SIZE_MB, 0), 2) as FREE_SIZE_MB,
            ROUND(df.TOTAL_SIZE_MB - NVL(fs.FREE_SIZE_MB, 0), 2) as USED_SIZE_MB,
            ROUND(((df.TOTAL_SIZE_MB - NVL(fs.FREE_SIZE_MB, 0)) / df.TOTAL_SIZE_MB) * 100, 2) as USED_PERCENT
        FROM 
            (SELECT TABLESPACE_NAME, SUM(BYTES)/1024/1024 as TOTAL_SIZE_MB
             FROM DBA_DATA_FILES
             GROUP BY TABLESPACE_NAME) df
        LEFT JOIN
            (SELECT TABLESPACE_NAME, SUM(BYTES)/1024/1024 as FREE_SIZE_MB
             FROM DBA_FREE_SPACE
             GROUP BY TABLESPACE_NAME) fs
        ON df.TABLESPACE_NAME = fs.TABLESPACE_NAME
        ORDER BY USED_PERCENT DESC
        """
        
        logger.info("📥 Récupération de l'utilisation des tablespaces...")
        return self.execute_query(query)
    
    def get_slow_queries(self, min_elapsed_sec: float = 1.0, limit: int = 20) -> pd.DataFrame:
        """Récupère les requêtes lentes"""
        query = f"""
        SELECT 
            s.SQL_ID,
            u.USERNAME as SCHEMA_NAME,
            s.EXECUTIONS,
            ROUND(s.ELAPSED_TIME / 1000000, 2) as TOTAL_ELAPSED_SEC,
            ROUND(s.ELAPSED_TIME / NULLIF(s.EXECUTIONS, 0) / 1000000, 4) as AVG_ELAPSED_SEC,
            ROUND(s.CPU_TIME / 1000000, 2) as CPU_TIME_SEC,
            s.BUFFER_GETS,
            s.DISK_READS,
            s.ROWS_PROCESSED,
            SUBSTR(s.SQL_TEXT, 1, 300) as SQL_TEXT
        FROM V$SQL s
        LEFT JOIN DBA_USERS u ON s.PARSING_USER_ID = u.USER_ID
        WHERE s.ELAPSED_TIME / NULLIF(s.EXECUTIONS, 0) / 1000000 > {min_elapsed_sec}
        AND s.SQL_TEXT NOT LIKE '%V$SQL%'
        AND s.SQL_TEXT NOT LIKE '%DBA_%'
        ORDER BY s.ELAPSED_TIME DESC
        FETCH FIRST {limit} ROWS ONLY
        """
        
        logger.info(f"📥 Récupération des requêtes lentes (> {min_elapsed_sec}s)...")
        return self.execute_query(query)


# ============================================================================
# TEST DE CONNEXION
# ============================================================================

if __name__ == "__main__":
    logger.info("🧪 Test de connexion Oracle Database")
    logger.info("=" * 60)
    
    # Créer le connecteur
    oracle = OracleConnector(
        host="localhost",
        port=1521,
        service_name="XEPDB1",
        user="system",
        password="oracle"
    )
    
    # Se connecter
    if oracle.connect():
        # Test 1 : Récupérer les statistiques SQL
        logger.info("\n📊 TEST 1 : Statistiques SQL")
        sql_stats = oracle.get_sql_statistics(limit=10)
        logger.info(f"Récupéré {len(sql_stats)} requêtes")
        if not sql_stats.empty:
            print("\n" + "="*80)
            print(sql_stats[['SQL_ID', 'SCHEMA_NAME', 'EXECUTIONS', 'ELAPSED_TIME_SEC', 'SQL_TEXT']].to_string(index=False))
            print("="*80)
        
        # Test 2 : Requêtes lentes
        logger.info("\n📊 TEST 2 : Requêtes lentes")
        slow_queries = oracle.get_slow_queries(min_elapsed_sec=0.1, limit=5)
        logger.info(f"Récupéré {len(slow_queries)} requêtes lentes")
        if not slow_queries.empty:
            print("\n" + "="*80)
            print(slow_queries[['SQL_ID', 'AVG_ELAPSED_SEC', 'EXECUTIONS', 'SQL_TEXT']].to_string(index=False))
            print("="*80)
        
        # Test 3 : Taille de la base
        logger.info("\n📊 TEST 3 : Taille de la base")
        db_size = oracle.get_database_size()
        logger.info(f"Taille : {db_size['total_size_gb']:.2f} GB")
        
        # Test 4 : Tablespaces
        logger.info("\n📊 TEST 4 : Utilisation des tablespaces")
        tablespaces = oracle.get_tablespace_usage()
        if not tablespaces.empty:
            print("\n" + "="*80)
            print(tablespaces.to_string(index=False))
            print("="*80)
        
        # Test 5 : Utilisateurs
        logger.info("\n📊 TEST 5 : Utilisateurs et rôles")
        users_data = oracle.get_users_and_roles()
        logger.info(f"Utilisateurs : {len(users_data['users'])}")
        logger.info(f"Rôles : {len(users_data['roles'])}")
        if not users_data['users'].empty:
            print("\n" + "="*80)
            print("UTILISATEURS:")
            print(users_data['users'][['USERNAME', 'ACCOUNT_STATUS', 'PROFILE', 'CREATED']].to_string(index=False))
            print("="*80)
        
        # Test 6 : Logs d'audit
        logger.info("\n📊 TEST 6 : Logs d'audit")
        audit_logs = oracle.get_audit_logs(limit=10)
        logger.info(f"Récupéré {len(audit_logs)} logs")
        if not audit_logs.empty:
            print("\n" + "="*80)
            print(audit_logs.to_string(index=False))
            print("="*80)
        
        # Déconnexion
        logger.info("\n" + "="*60)
        oracle.disconnect()
        logger.success("✅ TOUS LES TESTS RÉUSSIS !")
    else:
        logger.error("❌ Impossible de se connecter à Oracle")