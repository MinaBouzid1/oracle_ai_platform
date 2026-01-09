"""
Générateur de logs d'audit synthétiques
50 logs normaux + 20 logs suspects pour l'entraînement
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import json
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


class SyntheticLogsGenerator:
    """Génère des logs d'audit réalistes pour la détection d'anomalies"""
    
    def __init__(self):
        self.normal_users = ['SCOTT', 'HR_USER', 'APP_USER', 'ANALYST', 'REPORT_USER']
        self.suspicious_users = ['HACKER', 'UNKNOWN_USER', 'ADMIN_TEST']
        
        self.normal_objects = ['EMPLOYEES', 'DEPARTMENTS', 'ORDERS', 'CUSTOMERS', 'PRODUCTS']
        self.sensitive_objects = ['SALARY_DATA', 'CREDIT_CARDS', 'DBA_USERS', 'DBA_TAB_PRIVS']
        
        self.normal_actions = ['SELECT', 'INSERT', 'UPDATE']
        self.dangerous_actions = ['DROP', 'CREATE USER', 'GRANT', 'ALTER SYSTEM']
        
        self.business_hours = (8, 18)  # 8h-18h
    
    def generate_dataset(self, num_normal=50, num_suspicious=20) -> pd.DataFrame:
        """
        Génère un dataset complet de logs
        
        Args:
            num_normal: Nombre de logs normaux
            num_suspicious: Nombre de logs suspects
        
        Returns:
            DataFrame avec tous les logs
        """
        logger.info(f"🔧 Génération de {num_normal} logs normaux + {num_suspicious} logs suspects")
        
        normal_logs = self._generate_normal_logs(num_normal)
        suspicious_logs = self._generate_suspicious_logs(num_suspicious)
        
        # Combiner et mélanger
        all_logs = normal_logs + suspicious_logs
        random.shuffle(all_logs)
        
        df = pd.DataFrame(all_logs)
        logger.success(f"✅ {len(df)} logs générés")
        
        return df
    
    def _generate_normal_logs(self, num: int) -> list:
        """Génère des logs normaux"""
        logs = []
        base_time = datetime.now() - timedelta(days=7)
        
        for i in range(num):
            # Timestamp pendant les heures de bureau
            hour = random.randint(self.business_hours[0], self.business_hours[1])
            timestamp = base_time + timedelta(
                days=random.randint(0, 6),
                hours=hour,
                minutes=random.randint(0, 59)
            )
            
            log = {
                'TIMESTAMP': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'USERNAME': random.choice(self.normal_users),
                'ACTION': random.choice(self.normal_actions),
                'OBJECT_NAME': random.choice(self.normal_objects),
                'RETURNCODE': 0,  # Succès
                'CLIENT_ID': f'192.168.1.{random.randint(10, 50)}',
                'OS_USERNAME': f'employee{random.randint(1, 100)}',
                'TERMINAL': random.choice(['WORKSTATION1', 'LAPTOP5', 'SERVER2']),
                'LABEL': 'normal',
                'ANOMALY_TYPE': None
            }
            
            logs.append(log)
        
        return logs
    
    def _generate_suspicious_logs(self, num: int) -> list:
        """Génère des logs suspects avec différents types d'anomalies"""
        logs = []
        
        # Distribuer les types d'anomalies
        anomaly_types = [
            ('sql_injection', num // 5),
            ('privilege_escalation', num // 5),
            ('data_exfiltration', num // 5),
            ('off_hours_access', num // 5),
            ('brute_force', num - 4 * (num // 5))  # Le reste
        ]
        
        for anomaly_type, count in anomaly_types:
            logs.extend(self._generate_anomaly_type(anomaly_type, count))
        
        return logs
    
    def _generate_anomaly_type(self, anomaly_type: str, count: int) -> list:
        """Génère des logs d'un type d'anomalie spécifique"""
        logs = []
        base_time = datetime.now() - timedelta(days=7)
        
        for i in range(count):
            if anomaly_type == 'sql_injection':
                log = self._create_sql_injection_log(base_time, i)
            elif anomaly_type == 'privilege_escalation':
                log = self._create_privilege_escalation_log(base_time, i)
            elif anomaly_type == 'data_exfiltration':
                log = self._create_data_exfiltration_log(base_time, i)
            elif anomaly_type == 'off_hours_access':
                log = self._create_off_hours_log(base_time, i)
            elif anomaly_type == 'brute_force':
                log = self._create_brute_force_log(base_time, i)
            else:
                continue
            
            logs.append(log)
        
        return logs
    
    def _create_sql_injection_log(self, base_time: datetime, idx: int) -> dict:
        """Log d'injection SQL"""
        sql_injection_patterns = [
            "EMPLOYEES WHERE 1=1 OR '1'='1",
            "USERS WHERE username='admin'--",
            "ORDERS WHERE id=1 UNION SELECT * FROM PASSWORDS",
            "CUSTOMERS WHERE email=''; DROP TABLE USERS--",
            "PRODUCTS WHERE id=1' OR 'a'='a"
        ]
        
        timestamp = base_time + timedelta(
            days=random.randint(0, 6),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        return {
            'TIMESTAMP': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'USERNAME': random.choice(self.normal_users),
            'ACTION': 'SELECT',
            'OBJECT_NAME': random.choice(sql_injection_patterns),
            'RETURNCODE': 0,
            'CLIENT_ID': f'192.168.1.{random.randint(100, 254)}',
            'OS_USERNAME': random.choice(['hacker', 'attacker', 'malicious']),
            'TERMINAL': 'UNKNOWN',
            'LABEL': 'suspicious',
            'ANOMALY_TYPE': 'sql_injection'
        }
    
    def _create_privilege_escalation_log(self, base_time: datetime, idx: int) -> dict:
        """Log d'escalade de privilèges"""
        timestamp = base_time + timedelta(
            days=random.randint(0, 6),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        return {
            'TIMESTAMP': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'USERNAME': random.choice(self.normal_users),
            'ACTION': random.choice(['GRANT', 'CREATE USER', 'ALTER USER']),
            'OBJECT_NAME': random.choice([
                'SYSDBA TO HACKER',
                'DBA TO APP_USER',
                'BACKDOOR_ADMIN'
            ]),
            'RETURNCODE': 0,
            'CLIENT_ID': f'192.168.1.{random.randint(100, 254)}',
            'OS_USERNAME': f'user{random.randint(1, 10)}',
            'TERMINAL': random.choice(['WORKSTATION1', 'UNKNOWN']),
            'LABEL': 'suspicious',
            'ANOMALY_TYPE': 'privilege_escalation'
        }
    
    def _create_data_exfiltration_log(self, base_time: datetime, idx: int) -> dict:
        """Log d'exfiltration de données"""
        timestamp = base_time + timedelta(
            days=random.randint(0, 6),
            hours=random.randint(2, 5),  # Nuit
            minutes=random.randint(0, 59)
        )
        
        return {
            'TIMESTAMP': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'USERNAME': random.choice(self.normal_users + self.suspicious_users),
            'ACTION': 'SELECT',
            'OBJECT_NAME': random.choice(self.sensitive_objects),
            'RETURNCODE': 0,
            'CLIENT_ID': f'192.168.1.{random.randint(100, 254)}',
            'OS_USERNAME': random.choice(['external', 'vpn_user', 'remote']),
            'TERMINAL': 'REMOTE',
            'LABEL': 'suspicious',
            'ANOMALY_TYPE': 'data_exfiltration'
        }
    
    def _create_off_hours_log(self, base_time: datetime, idx: int) -> dict:
        """Log d'accès hors heures ouvrables"""
        # Choisir une heure suspecte (nuit ou week-end)
        hour = random.choice(list(range(0, 7)) + list(range(20, 24)))
        
        timestamp = base_time + timedelta(
            days=random.randint(0, 6),
            hours=hour,
            minutes=random.randint(0, 59)
        )
        
        return {
            'TIMESTAMP': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'USERNAME': random.choice(self.normal_users),
            'ACTION': random.choice(['SELECT', 'UPDATE', 'DELETE']),
            'OBJECT_NAME': random.choice(self.sensitive_objects),
            'RETURNCODE': 0,
            'CLIENT_ID': f'192.168.1.{random.randint(100, 254)}',
            'OS_USERNAME': f'user{random.randint(1, 50)}',
            'TERMINAL': random.choice(['REMOTE', 'UNKNOWN', 'VPN']),
            'LABEL': 'suspicious',
            'ANOMALY_TYPE': 'off_hours_access'
        }
    
    def _create_brute_force_log(self, base_time: datetime, idx: int) -> dict:
        """Log de tentative de brute force"""
        timestamp = base_time + timedelta(
            days=random.randint(0, 6),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=idx  # Tentatives rapprochées
        )
        
        return {
            'TIMESTAMP': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'USERNAME': random.choice(['ADMIN', 'ROOT', 'SYSTEM', 'DBA']),
            'ACTION': 'LOGON',
            'OBJECT_NAME': 'DATABASE',
            'RETURNCODE': random.choice([1017, 1005]),  # Codes d'erreur
            'CLIENT_ID': f'192.168.1.{random.randint(200, 254)}',
            'OS_USERNAME': 'attacker',
            'TERMINAL': 'UNKNOWN',
            'LABEL': 'suspicious',
            'ANOMALY_TYPE': 'brute_force'
        }
    
    def save_dataset(self, df: pd.DataFrame, output_dir='data/synthetic_data'):
        """Sauvegarde le dataset"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # CSV
        csv_path = f"{output_dir}/audit_logs_synthetic.csv"
        df.to_csv(csv_path, index=False)
        logger.success(f"💾 Dataset CSV : {csv_path}")
        
        # JSON (pour les tests)
        json_path = f"{output_dir}/audit_logs_synthetic.json"
        df.to_json(json_path, orient='records', indent=2)
        logger.success(f"💾 Dataset JSON : {json_path}")
        
        # Statistiques
        stats = {
            'total_logs': len(df),
            'normal_logs': len(df[df['LABEL'] == 'normal']),
            'suspicious_logs': len(df[df['LABEL'] == 'suspicious']),
            'anomaly_types': df[df['LABEL'] == 'suspicious']['ANOMALY_TYPE'].value_counts().to_dict(),
            'generated_at': datetime.now().isoformat()
        }
        
        stats_path = f"{output_dir}/dataset_stats.json"
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.success(f"📊 Statistiques : {stats_path}")
        
        return csv_path, json_path


def main():
    """Génération du dataset synthétique"""
    logger.info("="*60)
    logger.info("🧪 GÉNÉRATION DE LOGS SYNTHÉTIQUES")
    logger.info("="*60)
    
    generator = SyntheticLogsGenerator()
    
    # Générer le dataset
    df = generator.generate_dataset(num_normal=50, num_suspicious=20)
    
    # Statistiques
    print("\n📊 Statistiques du dataset :")
    print(f"  Total : {len(df)} logs")
    print(f"  Normaux : {len(df[df['LABEL'] == 'normal'])}")
    print(f"  Suspects : {len(df[df['LABEL'] == 'suspicious'])}")
    print("\n  Types d'anomalies :")
    anomaly_counts = df[df['LABEL'] == 'suspicious']['ANOMALY_TYPE'].value_counts()
    for anomaly_type, count in anomaly_counts.items():
        print(f"    • {anomaly_type}: {count}")
    
    # Sauvegarder
    generator.save_dataset(df)
    
    # Aperçu
    print("\n📋 Aperçu des logs suspects :")
    suspicious_sample = df[df['LABEL'] == 'suspicious'].head(3)
    for _, log in suspicious_sample.iterrows():
        print(f"\n  🔴 {log['ANOMALY_TYPE']}")
        print(f"     User: {log['USERNAME']} | Action: {log['ACTION']}")
        print(f"     Object: {log['OBJECT_NAME'][:50]}...")
        print(f"     Time: {log['TIMESTAMP']}")
    
    logger.info("\n✅ GÉNÉRATION TERMINÉE")
    logger.info("📂 Fichiers disponibles dans data/synthetic_data/")


if __name__ == "__main__":
    main()