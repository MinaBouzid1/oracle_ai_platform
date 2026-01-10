"""
Module 8 : Recovery Guide
Guide interactif de restauration et récupération Oracle
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger
import sys
import os

from llm_engine import LLMEngine
from rag_setup import OracleRAGSystem

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


class RecoveryGuide:
    """Guide de récupération Oracle assisté par IA"""
    
    def __init__(self):
        self.llm = LLMEngine()
        self.rag = OracleRAGSystem()
        self.current_playbook = None
        
        # Scénarios supportés
        self.scenarios = {
            '1': {
                'name': 'complete_restore',
                'title': 'Restauration complète après crash',
                'description': 'Base de données complètement indisponible, nécessite restauration totale'
            },
            '2': {
                'name': 'point_in_time',
                'title': 'Récupération point-in-time (PITR)',
                'description': 'Récupération à une date/heure spécifique'
            },
            '3': {
                'name': 'table_recovery',
                'title': 'Récupération de table',
                'description': 'Récupération d\'une table supprimée ou corrompue'
            },
            '4': {
                'name': 'tablespace_recovery',
                'title': 'Récupération de tablespace',
                'description': 'Récupération d\'un tablespace spécifique'
            }
        }
        
        logger.info("🔧 Initialisation du Recovery Guide")
    
    def start_recovery_wizard(self) -> Dict:
        """Lance l'assistant de récupération interactif"""
        print("\n" + "="*60)
        print("🚨 ASSISTANT DE RÉCUPÉRATION ORACLE")
        print("="*60)
        
        print("\n⚠️  Choisissez votre scénario de récupération :\n")
        
        for key, scenario in self.scenarios.items():
            print(f"   {key}) {scenario['title']}")
            print(f"      {scenario['description']}\n")
        
        choice = input("Votre choix (1-4) : ").strip()
        
        if choice not in self.scenarios:
            logger.error("❌ Choix invalide")
            return {}
        
        scenario = self.scenarios[choice]
        logger.info(f"\n📋 Scénario sélectionné : {scenario['title']}")
        
        # Collecter les informations selon le scénario
        if scenario['name'] == 'complete_restore':
            details = self._collect_complete_restore_info()
        elif scenario['name'] == 'point_in_time':
            details = self._collect_pitr_info()
        elif scenario['name'] == 'table_recovery':
            details = self._collect_table_recovery_info()
        elif scenario['name'] == 'tablespace_recovery':
            details = self._collect_tablespace_recovery_info()
        else:
            details = {}
        
        # Générer le playbook
        print("\n⏳ Génération du playbook de récupération...\n")
        playbook = self.generate_playbook(scenario['name'], details)
        
        return playbook
    
    def _collect_complete_restore_info(self) -> Dict:
        """Collecte les infos pour restauration complète"""
        print("\n📝 Informations nécessaires :\n")
        
        has_rman = input("1. Avez-vous des backups RMAN ? (oui/non) : ").strip().lower()
        has_archive = input("2. Avez-vous les archive logs ? (oui/non) : ").strip().lower()
        last_backup = input("3. Date du dernier backup (ex: 2024-01-15) : ").strip()
        target_scn = input("4. SCN ou timestamp cible (laisser vide pour latest) : ").strip() or "latest"
        
        return {
            'has_rman_backups': 'oui' in has_rman,
            'has_archive_logs': 'oui' in has_archive,
            'last_backup_date': last_backup,
            'target': target_scn,
            'scenario_type': 'crash_recovery'
        }
    
    def _collect_pitr_info(self) -> Dict:
        """Collecte les infos pour Point-In-Time Recovery"""
        print("\n📝 Informations nécessaires :\n")
        
        target_time = input("1. Date/heure cible (ex: 2024-01-15 14:30:00) : ").strip()
        tablespaces = input("2. Tablespaces affectés (séparés par virgule, ou 'all') : ").strip()
        has_archive = input("3. Archive logs disponibles ? (oui/non) : ").strip().lower()
        
        return {
            'target_time': target_time,
            'tablespaces': tablespaces.split(',') if tablespaces.lower() != 'all' else ['all'],
            'has_archive_logs': 'oui' in has_archive,
            'scenario_type': 'point_in_time'
        }
    
    def _collect_table_recovery_info(self) -> Dict:
        """Collecte les infos pour récupération de table"""
        print("\n📝 Informations nécessaires :\n")
        
        table_name = input("1. Nom de la table : ").strip().upper()
        action = input("2. Action (DROP/TRUNCATE/UPDATE) : ").strip().upper()
        incident_time = input("3. Timestamp de l'incident (ex: 2024-01-15 10:00:00) : ").strip()
        flashback = input("4. Flashback activé ? (oui/non) : ").strip().lower()
        
        return {
            'table_name': table_name,
            'action': action,
            'incident_time': incident_time,
            'flashback_enabled': 'oui' in flashback,
            'scenario_type': 'table_recovery'
        }
    
    def _collect_tablespace_recovery_info(self) -> Dict:
        """Collecte les infos pour récupération de tablespace"""
        print("\n📝 Informations nécessaires :\n")
        
        tablespace_name = input("1. Nom du tablespace : ").strip().upper()
        reason = input("2. Raison (corruption/suppression/autre) : ").strip()
        has_backup = input("3. Backup du tablespace disponible ? (oui/non) : ").strip().lower()
        
        return {
            'tablespace_name': tablespace_name,
            'reason': reason,
            'has_backup': 'oui' in has_backup,
            'scenario_type': 'tablespace_recovery'
        }
    
    def generate_playbook(self, scenario: str, details: Dict) -> Dict:
        """
        Génère un playbook détaillé de récupération
        
        Args:
            scenario: Type de scénario ('complete_restore', 'point_in_time', etc.)
            details: Détails collectés du scénario
        
        Returns:
            Playbook complet avec étapes, commandes, validations
        """
        logger.info(f"🤖 Génération du playbook pour : {scenario}")
        
        # Récupérer le context RAG
        search_query = f"Oracle recovery {scenario} RMAN restore flashback procedure"
        context_docs = self.rag.retrieve_context(search_query, top_k=4)
        context = "\n\n".join([doc['document'] for doc in context_docs])
        
        # Générer avec l'IA
        try:
            playbook_text = self.llm.guide_recovery(
                scenario=scenario,
                details=details,
                context=context
            )
            
            # Parser et structurer le playbook
            playbook = self._parse_playbook(playbook_text, scenario, details)
            
            self.current_playbook = playbook
            logger.success("✅ Playbook généré")
            
            return playbook
            
        except Exception as e:
            logger.error(f"❌ Erreur génération playbook : {e}")
            return {'error': str(e)}
    
    def _parse_playbook(self, playbook_text: str, scenario: str, details: Dict) -> Dict:
        """Parse et structure le playbook"""
        playbook = {
            'scenario': scenario,
            'details': details,
            'generated_at': datetime.now().isoformat(),
            'content': playbook_text,
            'metadata': {
                'estimated_duration': self._estimate_duration(scenario, details),
                'risk_level': self._assess_risk(scenario, details),
                'prerequisites': self._list_prerequisites(scenario, details)
            }
        }
        
        return playbook
    
    def _estimate_duration(self, scenario: str, details: Dict) -> str:
        """Estime la durée de la procédure"""
        durations = {
            'complete_restore': '2-6 heures',
            'point_in_time': '1-4 heures',
            'table_recovery': '15-60 minutes',
            'tablespace_recovery': '30 minutes - 2 heures'
        }
        return durations.get(scenario, '1-3 heures')
    
    def _assess_risk(self, scenario: str, details: Dict) -> str:
        """Évalue le niveau de risque"""
        if scenario == 'complete_restore':
            return 'ÉLEVÉ - Perte de données possible si mal exécuté'
        elif scenario == 'point_in_time':
            return 'MOYEN - Transactions après le point de récupération seront perdues'
        elif scenario == 'table_recovery':
            if details.get('flashback_enabled'):
                return 'FAIBLE - Flashback permet récupération sûre'
            else:
                return 'MOYEN - Sans flashback, utilisation de backup nécessaire'
        else:
            return 'MOYEN'
    
    def _list_prerequisites(self, scenario: str, details: Dict) -> List[str]:
        """Liste les prérequis"""
        prereqs = [
            'Accès SYSDBA à la base Oracle',
            'Espace disque suffisant pour la restauration',
            'Backups RMAN valides et accessibles'
        ]
        
        if scenario in ['complete_restore', 'point_in_time']:
            prereqs.append('Archive logs nécessaires disponibles')
        
        if scenario == 'table_recovery' and not details.get('flashback_enabled'):
            prereqs.append('Backup contenant la table cible')
        
        return prereqs
    
    def save_playbook(self, output_dir='data/oracle_exports/recovery_playbooks'):
        """Sauvegarde le playbook"""
        if not self.current_playbook:
            logger.warning("Aucun playbook à sauvegarder")
            return None
        
        os.makedirs(output_dir, exist_ok=True)
        
        scenario = self.current_playbook.get('scenario', 'unknown')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/playbook_{scenario}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.current_playbook, f, indent=2, ensure_ascii=False)
        
        logger.success(f"💾 Playbook sauvegardé : {filename}")
        
        # Sauvegarder aussi en texte pour faciliter la lecture
        text_filename = filename.replace('.json', '.txt')
        with open(text_filename, 'w', encoding='utf-8') as f:
            f.write(self.format_playbook_for_print())
        
        logger.info(f"   📄 Version texte : {text_filename}")
        
        return filename
    
    def format_playbook_for_print(self) -> str:
        """Formate le playbook pour affichage/impression"""
        if not self.current_playbook:
            return "Aucun playbook disponible"
        
        pb = self.current_playbook
        
        output = []
        output.append("="*70)
        output.append("🚨 PLAYBOOK DE RÉCUPÉRATION ORACLE")
        output.append("="*70)
        output.append("")
        output.append(f"📋 Scénario : {pb.get('scenario', 'N/A').replace('_', ' ').title()}")
        output.append(f"⏰ Généré le : {pb.get('generated_at', 'N/A')}")
        output.append("")
        output.append("📊 MÉTADONNÉES")
        output.append("-" * 70)
        
        metadata = pb.get('metadata', {})
        output.append(f"⏱️  Durée estimée : {metadata.get('estimated_duration', 'N/A')}")
        output.append(f"⚠️  Niveau de risque : {metadata.get('risk_level', 'N/A')}")
        output.append("")
        output.append("✅ PRÉREQUIS :")
        for prereq in metadata.get('prerequisites', []):
            output.append(f"   • {prereq}")
        output.append("")
        output.append("="*70)
        output.append("📝 PROCÉDURE DÉTAILLÉE")
        output.append("="*70)
        output.append("")
        output.append(pb.get('content', 'Contenu non disponible'))
        output.append("")
        output.append("="*70)
        output.append("✅ FIN DU PLAYBOOK")
        output.append("="*70)
        
        return "\n".join(output)
    
    def print_playbook(self):
        """Affiche le playbook à l'écran"""
        print("\n" + self.format_playbook_for_print())
    
    def quick_scenarios(self):
        """Génère des playbooks pour les 4 scénarios principaux (non-interactif)"""
        logger.info("🚀 Génération des playbooks pour tous les scénarios")
        
        # Scénario 1 : Restauration complète
        logger.info("\n1️⃣  Restauration complète...")
        pb1 = self.generate_playbook('complete_restore', {
            'has_rman_backups': True,
            'has_archive_logs': True,
            'last_backup_date': '2024-01-15',
            'target': 'latest',
            'scenario_type': 'crash_recovery'
        })
        
        # Scénario 2 : PITR
        logger.info("\n2️⃣  Point-in-time recovery...")
        pb2 = self.generate_playbook('point_in_time', {
            'target_time': '2024-01-15 14:30:00',
            'tablespaces': ['USERS', 'DATA'],
            'has_archive_logs': True,
            'scenario_type': 'point_in_time'
        })
        
        # Scénario 3 : Table recovery
        logger.info("\n3️⃣  Récupération de table...")
        pb3 = self.generate_playbook('table_recovery', {
            'table_name': 'EMPLOYEES',
            'action': 'DROP',
            'incident_time': '2024-01-15 10:00:00',
            'flashback_enabled': True,
            'scenario_type': 'table_recovery'
        })
        
        # Scénario 4 : Tablespace recovery
        logger.info("\n4️⃣  Récupération de tablespace...")
        pb4 = self.generate_playbook('tablespace_recovery', {
            'tablespace_name': 'USERS',
            'reason': 'corruption',
            'has_backup': True,
            'scenario_type': 'tablespace_recovery'
        })
        
        self.current_playbook = pb1  # Garder le premier pour l'exemple
        
        logger.success("\n✅ 4 playbooks générés")
        
        return [pb1, pb2, pb3, pb4]


