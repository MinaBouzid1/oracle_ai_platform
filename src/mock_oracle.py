"""
Simulateur de base de données Oracle pour le développement
Génère des données synthétiques réalistes
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import json

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
    
    def get_audit_logs(self, num_records=100):
        """Génère des logs d'audit synthétiques"""
        print(f"📊 Génération de {num_records} logs d'audit...")
        
        users = ['SCOTT', 'HR', 'ADMIN', 'APP_USER', 'DBA_JOHN', 'ANALYST']
        actions = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
        objects = ['EMPLOYEES', 'DEPARTMENTS', 'CUSTOMERS', 'ORDERS', 'PRODUCTS', 'SALARY_DATA']
        
        logs = []
        base_time = datetime.now() - timedelta(days=30)
        
        for i in range(num_records):
            log = {
                'TIMESTAMP': base_time + timedelta(minutes=random.randint(0, 43200)),
                'USERNAME': random.choice(users),
                'ACTION': random.choice(actions),
                'OBJECT_NAME': random.choice(objects),
                'RETURNCODE': 0 if random.random() > 0.05 else random.choice([1017, 942, 1031]),
                'CLIENT_ID': f'192.168.1.{random.randint(1, 254)}',
                'OS_USERNAME': f'user{random.randint(1, 50)}',
                'TERMINAL': random.choice(['WORKSTATION1', 'SERVER1', 'LAPTOP5', 'UNKNOWN'])
            }
            logs.append(log)
        
        return pd.DataFrame(logs)
    
    def get_sql_stats(self, num_queries=50):
        """Génère des statistiques SQL"""
        print(f"📊 Génération de {num_queries} requêtes SQL...")
        
        queries = []
        for i in range(num_queries):
            query = {
                'SQL_ID': f'sql_{i:04d}',
                'SQL_TEXT': self._generate_sql_query(),
                'EXECUTIONS': random.randint(1, 1000),
                'ELAPSED_TIME': random.randint(100, 5000000),
                'CPU_TIME': random.randint(50, 3000000),
                'BUFFER_GETS': random.randint(100, 100000),
                'DISK_READS': random.randint(0, 50000),
                'ROWS_PROCESSED': random.randint(1, 10000)
            }
            queries.append(query)
        
        return pd.DataFrame(queries)
    
    def get_execution_plan(self, sql_id):
        """Génère un plan d'exécution simulé"""
        plans = [
            {
                'OPERATION': 'SELECT STATEMENT',
                'OPTIONS': None,
                'OBJECT_NAME': None,
                'COST': random.randint(100, 1000),
                'CARDINALITY': random.randint(1, 10000)
            },
            {
                'OPERATION': 'TABLE ACCESS',
                'OPTIONS': random.choice(['FULL', 'BY INDEX ROWID']),
                'OBJECT_NAME': random.choice(['EMPLOYEES', 'DEPARTMENTS', 'ORDERS']),
                'COST': random.randint(50, 500),
                'CARDINALITY': random.randint(1, 5000)
            }
        ]
        return pd.DataFrame(plans)
    
    def get_security_config(self):
        """Génère une configuration de sécurité"""
        print("🔒 Récupération de la configuration de sécurité...")
        
        users = []
        for i in range(10):
            user = {
                'USERNAME': f'USER_{i}',
                'ACCOUNT_STATUS': random.choice(['OPEN', 'LOCKED', 'EXPIRED']),
                'PROFILE': random.choice(['DEFAULT', 'ADMIN_PROFILE', 'APP_PROFILE']),
                'DEFAULT_TABLESPACE': 'USERS',
                'CREATED': datetime.now() - timedelta(days=random.randint(30, 365))
            }
            users.append(user)
        
        return {
            'users': pd.DataFrame(users),
            'roles': self._get_roles(),
            'privileges': self._get_privileges()
        }
    
    def _generate_sql_query(self):
        """Génère une requête SQL aléatoire"""
        templates = [
            "SELECT * FROM employees WHERE department_id = {dept}",
            "SELECT e.name, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.id",
            "UPDATE employees SET salary = salary * 1.1 WHERE employee_id = {emp}",
            "SELECT COUNT(*) FROM orders WHERE order_date > SYSDATE - 30",
            "DELETE FROM temp_table WHERE created_date < SYSDATE - 7"
        ]
        template = random.choice(templates)
        return template.format(dept=random.randint(1, 10), emp=random.randint(100, 999))
    
    def _get_roles(self):
        """Génère des rôles"""
        roles = ['DBA', 'CONNECT', 'RESOURCE', 'SELECT_CATALOG_ROLE', 'APP_ROLE']
        return pd.DataFrame({'ROLE': roles})
    
    def _get_privileges(self):
        """Génère des privilèges"""
        privs = []
        users = [f'USER_{i}' for i in range(5)]
        privileges = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE TABLE', 'DROP ANY TABLE']
        
        for user in users:
            for _ in range(random.randint(2, 6)):
                privs.append({
                    'GRANTEE': user,
                    'PRIVILEGE': random.choice(privileges),
                    'ADMIN_OPTION': random.choice(['YES', 'NO'])
                })
        
        return pd.DataFrame(privs)
    
    def export_to_csv(self, output_dir='data/oracle_exports'):
        """Export toutes les données en CSV"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📁 Export des données vers {output_dir}/")
        
        # Logs d'audit
        audit_logs = self.get_audit_logs(100)
        audit_logs.to_csv(f'{output_dir}/audit_logs.csv', index=False)
        print(f"  ✅ audit_logs.csv ({len(audit_logs)} lignes)")
        
        # Stats SQL
        sql_stats = self.get_sql_stats(50)
        sql_stats.to_csv(f'{output_dir}/sql_stats.csv', index=False)
        print(f"  ✅ sql_stats.csv ({len(sql_stats)} lignes)")
        
        # Config sécurité
        security = self.get_security_config()
        security['users'].to_csv(f'{output_dir}/users.csv', index=False)
        security['roles'].to_csv(f'{output_dir}/roles.csv', index=False)
        security['privileges'].to_csv(f'{output_dir}/privileges.csv', index=False)
        print(f"  ✅ users.csv ({len(security['users'])} lignes)")
        print(f"  ✅ roles.csv ({len(security['roles'])} lignes)")
        print(f"  ✅ privileges.csv ({len(security['privileges'])} lignes)")
        
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