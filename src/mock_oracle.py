"""
Simulateur de base de données Oracle pour le développement
Génère des données synthétiques réalistes
Version corrigée pour compatibilité avec OracleDataExtractor
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import json
import os

class MockOracle:
    """Simule une connexion Oracle et génère des données test"""
    
    def __init__(self):
        self.connected = False
        print("🔄 Initialisation du simulateur Oracle...")
    
    def connect(self):
        """Simule une connexion à Oracle"""
        self.connected = True
        print("✅ Connecté au simulateur Oracle")
        return True
    
    def disconnect(self):
        """Simule la déconnexion"""
        self.connected = False
        print("🔌 Déconnecté du simulateur Oracle")
    
    def get_audit_logs(self, limit=100):
        """Génère des logs d'audit synthétiques"""
        print(f"📊 Génération de {limit} logs d'audit...")
        
        users = ['SCOTT', 'HR', 'ADMIN', 'APP_USER', 'DBA_JOHN', 'ANALYST']
        actions = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
        objects = ['EMPLOYEES', 'DEPARTMENTS', 'CUSTOMERS', 'ORDERS', 'PRODUCTS', 'SALARY_DATA']
        
        logs = []
        base_time = datetime.now() - timedelta(days=30)
        
        for i in range(limit):
            log = {
                'TIMESTAMP': (base_time + timedelta(minutes=random.randint(0, 43200))).strftime('%Y-%m-%d %H:%M:%S'),
                'USERNAME': random.choice(users),
                'ACTION_NAME': random.choice(actions),
                'OBJ_NAME': random.choice(objects),
                'SQL_TEXT': f"SELECT * FROM {random.choice(objects)} WHERE id = {random.randint(1, 100)}",
                'RETURNCODE': 0 if random.random() > 0.05 else random.choice([1017, 942, 1031]),
                'CLIENT_ID': f'192.168.1.{random.randint(1, 254)}',
                'OS_USERNAME': f'user{random.randint(1, 50)}',
                'TERMINAL': random.choice(['WORKSTATION1', 'SERVER1', 'LAPTOP5', 'UNKNOWN'])
            }
            logs.append(log)
        
        return pd.DataFrame(logs)
    
    def get_sql_statistics(self, limit=50):
        """Génère des statistiques SQL"""
        print(f"📊 Génération de {limit} requêtes SQL...")
        
        queries = []
        for i in range(limit):
            query = {
                'SQL_ID': f'sql_{i:04d}',
                'SQL_TEXT': self._generate_sql_query(),
                'EXECUTIONS': random.randint(1, 1000),
                'ELAPSED_TIME': random.randint(100, 5000000),
                'CPU_TIME': random.randint(50, 3000000),
                'BUFFER_GETS': random.randint(100, 100000),
                'DISK_READS': random.randint(0, 50000),
                'ROWS_PROCESSED': random.randint(1, 10000),
                'PLAN_HASH_VALUE': random.randint(1000000, 9999999),
                'SCHEMA_NAME': random.choice(['HR', 'SCOTT', 'SYS', 'SYSTEM']),
                'ELAPSED_TIME_SEC': random.uniform(0.1, 10.0),
                'CPU_TIME_SEC': random.uniform(0.05, 5.0),
                'AVG_ELAPSED_SEC': random.uniform(0.001, 0.5),
                'FETCHES': random.randint(1, 1000)
            }
            queries.append(query)
        
        return pd.DataFrame(queries)
    
    def get_slow_queries(self, min_elapsed_sec=0.1, limit=20):
        """Génère des requêtes lentes"""
        print(f"📊 Génération de {limit} requêtes lentes...")
        
        queries = []
        for i in range(limit):
            elapsed_time = random.uniform(min_elapsed_sec, 10.0) * 1000000  # Convertir en microsecondes
            query = {
                'SQL_ID': f'slow_{i:04d}',
                'SCHEMA_NAME': random.choice(['HR', 'SCOTT', 'APP_USER']),
                'EXECUTIONS': random.randint(1, 100),
                'TOTAL_ELAPSED_SEC': random.uniform(1.0, 30.0),
                'AVG_ELAPSED_SEC': random.uniform(0.5, 5.0),
                'CPU_TIME_SEC': random.uniform(0.5, 15.0),
                'BUFFER_GETS': random.randint(10000, 1000000),
                'DISK_READS': random.randint(1000, 100000),
                'ROWS_PROCESSED': random.randint(1000, 100000),
                'SQL_TEXT': self._generate_sql_query()
            }
            queries.append(query)
        
        return pd.DataFrame(queries)
    
    def get_users_and_roles(self):
        """Génère des utilisateurs et rôles"""
        print("👥 Génération d'utilisateurs et rôles...")
        
        # Utilisateurs
        users = []
        for i in range(10):
            status = random.choice(['OPEN', 'LOCKED', 'EXPIRED'])
            user = {
                'USERNAME': f'USER_{i:03d}',
                'ACCOUNT_STATUS': status,
                'PROFILE': random.choice(['DEFAULT', 'ADMIN_PROFILE', 'APP_PROFILE']),
                'DEFAULT_TABLESPACE': 'USERS',
                'CREATED': (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d %H:%M:%S'),
                'LOCK_DATE': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S') if status == 'LOCKED' else None,
                'EXPIRY_DATE': (datetime.now() + timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d %H:%M:%S')
            }
            users.append(user)
        
        # Rôles
        roles_data = []
        all_roles = ['DBA', 'CONNECT', 'RESOURCE', 'SELECT_CATALOG_ROLE', 'APP_ROLE']
        for i in range(len(users)):
            for _ in range(random.randint(1, 3)):
                roles_data.append({
                    'GRANTEE': users[i]['USERNAME'],
                    'GRANTED_ROLE': random.choice(all_roles),
                    'ADMIN_OPTION': random.choice(['YES', 'NO']),
                    'DEFAULT_ROLE': random.choice(['YES', 'NO'])
                })
        
        return {
            'users': pd.DataFrame(users),
            'roles': pd.DataFrame(roles_data)
        }
    
    def get_system_privileges(self):
        """Génère des privilèges système"""
        print("🔑 Génération de privilèges système...")
        
        privs = []
        users = [f'USER_{i:03d}' for i in range(5)]
        privileges = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE TABLE', 'DROP ANY TABLE', 
                     'CREATE SESSION', 'CREATE VIEW', 'CREATE PROCEDURE']
        
        for user in users:
            for _ in range(random.randint(2, 6)):
                privs.append({
                    'GRANTEE': user,
                    'PRIVILEGE': random.choice(privileges),
                    'ADMIN_OPTION': random.choice(['YES', 'NO'])
                })
        
        return pd.DataFrame(privs)
    
    def get_tablespace_usage(self):
        """Génère l'utilisation des tablespaces"""
        print("💾 Génération de l'utilisation des tablespaces...")
        
        tablespaces = ['SYSTEM', 'SYSAUX', 'USERS', 'TEMP', 'DATA', 'INDEX']
        data = []
        
        for ts in tablespaces:
            total_size = random.uniform(100, 1000)
            free_size = random.uniform(10, total_size * 0.5)
            used_size = total_size - free_size
            used_percent = (used_size / total_size) * 100
            
            data.append({
                'TABLESPACE_NAME': ts,
                'TOTAL_SIZE_MB': round(total_size, 2),
                'FREE_SIZE_MB': round(free_size, 2),
                'USED_SIZE_MB': round(used_size, 2),
                'USED_PERCENT': round(used_percent, 2)
            })
        
        return pd.DataFrame(data)
    
    def get_database_size(self):
        """Génère la taille de la base de données"""
        print("📊 Génération de la taille de la base...")
        
        total_size = random.uniform(10, 100)  # Entre 10 et 100 GB
        
        return {
            'total_size_gb': round(total_size, 2),
            'timestamp': datetime.now().isoformat(),
            'datafiles_count': random.randint(5, 20),
            'tablespaces_count': random.randint(4, 8),
            'estimated_growth_gb_per_month': round(random.uniform(0.5, 5.0), 2)
        }
    
    def get_execution_plan(self, sql_id):
        """Génère un plan d'exécution simulé"""
        print(f"📈 Génération du plan d'exécution pour SQL_ID: {sql_id}")
        
        plans = [
            {
                'ID': 0,
                'OPERATION': 'SELECT STATEMENT',
                'OPTIONS': None,
                'OBJECT_NAME': None,
                'COST': random.randint(100, 1000),
                'CARDINALITY': random.randint(1, 10000),
                'BYTES': random.randint(1024, 1048576),
                'ACCESS_PREDICATES': None,
                'FILTER_PREDICATES': None,
                'PLAN_HASH_VALUE': random.randint(1000000, 9999999)
            },
            {
                'ID': 1,
                'OPERATION': 'TABLE ACCESS',
                'OPTIONS': random.choice(['FULL', 'BY INDEX ROWID']),
                'OBJECT_NAME': random.choice(['EMPLOYEES', 'DEPARTMENTS', 'ORDERS']),
                'COST': random.randint(50, 500),
                'CARDINALITY': random.randint(1, 5000),
                'BYTES': random.randint(512, 524288),
                'ACCESS_PREDICATES': f"{random.choice(['EMPLOYEE_ID', 'DEPARTMENT_ID', 'ORDER_ID'])} = {random.randint(1, 100)}",
                'FILTER_PREDICATES': None,
                'PLAN_HASH_VALUE': random.randint(1000000, 9999999)
            }
        ]
        return pd.DataFrame(plans)
    
    def _generate_sql_query(self):
        """Génère une requête SQL aléatoire"""
        templates = [
            "SELECT * FROM employees WHERE department_id = {dept}",
            "SELECT e.name, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.id",
            "UPDATE employees SET salary = salary * 1.1 WHERE employee_id = {emp}",
            "SELECT COUNT(*) FROM orders WHERE order_date > SYSDATE - 30",
            "DELETE FROM temp_table WHERE created_date < SYSDATE - 7",
            "INSERT INTO audit_log (user_id, action, timestamp) VALUES ({user}, '{action}', SYSDATE)",
            "CREATE INDEX idx_emp_dept ON employees(department_id)",
            "ALTER TABLE customers ADD (created_date DATE DEFAULT SYSDATE)"
        ]
        template = random.choice(templates)
        return template.format(
            dept=random.randint(1, 10), 
            emp=random.randint(100, 999),
            user=random.randint(1, 100),
            action=random.choice(['LOGIN', 'LOGOUT', 'UPDATE', 'DELETE'])
        )
    
    def export_to_csv(self, output_dir='data/oracle_exports'):
        """Export toutes les données en CSV"""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📁 Export des données vers {output_dir}/")
        
        # Logs d'audit
        audit_logs = self.get_audit_logs(100)
        audit_logs.to_csv(f'{output_dir}/audit_logs.csv', index=False)
        print(f"  ✅ audit_logs.csv ({len(audit_logs)} lignes)")
        
        # Stats SQL
        sql_stats = self.get_sql_statistics(50)
        sql_stats.to_csv(f'{output_dir}/sql_stats.csv', index=False)
        print(f"  ✅ sql_stats.csv ({len(sql_stats)} lignes)")
        
        # Requêtes lentes
        slow_queries = self.get_slow_queries(0.1, 20)
        slow_queries.to_csv(f'{output_dir}/slow_queries.csv', index=False)
        print(f"  ✅ slow_queries.csv ({len(slow_queries)} lignes)")
        
        # Utilisateurs et rôles
        users_data = self.get_users_and_roles()
        users_data['users'].to_csv(f'{output_dir}/users.csv', index=False)
        users_data['roles'].to_csv(f'{output_dir}/user_roles.csv', index=False)
        print(f"  ✅ users.csv ({len(users_data['users'])} lignes)")
        print(f"  ✅ user_roles.csv ({len(users_data['roles'])} lignes)")
        
        # Privilèges système
        sys_privs = self.get_system_privileges()
        sys_privs.to_csv(f'{output_dir}/system_privileges.csv', index=False)
        print(f"  ✅ system_privileges.csv ({len(sys_privs)} lignes)")
        
        # Tablespaces
        tablespaces = self.get_tablespace_usage()
        tablespaces.to_csv(f'{output_dir}/tablespaces.csv', index=False)
        print(f"  ✅ tablespaces.csv ({len(tablespaces)} lignes)")
        
        # Taille DB
        db_size = self.get_database_size()
        with open(f'{output_dir}/database_metrics.json', 'w') as f:
            json.dump(db_size, f, indent=2)
        print(f"  ✅ database_metrics.json")
        
        print("\n✅ Export terminé!")
        return output_dir


if __name__ == "__main__":
    # Test du simulateur
    print("🧪 Test du simulateur Oracle\n")
    
    mock = MockOracle()
    mock.connect()
    
    # Test de génération
    print("\n" + "="*50)
    export_dir = mock.export_to_csv()
    
    print("\n" + "="*50)
    print("📊 Résumé des données générées:")
    print(f"  - Logs d'audit : 100 entrées")
    print(f"  - Requêtes SQL : 50 requêtes")
    print(f"  - Utilisateurs : 10 comptes")
    print(f"  - Rôles et privilèges inclus")
    print("\n✅ Module 1 - Extraction : TERMINÉ")