def main():
    """Fonction principale"""
    logger.info("="*60)
    logger.info("MODULE 8 : RESTAURATION & RÉCUPÉRATION ASSISTÉE")
    logger.info("="*60)
    
    # Initialiser le guide
    guide = RecoveryGuide()
    
    # Mode de fonctionnement
    print("\n🎯 Mode de fonctionnement :")
    print("   1) Mode interactif (assistant)")
    print("   2) Mode automatique (générer les 4 scénarios)")
    mode = input("Votre choix (1/2) : ").strip()
    
    if mode == '1':
        # Mode interactif
        playbook = guide.start_recovery_wizard()
        
        if playbook and 'error' not in playbook:
            # Afficher le playbook
            guide.print_playbook()
            
            # Sauvegarder
            guide.save_playbook()
    else:
        # Mode automatique
        playbooks = guide.quick_scenarios()
        
        # Afficher le premier comme exemple
        guide.print_playbook()
        
        # Sauvegarder tous
        for i, pb in enumerate(playbooks, 1):
            guide.current_playbook = pb
            guide.save_playbook()
    
    logger.info("\n✅ MODULE 8 TERMINÉ")
    logger.info("📂 Playbooks disponibles dans data/oracle_exports/recovery_playbooks/")


if __name__ == "__main__":
    main()