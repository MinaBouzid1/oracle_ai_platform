"""
Module 6 : Anomaly Detector
Détection intelligente d'anomalies et menaces cybersécurité
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Tuple
from loguru import logger
import sys
import os

from llm_engine import LLMEngine
from rag_setup import OracleRAGSystem

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


class AnomalyDetector:
    """Détecteur d'anomalies dans les logs d'audit Oracle"""
    
    def __init__(self):
        self.llm = LLMEngine()
        self.rag = OracleRAGSystem()
        self.detection_results = []
        self.statistics = {
            'total_analyzed': 0,
            'normal': 0,
            'suspect': 0,
            'critique': 0
        }
        
        logger.info("🛡️ Initialisation du Anomaly Detector")
    
    def analyze_logs(
        self, 
        logs_file: str,
        batch_size: int = 10
    ) -> List[Dict]:
        """
        Analyse un ensemble de logs d'audit
        
        Args:
            logs_file: Chemin vers le fichier CSV/JSON des logs
            batch_size: Nombre de logs à analyser en parallèle
        
        Returns:
            Liste des résultats de détection
        """
        logger.info("="*60)
        logger.info("🔍 DÉTECTION D'ANOMALIES")
        logger.info("="*60)
        
        # Charger les logs
        df = self._load_logs(logs_file)
        if df is None:
            return []
        
        logger.info(f"📊 {len(df)} logs à analyser")
        
        # Analyser chaque log
        results = []
        for idx, (_, log) in enumerate(df.iterrows(), 1):
            if idx % 10 == 0:
                logger.info(f"   Progression: {idx}/{len(df)}")
            
            result = self._analyze_single_log(log, idx)
            results.append(result)
            
            # Mettre à jour les statistiques
            self._update_statistics(result)
        
        self.detection_results = results
        
        # Sauvegarder les résultats
        self._save_results(results, logs_file)
        
        return results
    
    def _load_logs(self, logs_file: str) -> pd.DataFrame:
        """Charge les logs depuis CSV ou JSON"""
        try:
            if logs_file.endswith('.csv'):
                df = pd.read_csv(logs_file)
            elif logs_file.endswith('.json'):
                df = pd.read_json(logs_file)
            else:
                logger.error(f"❌ Format de fichier non supporté : {logs_file}")
                return None
            
            logger.success(f"✅ Logs chargés : {logs_file}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement logs : {e}")
            return None
    
    def _analyze_single_log(self, log: pd.Series, log_number: int) -> Dict:
        """Analyse un log individuel"""
        
        # Préparer l'entrée de log
        log_entry = {
            'TIMESTAMP': str(log.get('TIMESTAMP', '')),
            'USERNAME': str(log.get('USERNAME', '')),
            'ACTION': str(log.get('ACTION', '')),
            'OBJECT_NAME': str(log.get('OBJECT_NAME', '')),
            'RETURNCODE': int(log.get('RETURNCODE', 0)),
            'CLIENT_ID': str(log.get('CLIENT_ID', '')),
            'OS_USERNAME': str(log.get('OS_USERNAME', '')),
            'TERMINAL': str(log.get('TERMINAL', ''))
        }
        
        # Récupérer le context RAG pertinent
        search_query = f"anomalie {log_entry['ACTION']} {log_entry['OBJECT_NAME'][:30]} cybersécurité intrusion"
        context_docs = self.rag.retrieve_context(search_query, top_k=3)
        rag_context = "\n\n".join([doc['document'] for doc in context_docs])
        
        # Contexte historique simulé (dans une vraie app, ce serait l'historique réel)
        historical_context = self._get_historical_context(log_entry)
        
        # Analyse par l'IA
        try:
            detection = self.llm.detect_anomaly(
                log_entry=log_entry,
                historical_context=historical_context,
                rag_context=rag_context
            )
            
            # Ajouter les métadonnées
            detection['log_number'] = log_number
            detection['log_entry'] = log_entry
            
            # Ajouter la vraie classification si disponible (pour validation)
            if 'LABEL' in log:
                detection['true_label'] = log['LABEL']
                detection['true_anomaly_type'] = log.get('ANOMALY_TYPE', None)
            
            return detection
            
        except Exception as e:
            logger.error(f"   ❌ Erreur log #{log_number}: {e}")
            return {
                'log_number': log_number,
                'error': str(e),
                'classification': 'error',
                'log_entry': log_entry
            }
    
    def _get_historical_context(self, log_entry: Dict) -> str:
        """Génère un contexte historique simulé pour le log"""
        username = log_entry['USERNAME']
        action = log_entry['ACTION']
        
        context_parts = [
            f"Utilisateur {username} :",
            f"- Première connexion enregistrée : 2023-06-15",
            f"- Nombre moyen d'actions par jour : 25",
            f"- Actions typiques : SELECT, INSERT, UPDATE"
        ]
        
        # Détails spécifiques selon l'action
        if action in ['DROP', 'CREATE USER', 'GRANT', 'ALTER SYSTEM']:
            context_parts.append(f"- ⚠️  Action {action} inhabituelle pour cet utilisateur")
        
        if 'OR' in log_entry['OBJECT_NAME'] or '1=1' in log_entry['OBJECT_NAME']:
            context_parts.append("- ⚠️  Pattern SQL suspect dans l'objet cible")
        
        return "\n".join(context_parts)
    
    def _update_statistics(self, result: Dict):
        """Met à jour les statistiques de détection"""
        self.statistics['total_analyzed'] += 1
        
        classification = result.get('classification', 'error')
        if classification == 'normal':
            self.statistics['normal'] += 1
        elif classification == 'suspect':
            self.statistics['suspect'] += 1
        elif classification == 'critique':
            self.statistics['critique'] += 1
    
    def _save_results(self, results: List[Dict], input_file: str):
        """Sauvegarde les résultats de détection"""
        # Créer le répertoire de sortie
        output_dir = os.path.dirname(input_file)
        reports_dir = f"{output_dir}/reports" if output_dir else "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{reports_dir}/anomaly_detection_{timestamp}.json"
        
        # Préparer le rapport complet
        report = {
            'timestamp': datetime.now().isoformat(),
            'input_file': input_file,
            'statistics': self.statistics,
            'detections': results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.success(f"💾 Rapport sauvegardé : {filename}")
    
    def print_summary(self):
        """Affiche un résumé des détections"""
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DE LA DÉTECTION D'ANOMALIES")
        print("="*60)
        
        stats = self.statistics
        total = stats['total_analyzed']
        
        if total == 0:
            print("Aucune analyse disponible")
            return
        
        print(f"\n✅ {total} logs analysés")
        print(f"\n📈 Résultats :")
        print(f"   🟢 Normal    : {stats['normal']} ({stats['normal']/total*100:.1f}%)")
        print(f"   🟡 Suspect   : {stats['suspect']} ({stats['suspect']/total*100:.1f}%)")
        print(f"   🔴 Critique  : {stats['critique']} ({stats['critique']/total*100:.1f}%)")
        
        # Top anomalies critiques
        critical_detections = [
            d for d in self.detection_results 
            if d.get('classification') == 'critique'
        ]
        
        if critical_detections:
            print(f"\n🚨 ANOMALIES CRITIQUES DÉTECTÉES : {len(critical_detections)}\n")
            
            for i, detection in enumerate(critical_detections[:5], 1):
                log_entry = detection.get('log_entry', {})
                print(f"{i}. {detection.get('type_anomalie', 'Inconnu')}")
                print(f"   User: {log_entry.get('USERNAME', 'N/A')}")
                print(f"   Action: {log_entry.get('ACTION', 'N/A')}")
                print(f"   Object: {log_entry.get('OBJECT_NAME', 'N/A')[:50]}")
                print(f"   Time: {log_entry.get('TIMESTAMP', 'N/A')}")
                print(f"   Confiance: {detection.get('confiance', 0)}%")
                print(f"   Justification: {detection.get('justification', 'N/A')[:100]}...")
                print()
        
        print("="*60)
    
    def validate_accuracy(self) -> Dict:
        """
        Valide la précision du détecteur (si les vraies labels sont disponibles)
        
        Returns:
            Métriques de performance
        """
        predictions = []
        true_labels = []
        
        for result in self.detection_results:
            if 'true_label' in result and result.get('classification') != 'error':
                # Mapper la classification IA vers normal/suspicious
                predicted = 'normal' if result['classification'] == 'normal' else 'suspicious'
                predictions.append(predicted)
                true_labels.append(result['true_label'])
        
        if not predictions:
            logger.warning("⚠️  Pas de labels pour validation")
            return {}
        
        # Calculer les métriques
        correct = sum(1 for p, t in zip(predictions, true_labels) if p == t)
        total = len(predictions)
        accuracy = correct / total
        
        # Précision et rappel pour "suspicious"
        true_positives = sum(1 for p, t in zip(predictions, true_labels) 
                            if p == 'suspicious' and t == 'suspicious')
        false_positives = sum(1 for p, t in zip(predictions, true_labels) 
                             if p == 'suspicious' and t == 'normal')
        false_negatives = sum(1 for p, t in zip(predictions, true_labels) 
                             if p == 'normal' and t == 'suspicious')
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'total_samples': total,
            'correct_predictions': correct
        }
        
        logger.info("\n📊 MÉTRIQUES DE PERFORMANCE")
        logger.info(f"   Accuracy  : {accuracy*100:.1f}%")
        logger.info(f"   Precision : {precision*100:.1f}%")
        logger.info(f"   Recall    : {recall*100:.1f}%")
        logger.info(f"   F1-Score  : {f1_score*100:.1f}%")
        
        return metrics
    
    def export_alerts_csv(self, output_file: str, severity_threshold: int = 5):
        """
        Exporte les alertes dans un CSV
        
        Args:
            output_file: Fichier de sortie
            severity_threshold: Seuil de sévérité minimum (1-10)
        """
        alerts = []
        
        for result in self.detection_results:
            if result.get('classification') in ['suspect', 'critique']:
                severity = result.get('severite', 0)
                
                if severity >= severity_threshold:
                    log_entry = result.get('log_entry', {})
                    alerts.append({
                        'TIMESTAMP': log_entry.get('TIMESTAMP', ''),
                        'USERNAME': log_entry.get('USERNAME', ''),
                        'ACTION': log_entry.get('ACTION', ''),
                        'OBJECT_NAME': log_entry.get('OBJECT_NAME', ''),
                        'CLASSIFICATION': result.get('classification', ''),
                        'ANOMALY_TYPE': result.get('type_anomalie', ''),
                        'SEVERITY': severity,
                        'CONFIDENCE': result.get('confiance', 0),
                        'JUSTIFICATION': result.get('justification', '')
                    })
        
        df = pd.DataFrame(alerts)
        df.to_csv(output_file, index=False)
        logger.success(f"🚨 {len(alerts)} alertes exportées : {output_file}")
        
        return df


def main():
    """Fonction principale"""
    logger.info("="*60)
    logger.info("MODULE 6 : DÉTECTION D'ANOMALIES & CYBERSÉCURITÉ")
    logger.info("="*60)
    
    # Initialiser le détecteur
    detector = AnomalyDetector()
    
    # Analyser les logs synthétiques
    logs_file = 'data/synthetic_data/audit_logs_synthetic.csv'
    
    if not os.path.exists(logs_file):
        logger.error(f"❌ Fichier {logs_file} non trouvé")
        logger.info("💡 Exécutez d'abord : python synthetic_logs_generator.py")
        return
    
    results = detector.analyze_logs(logs_file)
    
    # Afficher le résumé
    detector.print_summary()
    
    # Valider la précision
    metrics = detector.validate_accuracy()
    
    # Exporter les alertes critiques
    detector.export_alerts_csv(
        'data/synthetic_data/critical_alerts.csv',
        severity_threshold=7
    )
    
    logger.info("\n✅ MODULE 6 TERMINÉ")
    logger.info("📂 Résultats disponibles dans data/synthetic_data/reports/")


if __name__ == "__main__":
    main()