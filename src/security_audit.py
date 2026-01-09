"""
Module 4 : Security Audit
Audit automatisé de la sécurité Oracle avec IA
"""

import os
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List
from loguru import logger
import sys

# Import des modules précédents
from llm_engine import LLMEngine
from rag_setup import OracleRAGSystem

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


class SecurityAuditor:
    """Auditeur de sécurité Oracle avec IA"""
    
    def __init__(self):
        self.llm = LLMEngine()
        self.rag = OracleRAGSystem()
        self.audit_results = {}
        
        logger.info("🔒 Initialisation du Security Auditor")
    
    def audit_full(self, data_dir='data/oracle_exports') -> Dict:
        """
        Audit complet de sécurité
        
        Returns:
            Rapport d'audit complet
        """
        logger.info("="*60)
        logger.info("🔍 AUDIT DE SÉCURITÉ ORACLE")
        logger.info("="*60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'audits': {},
            'score_global': 0,
            'niveau_risque_global': 'inconnu',
            'resume': {}
        }
        
        # 1. Audit des utilisateurs
        logger.info("\n📊 1/3 - Audit des comptes utilisateurs...")
        users_result = self._audit_users(data_dir)
        results['audits']['users'] = users_result
        
        # 2. Audit des privilèges
        logger.info("\n📊 2/3 - Audit des privilèges...")
        privs_result = self._audit_privileges(data_dir)
        results['audits']['privileges'] = privs_result
        
        # 3. Audit des profils (si disponible)
        logger.info("\n📊 3/3 - Audit des profils de mot de passe...")
        profiles_result = self._audit_profiles(data_dir)
        results['audits']['profiles'] = profiles_result
        
        # Calcul du score global
        scores = [
            r.get('score_securite', 0) 
            for r in [users_result, privs_result, profiles_result]
            if r and 'score_securite' in r
        ]
        
        if scores:
            results['score_global'] = sum(scores) / len(scores)
            results['niveau_risque_global'] = self._get_risk_level(results['score_global'])
        
        # Résumé
        results['resume'] = self._generate_summary(results)
        
        # Sauvegarder le rapport
        self._save_report(results, data_dir)
        
        self.audit_results = results
        return results
    
    def _audit_users(self, data_dir: str) -> Dict:
        """Audit des comptes utilisateurs"""
        users_file = f"{data_dir}/security_config_users.csv"
        
        if not os.path.exists(users_file):
            logger.warning(f"⚠️  Fichier {users_file} non trouvé")
            return {'error': 'Fichier users non trouvé'}
        
        # Charger les données
        users_df = pd.read_csv(users_file)
        logger.info(f"   📁 {len(users_df)} utilisateurs à auditer")
        
        # Récupérer le context RAG
        context_docs = self.rag.retrieve_context(
            "risques de sécurité comptes utilisateurs Oracle profils par défaut",
            top_k=3
        )
        context = "\n\n".join([doc['document'] for doc in context_docs])
        
        # Formatter les données pour le LLM
        users_summary = []
        for _, user in users_df.iterrows():
            users_summary.append({
                'USERNAME': user['USERNAME'],
                'ACCOUNT_STATUS': user['ACCOUNT_STATUS'],
                'PROFILE': user['PROFILE'],
                'CREATED': str(user['CREATED'])
            })
        
        # Analyse par l'IA
        logger.info("   🤖 Analyse IA en cours...")
        result = self.llm.assess_security(
            {'users': users_summary[:10]},  # Limiter à 10 pour éviter tokens
            'users',
            context=context
        )
        
        if 'error' not in result:
            logger.success(f"   ✅ Score : {result.get('score_securite', 'N/A')}/100")
            logger.info(f"   ⚠️  Risques détectés : {len(result.get('risques', []))}")
        
        return result
    
    def _audit_privileges(self, data_dir: str) -> Dict:
        """Audit des privilèges système"""
        privs_file = f"{data_dir}/security_config_privileges.csv"
        
        if not os.path.exists(privs_file):
            logger.warning(f"⚠️  Fichier {privs_file} non trouvé")
            return {'error': 'Fichier privileges non trouvé'}
        
        privs_df = pd.read_csv(privs_file)
        logger.info(f"   📁 {len(privs_df)} privilèges à auditer")
        
        # Context RAG
        context_docs = self.rag.retrieve_context(
            "privilèges dangereux Oracle DROP ANY ALTER SYSTEM moindre privilège",
            top_k=3
        )
        context = "\n\n".join([doc['document'] for doc in context_docs])
        
        # Formatter
        privs_summary = privs_df.to_dict('records')[:20]  # Limiter à 20
        
        # Analyse IA
        logger.info("   🤖 Analyse IA en cours...")
        result = self.llm.assess_security(
            {'privileges': privs_summary},
            'privileges',
            context=context
        )
        
        if 'error' not in result:
            logger.success(f"   ✅ Score : {result.get('score_securite', 'N/A')}/100")
        
        return result
    
    def _audit_profiles(self, data_dir: str) -> Dict:
        """Audit des profils de mot de passe"""
        # Pour la version simulée, créer un profil par défaut
        mock_profile = {
            'PROFILE': 'DEFAULT',
            'RESOURCE_NAME': [
                'PASSWORD_LIFE_TIME',
                'FAILED_LOGIN_ATTEMPTS',
                'PASSWORD_LOCK_TIME',
                'PASSWORD_REUSE_TIME'
            ],
            'LIMIT': ['UNLIMITED', 'UNLIMITED', 'UNLIMITED', 'UNLIMITED']
        }
        
        logger.info(f"   📁 Audit du profil DEFAULT")
        
        # Context RAG
        context_docs = self.rag.retrieve_context(
            "profil mot de passe Oracle PASSWORD_LIFE_TIME FAILED_LOGIN_ATTEMPTS sécurité",
            top_k=2
        )
        context = "\n\n".join([doc['document'] for doc in context_docs])
        
        # Formatter pour le LLM
        profile_str = "Profil : DEFAULT\n"
        for resource, limit in zip(mock_profile['RESOURCE_NAME'], mock_profile['LIMIT']):
            profile_str += f"  {resource} : {limit}\n"
        
        # Analyse IA
        logger.info("   🤖 Analyse IA en cours...")
        result = self.llm.assess_security(
            profile_str,
            'profiles',
            context=context
        )
        
        if 'error' not in result:
            logger.success(f"   ✅ Score : {result.get('score_securite', 'N/A')}/100")
        
        return result
    
    def _get_risk_level(self, score: float) -> str:
        """Détermine le niveau de risque selon le score"""
        if score >= 80:
            return "faible"
        elif score >= 60:
            return "moyen"
        elif score >= 40:
            return "haut"
        else:
            return "critique"
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Génère un résumé de l'audit"""
        all_risks = []
        
        for audit_type, audit_result in results['audits'].items():
            if isinstance(audit_result, dict) and 'risques' in audit_result:
                for risk in audit_result['risques']:
                    risk['source'] = audit_type
                    all_risks.append(risk)
        
        # Trier par sévérité
        severity_order = {'critique': 0, 'haute': 1, 'moyenne': 2, 'faible': 3}
        all_risks.sort(key=lambda x: severity_order.get(x.get('severite', 'faible'), 4))
        
        return {
            'total_risques': len(all_risks),
            'risques_critiques': len([r for r in all_risks if r.get('severite') == 'critique']),
            'risques_hauts': len([r for r in all_risks if r.get('severite') == 'haute']),
            'risques_moyens': len([r for r in all_risks if r.get('severite') == 'moyenne']),
            'top_3_risques': all_risks[:3]
        }
    
    def _save_report(self, results: Dict, output_dir: str):
        """Sauvegarde le rapport d'audit"""
        os.makedirs(f"{output_dir}/reports", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/reports/security_audit_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.success(f"💾 Rapport sauvegardé : {filename}")
    
    def print_summary(self):
        """Affiche un résumé visuel de l'audit"""
        if not self.audit_results:
            logger.warning("Aucun audit disponible")
            return
        
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DE L'AUDIT DE SÉCURITÉ")
        print("="*60)
        
        score = self.audit_results.get('score_global', 0)
        niveau = self.audit_results.get('niveau_risque_global', 'inconnu')
        
        # Barre de score colorée
        bar_length = 50
        filled = int((score / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\n🎯 Score global de sécurité : {score:.1f}/100")
        print(f"   [{bar}]")
        print(f"   Niveau de risque : {niveau.upper()}")
        
        resume = self.audit_results.get('resume', {})
        print(f"\n📈 Statistiques :")
        print(f"   • Total risques détectés : {resume.get('total_risques', 0)}")
        print(f"   • Risques CRITIQUES : {resume.get('risques_critiques', 0)}")
        print(f"   • Risques HAUTS : {resume.get('risques_hauts', 0)}")
        print(f"   • Risques MOYENS : {resume.get('risques_moyens', 0)}")
        
        # Top 3 risques
        top_risks = resume.get('top_3_risques', [])
        if top_risks:
            print(f"\n⚠️  TOP 3 des risques :")
            for i, risk in enumerate(top_risks, 1):
                severity_emoji = {
                    'critique': '🔴',
                    'haute': '🟠',
                    'moyenne': '🟡',
                    'faible': '🟢'
                }
                emoji = severity_emoji.get(risk.get('severite', 'faible'), '⚪')
                
                print(f"\n   {i}. {emoji} {risk.get('titre', 'N/A')}")
                print(f"      Sévérité : {risk.get('severite', 'N/A')}")
                print(f"      Source : {risk.get('source', 'N/A')}")
                print(f"      Recommandation : {risk.get('recommandation', 'N/A')[:100]}...")
        
        print("\n" + "="*60)


def main():
    """Fonction principale"""
    logger.info("="*60)
    logger.info("MODULE 4 : AUDIT DE SÉCURITÉ AUTOMATISÉ")
    logger.info("="*60)
    
    # Créer l'auditeur
    auditor = SecurityAuditor()
    
    # Lancer l'audit complet
    results = auditor.audit_full('data/oracle_exports')
    
    # Afficher le résumé
    auditor.print_summary()
    
    logger.info("\n✅ MODULE 4 TERMINÉ")
    logger.info("📂 Rapport complet disponible dans data/oracle_exports/reports/")


if __name__ == "__main__":
    main()