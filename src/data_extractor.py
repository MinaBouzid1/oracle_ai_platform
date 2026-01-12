"""
Module 1 : Data Extractor - Version Hybride
Support à la fois Oracle Database réel et le simulateur Mock
Mode Mock: Génération automatique de TOUTES les données
"""

import os
import pandas as pd
from dotenv import load_dotenv
from loguru import logger
import sys
from pathlib import Path
import json
from datetime import datetime

# Import du connecteur Oracle
try:
    from oracle_connector import OracleConnector
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False
    logger.warning("⚠️  Oracle connector non disponible")

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

load_dotenv()


class OracleDataExtractor:
    """Extraction de données depuis Oracle Database ou simulateur"""
    
    def __init__(self, use_mock: bool = None, force_mode: str = None):
        """
        Args:
            use_mock: Si True, utilise le simulateur, sinon Oracle réel
                      Si None, détection automatique
            force_mode: 'oracle' ou 'mock' pour forcer le mode
        """
        self.export_dir = Path("data/oracle_exports")
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Déterminer le mode
        if force_mode:
            if force_mode.lower() == 'oracle':
                self.use_mock = False
            elif force_mode.lower() == 'mock':
                self.use_mock = True
            else:
                logger.error(f"❌ Mode inconnu: {force_mode}. Utilisation 'mock' par défaut.")
                self.use_mock = True
        elif use_mock is not None:
            self.use_mock = use_mock
        else:
            # Détection automatique: utiliser mock si Oracle n'est pas disponible
            self.use_mock = not self._check_oracle_availability()
        
        # Initialiser le connecteur approprié
        self.oracle = self._init_connector()
        
        # Statistiques
        self.extraction_stats = {
            'mode': 'mock' if self.use_mock else 'oracle',
            'timestamp': datetime.now().isoformat(),
            'files': {}
        }
    
    def _check_oracle_availability(self) -> bool:
        """Vérifie si Oracle est disponible"""
        if not ORACLE_AVAILABLE:
            logger.warning("⚠️  Oracle connector non installé")
            return False
        
        # Tester la connexion
        try:
            oracle = OracleConnector()
            connected = oracle.connect()
            if connected:
                oracle.disconnect()
                logger.success("✅ Oracle Database disponible")
                return True
            else:
                logger.warning("⚠️  Oracle non accessible")
                return False
        except Exception as e:
            logger.warning(f"⚠️  Erreur connexion Oracle: {e}")
            return False
    
    def _init_connector(self):
        """Initialise le connecteur approprié"""
        if self.use_mock:
            logger.info("🔧 Mode MOCK activé (données simulées)")
            try:
                from mock_oracle import MockOracle
                mock = MockOracle()
                mock.connect()  # Connecter le mock immédiatement
                return mock
            except ImportError:
                logger.error("❌ Module mock_oracle non trouvé")
                logger.info("💡 Créez le fichier mock_oracle.py ou installez Oracle")
                raise
        else:
            logger.info("🚀 Mode ORACLE activé (base réelle)")
            if not ORACLE_AVAILABLE:
                logger.error("❌ Oracle connector non disponible")
                logger.info("💡 Installez: pip install oracledb")
                logger.info("💡 Basculer en mode mock avec: extractor = OracleDataExtractor(use_mock=True)")
                raise ImportError("Oracle connector non disponible")
            
            return OracleConnector(
                host=os.getenv("ORACLE_HOST", "localhost"),
                port=int(os.getenv("ORACLE_PORT", 1521)),
                service_name=os.getenv("ORACLE_SERVICE", "XEPDB1"),
                user=os.getenv("ORACLE_USER", "system"),
                password=os.getenv("ORACLE_PASSWORD", "oracle")
            )
    
    def extract_all(self) -> bool:
        """
        Extrait TOUTES les données automatiquement
        
        Mode MOCK: Génère toutes les données simulées
        Mode ORACLE: Extrait toutes les données réelles
        
        Returns:
            True si succès, False sinon
        """
        logger.info("🚀 Démarrage de l'extraction Oracle Database")
        logger.info("=" * 60)
        logger.info(f"📊 Mode: {'MOCK (données simulées)' if self.use_mock else 'ORACLE (base réelle)'}")
        
        if not self.use_mock:
            # Mode Oracle: besoin de se connecter
            if not self.oracle.connect():
                logger.error("❌ Impossible de se connecter à Oracle")
                logger.info("💡 Voulez-vous basculer en mode MOCK ?")
                logger.info("   extractor = OracleDataExtractor(use_mock=True)")
                return False
        
        try:
            files_extracted = []
            
            # 1. Logs d'audit
            logger.info("📥 Génération des logs d'audit...")
            audit_logs = self.oracle.get_audit_logs(limit=100)
            audit_path = self.export_dir / "audit_logs.csv"
            audit_logs.to_csv(audit_path, index=False)
            logger.success(f"✅ Logs d'audit : {len(audit_logs)} lignes → {audit_path}")
            files_extracted.append(audit_path)
            self.extraction_stats['files']['audit_logs'] = {
                'path': str(audit_path),
                'rows': len(audit_logs),
                'size_kb': os.path.getsize(audit_path) / 1024
            }
            
            # 2. Statistiques SQL
            logger.info("📥 Génération des statistiques SQL...")
            sql_stats = self.oracle.get_sql_statistics(limit=50)
            sql_path = self.export_dir / "sql_stats.csv"
            sql_stats.to_csv(sql_path, index=False)
            logger.success(f"✅ Stats SQL : {len(sql_stats)} lignes → {sql_path}")
            files_extracted.append(sql_path)
            self.extraction_stats['files']['sql_stats'] = {
                'path': str(sql_path),
                'rows': len(sql_stats),
                'size_kb': os.path.getsize(sql_path) / 1024
            }
            
            # 3. Requêtes lentes
            logger.info("📥 Génération des requêtes lentes...")
            slow_queries = self.oracle.get_slow_queries(min_elapsed_sec=0.1, limit=20)
            slow_path = self.export_dir / "slow_queries.csv"
            slow_queries.to_csv(slow_path, index=False)
            logger.success(f"✅ Requêtes lentes : {len(slow_queries)} lignes → {slow_path}")
            files_extracted.append(slow_path)
            self.extraction_stats['files']['slow_queries'] = {
                'path': str(slow_path),
                'rows': len(slow_queries),
                'size_kb': os.path.getsize(slow_path) / 1024
            }
            
            # 4. Utilisateurs et rôles
            logger.info("📥 Génération des utilisateurs et rôles...")
            users_data = self.oracle.get_users_and_roles()
            
            users_path = self.export_dir / "users.csv"
            users_data['users'].to_csv(users_path, index=False)
            logger.success(f"✅ Utilisateurs : {len(users_data['users'])} lignes → {users_path}")
            files_extracted.append(users_path)
            self.extraction_stats['files']['users'] = {
                'path': str(users_path),
                'rows': len(users_data['users']),
                'size_kb': os.path.getsize(users_path) / 1024
            }
            
            roles_path = self.export_dir / "user_roles.csv"
            users_data['roles'].to_csv(roles_path, index=False)
            logger.success(f"✅ Rôles : {len(users_data['roles'])} lignes → {roles_path}")
            files_extracted.append(roles_path)
            self.extraction_stats['files']['user_roles'] = {
                'path': str(roles_path),
                'rows': len(users_data['roles']),
                'size_kb': os.path.getsize(roles_path) / 1024
            }
            
            # 5. Privilèges système
            logger.info("📥 Génération des privilèges système...")
            sys_privs = self.oracle.get_system_privileges()
            privs_path = self.export_dir / "system_privileges.csv"
            sys_privs.to_csv(privs_path, index=False)
            logger.success(f"✅ Privilèges : {len(sys_privs)} lignes → {privs_path}")
            files_extracted.append(privs_path)
            self.extraction_stats['files']['system_privileges'] = {
                'path': str(privs_path),
                'rows': len(sys_privs),
                'size_kb': os.path.getsize(privs_path) / 1024
            }
            
            # 6. Tablespaces
            logger.info("📥 Génération des tablespaces...")
            tablespaces = self.oracle.get_tablespace_usage()
            ts_path = self.export_dir / "tablespaces.csv"
            tablespaces.to_csv(ts_path, index=False)
            logger.success(f"✅ Tablespaces : {len(tablespaces)} lignes → {ts_path}")
            files_extracted.append(ts_path)
            self.extraction_stats['files']['tablespaces'] = {
                'path': str(ts_path),
                'rows': len(tablespaces),
                'size_kb': os.path.getsize(ts_path) / 1024
            }
            
            # 7. Taille de la base
            logger.info("📥 Génération de la taille de la base...")
            db_size = self.oracle.get_database_size()
            size_path = self.export_dir / "database_metrics.json"
            with open(size_path, 'w') as f:
                json.dump(db_size, f, indent=2)
            logger.success(f"✅ Métriques DB → {size_path}")
            files_extracted.append(size_path)
            self.extraction_stats['files']['database_metrics'] = {
                'path': str(size_path),
                'rows': 1,
                'size_kb': os.path.getsize(size_path) / 1024
            }
            
            # 8. Fichier de configuration de sécurité (pour Module 4)
            logger.info("📥 Génération de la configuration de sécurité...")
            security_config = self._generate_security_config()
            security_path = self.export_dir / "security_config_users.csv"
            security_config.to_csv(security_path, index=False)
            logger.success(f"✅ Configuration sécurité : {len(security_config)} lignes → {security_path}")
            files_extracted.append(security_path)
            self.extraction_stats['files']['security_config'] = {
                'path': str(security_path),
                'rows': len(security_config),
                'size_kb': os.path.getsize(security_path) / 1024
            }
            
            # 9. Fichier de privilèges de sécurité
            logger.info("📥 Génération des privilèges de sécurité...")
            security_privs = self._generate_security_privileges()
            security_privs_path = self.export_dir / "security_config_privileges.csv"
            security_privs.to_csv(security_privs_path, index=False)
            logger.success(f"✅ Privilèges sécurité : {len(security_privs)} lignes → {security_privs_path}")
            files_extracted.append(security_privs_path)
            
            # 10. Créer un fichier de métadonnées
            metadata = {
                'extraction_mode': 'mock' if self.use_mock else 'oracle',
                'timestamp': datetime.now().isoformat(),
                'total_files': len(files_extracted),
                'total_rows': sum([
                    len(audit_logs), len(sql_stats), len(slow_queries),
                    len(users_data['users']), len(users_data['roles']),
                    len(sys_privs), len(tablespaces), len(security_config),
                    len(security_privs)
                ]),
                'files': {f.name: os.path.getsize(f) for f in files_extracted}
            }
            
            metadata_path = self.export_dir / "extraction_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"📄 Métadonnées : {metadata_path}")
            
            logger.success("=" * 60)
            logger.success("✅ EXTRACTION TERMINÉE")
            logger.info(f"\n📊 RÉSUMÉ (Mode: {'MOCK' if self.use_mock else 'ORACLE'}):")
            logger.info(f"   - Logs d'audit: {len(audit_logs)}")
            logger.info(f"   - Statistiques SQL: {len(sql_stats)}")
            logger.info(f"   - Requêtes lentes: {len(slow_queries)}")
            logger.info(f"   - Utilisateurs: {len(users_data['users'])}")
            logger.info(f"   - Rôles: {len(users_data['roles'])}")
            logger.info(f"   - Privilèges: {len(sys_privs)}")
            logger.info(f"   - Tablespaces: {len(tablespaces)}")
            logger.info(f"   - Config sécurité: {len(security_config)}")
            logger.info(f"   - Privilèges sécurité: {len(security_privs)}")
            
            if 'total_size_gb' in db_size:
                logger.info(f"   - Taille DB: {db_size['total_size_gb']:.2f} GB")
            
            logger.info(f"\n💾 Fichiers générés: {len(files_extracted)}")
            for file in files_extracted:
                size_kb = os.path.getsize(file) / 1024
                logger.info(f"   • {file.name} ({size_kb:.1f} KB)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
            
        finally:
            if not self.use_mock:
                self.oracle.disconnect()
    
    def _generate_security_config(self):
        """Génère une configuration de sécurité pour le Module 4"""
        users = []
        statuses = ['OPEN', 'LOCKED', 'EXPIRED', 'EXPIRED(GRACE)']
        profiles = ['DEFAULT', 'MONITORING_PROFILE', 'APP_PROFILE', 'ADMIN_PROFILE']
        
        for i in range(12):
            users.append({
                'USERNAME': f'USER_{i:03d}',
                'ACCOUNT_STATUS': random.choice(statuses),
                'PROFILE': random.choice(profiles),
                'CREATED': (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
            })
        
        # Ajouter quelques utilisateurs à risque
        users.append({
            'USERNAME': 'TEST_USER',
            'ACCOUNT_STATUS': 'OPEN',
            'PROFILE': 'DEFAULT',
            'CREATED': '2020-01-15'
        })
        
        users.append({
            'USERNAME': 'ADMIN_BACKUP',
            'ACCOUNT_STATUS': 'OPEN',
            'PROFILE': 'DEFAULT',
            'CREATED': '2019-03-20'
        })
        
        return pd.DataFrame(users)
    
    def _generate_security_privileges(self):
        """Génère des privilèges de sécurité pour le Module 4"""
        import random
        
        privileges = []
        users = [f'USER_{i:03d}' for i in range(8)] + ['TEST_USER', 'ADMIN_BACKUP']
        dangerous_privs = ['DROP ANY TABLE', 'ALTER SYSTEM', 'GRANT ANY PRIVILEGE', 
                          'CREATE USER', 'DROP USER', 'ALTER DATABASE']
        normal_privs = ['CREATE SESSION', 'CREATE TABLE', 'SELECT ANY TABLE', 
                       'INSERT ANY TABLE', 'UPDATE ANY TABLE']
        
        for user in users:
            # Ajouter quelques privilèges normaux
            for _ in range(random.randint(2, 4)):
                privileges.append({
                    'GRANTEE': user,
                    'PRIVILEGE': random.choice(normal_privs),
                    'ADMIN_OPTION': random.choice(['YES', 'NO'])
                })
            
            # Ajouter occasionnellement un privilège dangereux
            if random.random() < 0.3:  # 30% de chance
                privileges.append({
                    'GRANTEE': user,
                    'PRIVILEGE': random.choice(dangerous_privs),
                    'ADMIN_OPTION': random.choice(['YES', 'NO'])
                })
        
        return pd.DataFrame(privileges)
    
    def switch_mode(self, use_mock: bool):
        """Change le mode d'extraction"""
        old_mode = 'MOCK' if self.use_mock else 'ORACLE'
        self.use_mock = use_mock
        new_mode = 'MOCK' if self.use_mock else 'ORACLE'
        
        logger.info(f"🔄 Changement de mode: {old_mode} → {new_mode}")
        self.oracle = self._init_connector()
    
    def get_stats(self):
        """Retourne les statistiques de l'extraction"""
        return self.extraction_stats
    
    def quick_extract(self, mode='auto'):
        """
        Extraction rapide sans menu interactif
        
        Args:
            mode: 'auto', 'oracle', ou 'mock'
        """
        if mode == 'oracle':
            extractor = OracleDataExtractor(force_mode='oracle')
        elif mode == 'mock':
            extractor = OracleDataExtractor(force_mode='mock')
        else:  # auto
            extractor = OracleDataExtractor()
        
        success = extractor.extract_all()
        
        if success:
            stats = extractor.get_stats()
            print(f"\n✅ Extraction {stats['mode']} terminée avec succès!")
            print(f"📁 Données dans: data/oracle_exports/")
        else:
            print("\n❌ Échec de l'extraction")
        
        return success


def main():
    """Fonction principale avec options simples"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extracteur de données Oracle')
    parser.add_argument('--mode', choices=['auto', 'oracle', 'mock'], default='auto',
                       help='Mode d\'extraction (auto/oracle/mock)')
    parser.add_argument('--quick', action='store_true',
                       help='Extraction rapide sans menu interactif')
    
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("MODULE 1 : EXTRACTION DE DONNÉES ORACLE")
    logger.info("="*60)
    
    if args.quick:
        # Mode rapide: extraire directement sans menu
        extractor = OracleDataExtractor()
        if args.mode != 'auto':
            extractor = OracleDataExtractor(force_mode=args.mode)
        
        extractor.extract_all()
        
    else:
        # Mode interactif simplifié
        print(f"\n🎯 Mode sélectionné: {args.mode.upper()}")
        print("   L'extraction générera TOUTES les données automatiquement.")
        print("   Appuyez sur Entrée pour continuer ou Ctrl+C pour annuler...")
        
        try:
            input()
        except KeyboardInterrupt:
            logger.info("\n👋 Opération annulée")
            return
        
        # Créer l'extracteur
        if args.mode == 'oracle':
            extractor = OracleDataExtractor(force_mode='oracle')
        elif args.mode == 'mock':
            extractor = OracleDataExtractor(force_mode='mock')
        else:  # auto
            extractor = OracleDataExtractor()
        
        # Exécuter l'extraction complète
        success = extractor.extract_all()
        
        if success:
            stats = extractor.get_stats()
            print(f"\n🎉 EXTRACTION {stats['mode'].upper()} RÉUSSIE!")
            print(f"📊 Fichiers générés: {len(stats.get('files', {}))}")
            print(f"💾 Répertoire: data/oracle_exports/")
    
    logger.info("\n✅ MODULE 1 TERMINÉ")


# Ajouter ces imports au début du fichier si nécessaire
import random
from datetime import timedelta

if __name__ == "__main__":
    main()