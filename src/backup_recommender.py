"""
Module 7 : Backup Recommender
Recommandation intelligente de stratégies de sauvegarde Oracle
"""

import json
from datetime import datetime
from typing import Dict, List
from loguru import logger
import sys
import os

from llm_engine import LLMEngine
from rag_setup import OracleRAGSystem

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


class BackupRecommender:
    """Recommandateur de stratégies de sauvegarde Oracle"""
    
    def __init__(self):
        self.llm = LLMEngine()
        self.rag = OracleRAGSystem()
        self.recommendations = {}
        
        # Templates de stratégies pré-définies
        self.strategy_templates = {
            'critical_24x7': {
                'description': 'Mission critique 24/7',
                'rpo_max': '15 minutes',
                'rto_max': '1 heure',
                'backup_types': ['archive_logs', 'incremental', 'complete']
            },
            'production_business_hours': {
                'description': 'Production heures ouvrables',
                'rpo_max': '4 heures',
                'rto_max': '4 heures',
                'backup_types': ['incremental', 'complete']
            },
            'development': {
                'description': 'Développement/Test',
                'rpo_max': '24 heures',
                'rto_max': '8 heures',
                'backup_types': ['complete']
            }
        }
        
        logger.info("💾 Initialisation du Backup Recommender")
    
    def recommend_strategy(
        self,
        rpo: str,
        rto: str,
        db_size: str,
        criticality: str,
        budget: str,
        transaction_volume: str = "moyen"
    ) -> Dict:
        """
        Recommande une stratégie de sauvegarde optimale
        
        Args:
            rpo: Recovery Point Objective (ex: "15 minutes", "4 heures", "1 jour")
            rto: Recovery Time Objective (ex: "1 heure", "4 heures", "1 jour")
            db_size: Taille de la base (ex: "10GB", "500GB", "2TB")
            criticality: Criticité ("critique", "haute", "moyenne", "faible")
            budget: Budget disponible ("illimité", "élevé", "moyen", "limité")
            transaction_volume: Volume de transactions ("très élevé", "élevé", "moyen", "faible")
        
        Returns:
            Stratégie recommandée avec script RMAN
        """
        logger.info("="*60)
        logger.info("💾 RECOMMANDATION DE STRATÉGIE DE SAUVEGARDE")
        logger.info("="*60)
        
        logger.info(f"\n📋 Exigences :")
        logger.info(f"   RPO : {rpo}")
        logger.info(f"   RTO : {rto}")
        logger.info(f"   Taille DB : {db_size}")
        logger.info(f"   Criticité : {criticality}")
        logger.info(f"   Budget : {budget}")
        logger.info(f"   Volume transactions : {transaction_volume}")
        
        # Récupérer le context RAG
        search_query = f"stratégie sauvegarde Oracle RMAN RPO RTO {criticality} archive logs"
        context_docs = self.rag.retrieve_context(search_query, top_k=4)
        context = "\n\n".join([doc['document'] for doc in context_docs])
        
        # Préparer les paramètres pour le LLM
        requirements = {
            'rpo': rpo,
            'rto': rto,
            'db_size': db_size,
            'criticality': criticality,
            'budget': budget,
            'transaction_volume': transaction_volume
        }
        
        # Génération de la stratégie
        logger.info("\n🤖 Génération de la stratégie...")
        
        # Utilisation directe de la génération basée sur règles
        # (contourne les problèmes de parsing JSON avec certains modèles)
        recommendation = self._build_fallback_strategy(
            rpo, rto, db_size, criticality, budget, transaction_volume, ""
        )
        
        # Enrichir avec des scripts RMAN détaillés
        recommendation = self._enrich_with_rman_scripts(recommendation)
        
        # Ajouter métadonnées
        recommendation['input_requirements'] = requirements
        recommendation['timestamp'] = datetime.now().isoformat()
        
        # Sauvegarder
        self.recommendations = recommendation
        
        logger.success("✅ Stratégie recommandée générée")
        
        return recommendation
    
    def _build_fallback_strategy(
        self,
        rpo: str,
        rto: str, 
        db_size: str,
        criticality: str,
        budget: str,
        transaction_volume: str,
        raw_response: str = ""
    ) -> Dict:
        """
        Construit une stratégie de secours basée sur des règles métier
        """
        logger.info("🔧 Génération d'une stratégie basée sur les règles métier...")
        
        # Extraction depuis raw_response si disponible
        import re
        
        def extract_field(text, field):
            pattern = rf'"{field}"\s*:\s*"([^"]+)"'
            match = re.search(pattern, text)
            return match.group(1) if match else None
        
        # Déterminer la stratégie selon la criticité
        if criticality.lower() in ['critique', 'critical']:
            strategy = {
                'strategie_recommandee': 'Mission Critique 24/7',
                'type_backup': 'Incrémentale',
                'frequence': {
                    'complete': 'Quotidienne (3h du matin)',
                    'incrementale': 'Toutes les 2 heures',
                    'archive_logs': 'Toutes les 15 minutes'
                },
                'retention': '30 jours',
                'stockage': '/u01/backup/oracle (disk primaire) + cloud secondaire',
                'cout_estime': 'Élevé (4000-6000€/mois)',
                'justification': f'RPO de {rpo} et RTO de {rto} nécessitent des backups très fréquents avec architecture redondante pour garantir haute disponibilité.'
            }
        elif criticality.lower() in ['haute', 'high', 'élevée']:
            strategy = {
                'strategie_recommandee': 'Production Haute Disponibilité',
                'type_backup': 'Incrémentale',
                'frequence': {
                    'complete': 'Hebdomadaire (dimanche 2h)',
                    'incrementale': 'Quotidienne (23h)',
                    'archive_logs': 'Horaire'
                },
                'retention': '14 jours',
                'stockage': '/u01/backup/oracle (NAS) + bandes mensuelles',
                'cout_estime': 'Moyen (2000-3000€/mois)',
                'justification': f'RPO {rpo} et RTO {rto} avec criticité haute. Backups quotidiens incrémentaux + archive logs horaires assurent récupération rapide.'
            }
        elif criticality.lower() in ['moyenne', 'medium', 'normal']:
            strategy = {
                'strategie_recommandee': 'Production Standard',
                'type_backup': 'Différentielle',
                'frequence': {
                    'complete': 'Hebdomadaire (samedi 23h)',
                    'incrementale': 'Quotidienne (2h)',
                    'archive_logs': 'Toutes les 4 heures'
                },
                'retention': '7 jours',
                'stockage': '/u01/backup/oracle (disk local)',
                'cout_estime': 'Moyen-Faible (1000-1500€/mois)',
                'justification': f'Configuration équilibrée pour {db_size}. Criticité moyenne permet RPO {rpo} avec backups quotidiens.'
            }
        else:  # faible
            strategy = {
                'strategie_recommandee': 'Développement/Test',
                'type_backup': 'Complète',
                'frequence': {
                    'complete': 'Quotidienne (3h)',
                    'incrementale': 'Non applicable',
                    'archive_logs': 'Quotidienne (avec backup complet)'
                },
                'retention': '3 jours',
                'stockage': '/u01/backup/oracle (disk local)',
                'cout_estime': 'Faible (300-500€/mois)',
                'justification': 'Environnement non-critique. Backups complets quotidiens suffisants pour récupération standard.'
            }
        
        # Tenter d'extraire des infos du raw_response si disponible
        if raw_response:
            extracted_strategy = extract_field(raw_response, 'strategie_recommandee')
            if extracted_strategy:
                strategy['strategie_recommandee'] = extracted_strategy
            
            extracted_type = extract_field(raw_response, 'type_backup')
            if extracted_type:
                strategy['type_backup'] = extracted_type
        
        logger.success(f"✅ Stratégie générée : {strategy['strategie_recommandee']}")
        
        return strategy
    
    def _enrich_with_rman_scripts(self, recommendation: Dict) -> Dict:
        """Enrichit la recommandation avec des scripts RMAN complets"""
        
        # Script de configuration RMAN
        config_script = """
-- Configuration RMAN
CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF {retention} DAYS;
CONFIGURE CONTROLFILE AUTOBACKUP ON;
CONFIGURE CONTROLFILE AUTOBACKUP FORMAT FOR DEVICE TYPE DISK TO '{backup_location}/%F';
CONFIGURE DEVICE TYPE DISK PARALLELISM {parallelism};
CONFIGURE COMPRESSION ALGORITHM 'MEDIUM';
"""
        
        # Script de sauvegarde complète
        full_backup_script = """
-- Sauvegarde complète
RUN {{
  ALLOCATE CHANNEL ch1 DEVICE TYPE DISK FORMAT '{backup_location}/full_%U';
  BACKUP AS COMPRESSED BACKUPSET
    DATABASE
    PLUS ARCHIVELOG DELETE INPUT;
  BACKUP CURRENT CONTROLFILE FORMAT '{backup_location}/control_%U';
  BACKUP SPFILE FORMAT '{backup_location}/spfile_%U';
  RELEASE CHANNEL ch1;
}}
"""
        
        # Script de sauvegarde incrémentale
        incremental_backup_script = """
-- Sauvegarde incrémentale niveau 1
RUN {{
  ALLOCATE CHANNEL ch1 DEVICE TYPE DISK FORMAT '{backup_location}/incr_%U';
  BACKUP AS COMPRESSED BACKUPSET
    INCREMENTAL LEVEL 1
    DATABASE
    PLUS ARCHIVELOG DELETE INPUT;
  RELEASE CHANNEL ch1;
}}
"""
        
        # Script d'archivage des logs
        archive_log_script = """
-- Sauvegarde des archive logs
RUN {{
  ALLOCATE CHANNEL ch1 DEVICE TYPE DISK FORMAT '{backup_location}/arch_%U';
  BACKUP AS COMPRESSED BACKUPSET
    ARCHIVELOG ALL DELETE INPUT;
  RELEASE CHANNEL ch1;
}}
"""
        
        # Ajouter les scripts avec variables remplies
        backup_location = '/u01/backup/oracle'
        retention = recommendation.get('retention', '7 jours').split()[0]
        parallelism = '2'
        
        recommendation['scripts'] = {
            'configuration': config_script.format(
                retention=retention,
                backup_location=backup_location,
                parallelism=parallelism
            ),
            'full_backup': full_backup_script.format(backup_location=backup_location),
            'incremental_backup': incremental_backup_script.format(backup_location=backup_location),
            'archive_log_backup': archive_log_script.format(backup_location=backup_location)
        }
        
        # Script de planification cron
        cron_schedule = self._generate_cron_schedule(recommendation)
        recommendation['cron_schedule'] = cron_schedule
        
        return recommendation
    
    def _generate_cron_schedule(self, recommendation: Dict) -> List[Dict]:
        """Génère un planning cron pour les sauvegardes"""
        schedule = []
        
        frequence = recommendation.get('frequence', {})
        
        # Sauvegarde complète
        if 'complete' in frequence:
            freq = frequence['complete'].lower()
            if 'quotidien' in freq:
                schedule.append({
                    'type': 'full_backup',
                    'cron': '0 2 * * *',
                    'description': 'Sauvegarde complète quotidienne à 2h00'
                })
            elif 'hebdomadaire' in freq:
                schedule.append({
                    'type': 'full_backup',
                    'cron': '0 2 * * 0',
                    'description': 'Sauvegarde complète hebdomadaire le dimanche à 2h00'
                })
        
        # Sauvegarde incrémentale
        if 'incrementale' in frequence:
            freq = frequence['incrementale'].lower()
            if 'horaire' in freq or 'heure' in freq:
                schedule.append({
                    'type': 'incremental_backup',
                    'cron': '0 * * * *',
                    'description': 'Sauvegarde incrémentale toutes les heures'
                })
            elif 'quotidien' in freq:
                schedule.append({
                    'type': 'incremental_backup',
                    'cron': '0 23 * * *',
                    'description': 'Sauvegarde incrémentale quotidienne à 23h00'
                })
        
        # Archive logs
        if 'archive_logs' in frequence:
            freq = frequence['archive_logs'].lower()
            if '15' in freq and 'minute' in freq:
                schedule.append({
                    'type': 'archive_log_backup',
                    'cron': '*/15 * * * *',
                    'description': 'Sauvegarde archive logs toutes les 15 minutes'
                })
            elif 'horaire' in freq or 'heure' in freq:
                schedule.append({
                    'type': 'archive_log_backup',
                    'cron': '0 * * * *',
                    'description': 'Sauvegarde archive logs toutes les heures'
                })
        
        return schedule
    
    def save_strategy(self, output_dir='data/oracle_exports/backup_strategies'):
        """Sauvegarde la stratégie recommandée"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/backup_strategy_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.recommendations, f, indent=2, ensure_ascii=False)
        
        logger.success(f"💾 Stratégie sauvegardée : {filename}")
        
        # Sauvegarder aussi les scripts séparément
        scripts_dir = f"{output_dir}/scripts"
        os.makedirs(scripts_dir, exist_ok=True)
        
        if 'scripts' in self.recommendations:
            for script_name, script_content in self.recommendations['scripts'].items():
                script_file = f"{scripts_dir}/{script_name}_{timestamp}.sql"
                with open(script_file, 'w') as f:
                    f.write(script_content)
                logger.info(f"   📜 Script : {script_file}")
        
        return filename
    
    def print_summary(self):
        """Affiche un résumé de la stratégie recommandée"""
        if not self.recommendations:
            logger.warning("Aucune recommandation disponible")
            return
        
        rec = self.recommendations
        
        print("\n" + "="*60)
        print("💾 STRATÉGIE DE SAUVEGARDE RECOMMANDÉE")
        print("="*60)
        
        print(f"\n📌 Stratégie : {rec.get('strategie_recommandee', 'N/A')}")
        print(f"   Type : {rec.get('type_backup', 'N/A')}")
        
        print(f"\n⏰ Fréquences :")
        frequence = rec.get('frequence', {})
        for backup_type, freq in frequence.items():
            print(f"   • {backup_type.title()} : {freq}")
        
        print(f"\n📦 Rétention : {rec.get('retention', 'N/A')}")
        print(f"💾 Stockage : {rec.get('stockage', 'N/A')}")
        print(f"💰 Coût estimé : {rec.get('cout_estime', 'N/A')}")
        
        print(f"\n📝 Justification :")
        print(f"   {rec.get('justification', 'N/A')}")
        
        # Planning cron
        if 'cron_schedule' in rec and rec['cron_schedule']:
            print(f"\n🕐 Planning (crontab) :")
            for job in rec['cron_schedule']:
                print(f"   {job['cron']} - {job['description']}")
        
        print("\n" + "="*60)
    
    def interactive_wizard(self) -> Dict:
        """Assistant interactif pour recueillir les besoins"""
        print("\n" + "="*60)
        print("🧙 ASSISTANT DE CONFIGURATION DE SAUVEGARDE")
        print("="*60)
        
        print("\nRépondez aux questions suivantes :\n")
        
        # Question 1 : RPO
        print("1️⃣  Quel est votre RPO (Recovery Point Objective) ?")
        print("   a) 15 minutes (très critique)")
        print("   b) 1 heure (critique)")
        print("   c) 4 heures (important)")
        print("   d) 1 jour (standard)")
        rpo_choice = input("   Votre choix (a/b/c/d) : ").strip().lower()
        rpo_map = {'a': '15 minutes', 'b': '1 heure', 'c': '4 heures', 'd': '1 jour'}
        rpo = rpo_map.get(rpo_choice, '4 heures')
        
        # Question 2 : RTO
        print("\n2️⃣  Quel est votre RTO (Recovery Time Objective) ?")
        print("   a) 1 heure")
        print("   b) 4 heures")
        print("   c) 8 heures")
        print("   d) 1 jour")
        rto_choice = input("   Votre choix (a/b/c/d) : ").strip().lower()
        rto_map = {'a': '1 heure', 'b': '4 heures', 'c': '8 heures', 'd': '1 jour'}
        rto = rto_map.get(rto_choice, '4 heures')
        
        # Question 3 : Taille DB
        print("\n3️⃣  Quelle est la taille de votre base de données ?")
        db_size = input("   (ex: 100GB, 500GB, 2TB) : ").strip() or "100GB"
        
        # Question 4 : Criticité
        print("\n4️⃣  Quelle est la criticité de votre base ?")
        print("   a) Critique (production 24/7)")
        print("   b) Haute (production heures ouvrables)")
        print("   c) Moyenne (pré-production)")
        print("   d) Faible (développement/test)")
        crit_choice = input("   Votre choix (a/b/c/d) : ").strip().lower()
        crit_map = {'a': 'critique', 'b': 'haute', 'c': 'moyenne', 'd': 'faible'}
        criticality = crit_map.get(crit_choice, 'moyenne')
        
        # Question 5 : Budget
        print("\n5️⃣  Quel est votre budget pour les sauvegardes ?")
        print("   a) Illimité")
        print("   b) Élevé")
        print("   c) Moyen")
        print("   d) Limité")
        budget_choice = input("   Votre choix (a/b/c/d) : ").strip().lower()
        budget_map = {'a': 'illimité', 'b': 'élevé', 'c': 'moyen', 'd': 'limité'}
        budget = budget_map.get(budget_choice, 'moyen')
        
        print("\n⏳ Génération de la stratégie optimale...\n")
        
        # Générer la recommandation
        return self.recommend_strategy(
            rpo=rpo,
            rto=rto,
            db_size=db_size,
            criticality=criticality,
            budget=budget
        )


def main():
    """Fonction principale"""
    logger.info("="*60)
    logger.info("MODULE 7 : PLANS DE SAUVEGARDE INTELLIGENTS")
    logger.info("="*60)
    
    # Initialiser le recommandateur
    recommender = BackupRecommender()
    
    # Mode interactif ou automatique
    print("\n🎯 Mode de fonctionnement :")
    print("   1) Mode interactif (assistant)")
    print("   2) Mode automatique (exemple pré-défini)")
    mode = input("Votre choix (1/2) : ").strip()
    
    if mode == '1':
        # Mode interactif
        recommendation = recommender.interactive_wizard()
    else:
        # Mode automatique avec exemple
        logger.info("\n📋 Utilisation d'un exemple de configuration...\n")
        recommendation = recommender.recommend_strategy(
            rpo="1 heure",
            rto="4 heures",
            db_size="500GB",
            criticality="haute",
            budget="moyen",
            transaction_volume="élevé"
        )
    
    # Afficher le résumé
    recommender.print_summary()
    
    # Sauvegarder
    recommender.save_strategy()
    
    logger.info("\n✅ MODULE 7 TERMINÉ")
    logger.info("📂 Stratégie disponible dans data/oracle_exports/backup_strategies/")


if __name__ == "__main__":
    main()