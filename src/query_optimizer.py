"""
Module 5 : Query Optimizer
Analyse et optimisation intelligente des requêtes Oracle
Compatible avec Oracle réel via Docker
"""

import os
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Tuple
from loguru import logger
import sys
from pathlib import Path

from llm_engine import LLMEngine
from rag_setup import OracleRAGSystem
from oracle_connector import OracleConnector

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


class QueryOptimizer:
    """Analyseur et optimiseur de requêtes SQL avec IA"""
    
    def __init__(self):
        """
        Args:
            llm_engine: Moteur LLM pour l'analyse
            rag_system: Système RAG pour le contexte
        """
        self.llm = LLMEngine()
        self.rag = OracleRAGSystem()
        self.output_dir = Path("data/oracle_exports/query_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Connecteur Oracle
        self.oracle = OracleConnector()
    
    def load_awr_data(self, data_dir='data/oracle_exports'):
        """
        Charge les données AWR depuis les fichiers exportés
        
        Args:
            data_dir: Répertoire des données exportées
            
        Returns:
            DataFrame avec les données AWR
        """
        try:
            # Chercher le fichier AWR
            awr_file = os.path.join(data_dir, 'awr_data.csv')
            
            if not os.path.exists(awr_file):
                # Chercher d'autres noms possibles
                for file in os.listdir(data_dir):
                    if 'awr' in file.lower() and file.endswith('.csv'):
                        awr_file = os.path.join(data_dir, file)
                        break
            
            if not os.path.exists(awr_file):
                logger.warning(f"❌ Aucun fichier AWR trouvé dans {data_dir}")
                return pd.DataFrame()
            
            # Charger les données
            awr_data = pd.read_csv(awr_file)
            logger.info(f"✅ Données AWR chargées : {len(awr_data)} lignes")
            
            # Vérifier les colonnes nécessaires
            required_columns = ['ELAPSED_TIME', 'SNAP_TIME']
            missing_columns = [col for col in required_columns if col not in awr_data.columns]
            
            if missing_columns:
                logger.warning(f"⚠️ Colonnes manquantes dans les données AWR: {missing_columns}")
                
                # Chercher des colonnes similaires
                for col in missing_columns:
                    similar_cols = [c for c in awr_data.columns if col.lower() in c.lower()]
                    if similar_cols:
                        logger.info(f"   Colonne similaire pour {col}: {similar_cols[0]}")
                        awr_data[col] = awr_data[similar_cols[0]]
            
            return awr_data
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement des données AWR: {e}")
            return pd.DataFrame()
    
    def get_performance_metrics(self, data_dir='data/oracle_exports', timeframe_days=7):
        """
        Récupère les métriques globales de performance
        
        Args:
            data_dir: Répertoire des données exportées
            timeframe_days: Période d'analyse en jours
            
        Returns:
            Dictionnaire avec les métriques de performance
        """
        try:
            # Charger les données AWR
            awr_data = self.load_awr_data(data_dir)
            
            if awr_data.empty:
                return {"error": "Aucune donnée AWR disponible"}
            
            # Calculer les métriques
            total_queries = len(awr_data)
            total_execution_time = awr_data['ELAPSED_TIME'].sum() / 1000000  # Convertir en secondes
            
            avg_query_time = awr_data['ELAPSED_TIME'].mean() / 1000  # Convertir en ms
            slow_queries = len(awr_data[awr_data['ELAPSED_TIME'] > 500000])  # > 0.5s
            slow_queries_pct = (slow_queries / total_queries * 100) if total_queries > 0 else 0
            
            # Tendance temporelle (comparaison avec période précédente)
            if 'SNAP_TIME' in awr_data.columns:
                awr_data['SNAP_TIME'] = pd.to_datetime(awr_data['SNAP_TIME'])
                recent_cutoff = pd.Timestamp.now() - pd.Timedelta(days=timeframe_days)
                
                recent_data = awr_data[awr_data['SNAP_TIME'] >= recent_cutoff]
                older_data = awr_data[awr_data['SNAP_TIME'] < recent_cutoff]
                
                if len(recent_data) > 0 and len(older_data) > 0:
                    recent_avg = recent_data['ELAPSED_TIME'].mean()
                    older_avg = older_data['ELAPSED_TIME'].mean()
                    time_trend = "↗️" if recent_avg > older_avg else "↘️" if recent_avg < older_avg else "→"
                    avg_time_trend = "↗️" if recent_avg > older_avg else "↘️" if recent_avg < older_avg else "→"
                else:
                    time_trend = "→"
                    avg_time_trend = "→"
            else:
                time_trend = "→"
                avg_time_trend = "→"
            
            # Distribution des temps d'exécution pour le graphique
            query_times_ms = (awr_data['ELAPSED_TIME'] / 1000).head(1000).tolist()
            
            # Top 10 requêtes les plus lentes
            top_10 = awr_data.nlargest(10, 'ELAPSED_TIME')
            top_10_list = []
            
            for idx, row in top_10.iterrows():
                sql_text = row.get('SQL_TEXT', '')[:100] + "..." if len(str(row.get('SQL_TEXT', ''))) > 100 else str(row.get('SQL_TEXT', ''))
                top_10_list.append({
                    'sql_id': row.get('SQL_ID', f'query_{idx}'),
                    'sql_text': sql_text,
                    'elapsed_time_ms': float(row['ELAPSED_TIME'] / 1000)
                })
            
            return {
                'total_execution_time_seconds': round(total_execution_time, 2),
                'total_queries': total_queries,
                'avg_query_time_ms': round(avg_query_time, 2),
                'slow_queries_count': slow_queries,
                'slow_queries_percentage': round(slow_queries_pct, 2),
                'time_trend': time_trend,
                'avg_time_trend': avg_time_trend,
                'query_times_distribution': query_times_ms,
                'top_10_queries': top_10_list
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul des métriques: {e}")
            return {"error": f"Erreur lors du calcul des métriques: {str(e)}"}
    
    def analyze_query(self, sql_query: str, sql_id: str = None) -> Dict:
        """
        Analyse complète d'une requête SQL
        
        Args:
            sql_query: Requête SQL à analyser
            sql_id: ID SQL Oracle (optionnel)
            
        Returns:
            Dictionnaire avec analyse complète
        """
        logger.info(f"🔍 Analyse de la requête : {sql_query[:100]}...")
        
        # 1. Récupérer le contexte RAG
        context_docs = self.rag.retrieve_context(
            f"Comment optimiser cette requête : {sql_query}",
            top_k=3
        )
        
        # Extraire le texte des documents de contexte
        rag_context = "\n\n".join([doc['document'] for doc in context_docs])
        
        # 2. Récupérer le plan d'exécution si SQL_ID fourni
        execution_plan = ""
        if sql_id and self.oracle.connection:
            plan_df = self.oracle.get_execution_plan(sql_id)
            if not plan_df.empty:
                execution_plan = "\n".join([
                    f"  {row['OPERATION']} (Cost: {row['COST']})"
                    for _, row in plan_df.iterrows()
                ])
        
        # 3. Analyser avec le LLM - CORRECTION ICI
        analysis = self.llm.analyze_query(
            sql_text=sql_query,  # Changé de sql_query à sql_text
            plan=execution_plan if execution_plan else "Plan non disponible",  # Changé de execution_plan à plan
            metrics={},  # Ajouté metrics vide
            context=rag_context
        )
        
        return analysis
    
    def analyze_slow_queries(self, min_elapsed_sec: float = 1.0, limit: int = 20) -> List[Dict]:
        """
        Analyse toutes les requêtes lentes de la base
        
        Args:
            min_elapsed_sec: Temps minimum (secondes)
            limit: Nombre max de requêtes à analyser
            
        Returns:
            Liste des analyses
        """
        logger.info(f"🔍 Récupération des requêtes lentes (> {min_elapsed_sec}s)...")
        
        # Récupérer les requêtes lentes depuis Oracle
        slow_queries = self.oracle.get_slow_queries(min_elapsed_sec, limit)
        
        if slow_queries.empty:
            logger.warning("⚠️ Aucune requête lente trouvée")
            return []
        
        logger.info(f"📊 {len(slow_queries)} requêtes lentes trouvées")
        
        results = []
        
        for idx, row in slow_queries.iterrows():
            sql_id = row['SQL_ID']
            sql_text = row['SQL_TEXT']
            elapsed = row['TOTAL_ELAPSED_SEC']
            executions = row['EXECUTIONS']
            
            logger.info(f"\n{'='*80}")
            logger.info(f"🔍 Analyse {idx+1}/{len(slow_queries)}: SQL_ID={sql_id}")
            logger.info(f"   Temps total: {elapsed:.2f}s | Exécutions: {executions}")
            logger.info(f"   Requête: {sql_text[:100]}...")
            
            # Analyser la requête
            analysis = self.analyze_query(sql_text, sql_id)
            
            # Ajouter les métriques
            analysis['metrics'] = {
                'sql_id': sql_id,
                'total_elapsed_sec': float(elapsed),
                'executions': int(executions),
                'avg_elapsed_sec': float(row.get('AVG_ELAPSED_SEC', 0)),
                'buffer_gets': int(row.get('BUFFER_GETS', 0)),
                'disk_reads': int(row.get('DISK_READS', 0))
            }
            
            results.append(analysis)
            
            # Afficher le résumé
            logger.info(f"\n📋 RÉSUMÉ DE L'ANALYSE:")
            logger.info(f"   Explication: {analysis.get('explanation', 'N/A')[:200]}...")
            logger.info(f"   Points coûteux: {len(analysis.get('bottlenecks', []))} identifiés")
            logger.info(f"   Recommandations: {len(analysis.get('recommendations', []))}")
        
        return results
    
    def generate_report(self, analyses: List[Dict]) -> str:
        """
        Génère un rapport d'optimisation complet
        
        Args:
            analyses: Liste des analyses de requêtes
            
        Returns:
            Chemin du rapport JSON
        """
        if not analyses:
            logger.warning("⚠️ Aucune analyse à sauvegarder")
            return None
        
        # Créer le rapport
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_queries_analyzed': len(analyses),
            'queries': analyses,
            'summary': {
                'total_bottlenecks': sum(len(a.get('bottlenecks', [])) for a in analyses),
                'total_recommendations': sum(len(a.get('recommendations', [])) for a in analyses),
                'avg_elapsed_time': sum(a.get('metrics', {}).get('total_elapsed_sec', 0) for a in analyses) / len(analyses)
            }
        }
        
        # Sauvegarder JSON
        report_path = self.output_dir / f"query_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.success(f"✅ Rapport JSON sauvegardé : {report_path}")
        
        # Créer aussi un CSV avec les recommandations
        recommendations_data = []
        for analysis in analyses:
            sql_id = analysis.get('metrics', {}).get('sql_id', 'N/A')
            for rec in analysis.get('recommendations', []):
                recommendations_data.append({
                    'SQL_ID': sql_id,
                    'Temps_Total_Sec': analysis.get('metrics', {}).get('total_elapsed_sec', 0),
                    'Recommandation': rec
                })
        
        if recommendations_data:
            rec_df = pd.DataFrame(recommendations_data)
            rec_path = self.output_dir / f"recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            rec_df.to_csv(rec_path, index=False, encoding='utf-8')
            logger.success(f"✅ Recommandations CSV : {rec_path}")
        
        return str(report_path)
    
    def interactive_mode(self):
        """Mode interactif pour analyser des requêtes"""
        logger.info("\n" + "="*80)
        logger.info("🎯 MODE INTERACTIF - ANALYSEUR DE REQUÊTES")
        logger.info("="*80)
        logger.info("Entrez une requête SQL à analyser (ou 'quit' pour quitter)")
        logger.info("Exemple : SELECT * FROM employees WHERE salary > 50000")
        logger.info("="*80 + "\n")
        
        while True:
            try:
                sql_query = input("\n💭 Requête SQL > ").strip()
                
                if sql_query.lower() in ['quit', 'exit', 'q']:
                    logger.info("👋 Au revoir !")
                    break
                
                if not sql_query:
                    continue
                
                # Analyser avec le LLM directement - CORRECTION ICI
                analysis = self.llm.analyze_query(
                    sql_text=sql_query,
                    plan="Plan non disponible",
                    metrics={},
                    context=""
                )
                
                # Afficher le résultat
                print("\n" + "="*80)
                print("📊 RÉSULTAT DE L'ANALYSE")
                print("="*80)
                
                print(f"\n📝 EXPLICATION:")
                print(f"{analysis.get('explanation', 'N/A')}")
                
                print(f"\n⚠️ POINTS COÛTEUX ({len(analysis.get('bottlenecks', []))}):")
                for i, bottleneck in enumerate(analysis.get('bottlenecks', []), 1):
                    print(f"  {i}. {bottleneck}")
                
                print(f"\n💡 RECOMMANDATIONS ({len(analysis.get('recommendations', []))}):")
                for i, rec in enumerate(analysis.get('recommendations', []), 1):
                    print(f"  {i}. {rec}")
                
                print("="*80)
                
            except KeyboardInterrupt:
                logger.info("\n👋 Au revoir !")
                break
            except Exception as e:
                logger.error(f"❌ Erreur : {e}")

    def analyze_slow_queries_from_file(self, data_dir='data/oracle_exports', top_n=5, threshold_elapsed=500000):
        """
        Analyse les requêtes lentes à partir des fichiers exportés
        
        Args:
            data_dir: Répertoire des données exportées
            top_n: Nombre de requêtes à analyser
            threshold_elapsed: Seuil de temps écoulé (microsecondes)
            
        Returns:
            Liste des analyses
        """
        logger.info(f"🔍 Analyse des requêtes lentes depuis les fichiers...")
        
        sql_stats_file = f"{data_dir}/sql_stats.csv"
        
        if not os.path.exists(sql_stats_file):
            logger.error(f"❌ Fichier {sql_stats_file} non trouvé")
            return []
        
        # Charger les statistiques SQL
        sql_stats = pd.read_csv(sql_stats_file)
        
        # DEBUG: Afficher les colonnes disponibles
        logger.info(f"📊 Colonnes disponibles dans sql_stats.csv: {list(sql_stats.columns)}")
        logger.info(f"📊 Nombre de lignes: {len(sql_stats)}")
        
        # Identifier quelle colonne contient le temps d'exécution
        time_columns = ['ELAPSED_TIME', 'ELAPSED_TIME_SEC', 'ELAPSED_TIME_MS', 'TIME', 'TOTAL_ELAPSED_SEC', 'ELAPSED_TIME_MICRO']
        found_column = None
        
        for col in time_columns:
            if col in sql_stats.columns:
                found_column = col
                logger.info(f"✅ Colonne de temps trouvée: {col}")
                break
        
        if not found_column:
            logger.warning("⚠️  Aucune colonne de temps standard trouvée")
            logger.info("Colonnes disponibles:")
            for col in sql_stats.columns:
                logger.info(f"  - {col}")
            return []
        
        # Convertir le seuil si nécessaire
        if found_column == 'ELAPSED_TIME_SEC' or found_column == 'TOTAL_ELAPSED_SEC':
            threshold = threshold_elapsed / 1000000  # Convertir en secondes
        elif found_column == 'ELAPSED_TIME_MS':
            threshold = threshold_elapsed / 1000  # Convertir en millisecondes
        else:
            threshold = threshold_elapsed  # Déjà en microsecondes
        
        # Filtrer les requêtes lentes
        slow_queries = sql_stats[sql_stats[found_column] > threshold]
        
        if len(slow_queries) == 0:
            logger.warning(f"⚠️ Aucune requête lente trouvée (seuil: {threshold})")
            return []
        
        # Prendre les top_n requêtes les plus lentes
        slow_queries = slow_queries.nlargest(top_n, found_column)
        
        logger.info(f"📊 {len(slow_queries)} requêtes lentes trouvées")
        
        results = []
        
        for idx, row in slow_queries.iterrows():
            sql_id = row.get('SQL_ID', f'unknown_{idx}')
            sql_text = row.get('SQL_TEXT', '')
            
            if pd.isna(sql_text) or sql_text == '':
                logger.warning(f"⚠️ SQL_TEXT vide pour SQL_ID: {sql_id}")
                continue
            
            elapsed = row.get(found_column, 0)
            executions = row.get('EXECUTIONS', 1)
            
            logger.info(f"\n{'='*80}")
            logger.info(f"🔍 Analyse {idx+1}/{len(slow_queries)}: SQL_ID={sql_id}")
            
            # Afficher le temps avec l'unité appropriée
            if found_column == 'ELAPSED_TIME_SEC' or found_column == 'TOTAL_ELAPSED_SEC':
                logger.info(f"   Temps total: {elapsed:.2f}s | Exécutions: {executions}")
            elif found_column == 'ELAPSED_TIME_MS':
                logger.info(f"   Temps total: {elapsed:.2f}ms | Exécutions: {executions}")
            else:
                logger.info(f"   Temps total: {elapsed/1000000:.2f}s | Exécutions: {executions}")
            
            logger.info(f"   Requête: {sql_text[:100]}...")
            
            # Récupérer le plan d'exécution si possible
            execution_plan = ""
            try:
                if self.oracle.connection:
                    plan_df = self.oracle.get_execution_plan(sql_id)
                    if not plan_df.empty:
                        execution_plan = "\n".join([
                            f"  {row['OPERATION']} (Cost: {row['COST']})"
                            for _, row in plan_df.iterrows()
                        ])
            except Exception as e:
                logger.warning(f"⚠️ Impossible de récupérer le plan d'exécution: {e}")
            
            # Récupérer le contexte RAG
            context_docs = self.rag.retrieve_context(
                f"optimisation requête Oracle {sql_text[:50]}",
                top_k=3
            )
            rag_context = "\n\n".join([doc['document'] for doc in context_docs])
            
            try:
                # Analyser avec le LLM - CORRECTION ICI
                analysis = self.llm.analyze_query(
                    sql_text=sql_text,  # Changé de sql_query à sql_text
                    plan=execution_plan if execution_plan else "Plan non disponible",  # Changé de execution_plan à plan
                    metrics=row.to_dict(),
                    context=rag_context
                )
                
                # Ajouter les métriques
                analysis['metrics'] = row.to_dict()
                analysis['sql_text'] = sql_text
                analysis['sql_id'] = sql_id
                
                results.append(analysis)
                
                # Afficher le résumé
                logger.info(f"\n📋 RÉSUMÉ DE L'ANALYSE:")
                if 'resume' in analysis:
                    logger.info(f"   Résumé: {analysis.get('resume', 'N/A')[:200]}...")
                elif 'explanation' in analysis:
                    logger.info(f"   Explication: {analysis.get('explanation', 'N/A')[:200]}...")
                
                optimisations = analysis.get('optimisations', [])
                if not optimisations:
                    optimisations = analysis.get('recommendations', [])
                
                logger.info(f"   Optimisations proposées: {len(optimisations)}")
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'analyse de la requête {sql_id}: {e}")
        
        return results


def main():
    """Fonction principale"""
    logger.info("="*60)
    logger.info("MODULE 5 : ANALYSE D'OPTIMISATION DE REQUÊTES")
    logger.info("="*60)
    
    # 1. Initialiser les composants
    logger.info("🚀 Initialisation du Query Optimizer")
    optimizer = QueryOptimizer()
    
    # 2. Se connecter à Oracle
    logger.info("🔌 Connexion à Oracle Database...")
    if not optimizer.oracle.connect():
        logger.error("❌ Impossible de se connecter à Oracle")
        logger.info("💡 Assurez-vous que le conteneur Docker Oracle est démarré")
        logger.info("💡 Commande : docker ps | grep oracle")
        return
    
    try:
        # 3. Analyser les requêtes lentes depuis les fichiers
        logger.info("\n" + "="*60)
        logger.info("🔍 ANALYSE DES REQUÊTES LENTES")
        logger.info("="*60)
        
        analyses = optimizer.analyze_slow_queries_from_file(
            data_dir='data/oracle_exports',
            top_n=5,
            threshold_elapsed=500000  # 0.5 seconde
        )
        
        if analyses:
            # 4. Générer le rapport
            logger.info("\n" + "="*60)
            logger.info("📄 GÉNÉRATION DU RAPPORT")
            logger.info("="*60)
            
            report_path = optimizer.generate_report(analyses)
            
            logger.success("\n" + "="*60)
            logger.success("✅ ANALYSE TERMINÉE")
            logger.success("="*60)
            logger.info(f"   Requêtes analysées : {len(analyses)}")
            logger.info(f"   Rapport : {report_path}")
        
        # 5. Mode interactif (optionnel)
        logger.info("\n" + "="*60)
        response = input("Voulez-vous analyser d'autres requêtes en mode interactif ? (o/n) > ").strip().lower()
        if response == 'o':
            optimizer.interactive_mode()
    
    finally:
        # 6. Déconnexion
        optimizer.oracle.disconnect()


if __name__ == "__main__":
    main()