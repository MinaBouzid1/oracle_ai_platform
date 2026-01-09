"""
Module 5 : Query Optimizer
Analyse et optimisation intelligente des requêtes Oracle
"""

import os
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Tuple
from loguru import logger
import sys

from llm_engine import LLMEngine
from rag_setup import OracleRAGSystem
from data_extractor import OracleDataExtractor

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


class QueryOptimizer:
    """Optimiseur de requêtes Oracle avec IA"""
    
    def __init__(self):
        self.llm = LLMEngine()
        self.rag = OracleRAGSystem()
        self.extractor = OracleDataExtractor(use_mock=True)
        self.optimization_results = []
        
        logger.info("🚀 Initialisation du Query Optimizer")
    
    def analyze_slow_queries(
        self, 
        data_dir='data/oracle_exports',
        top_n: int = 10,
        threshold_elapsed: int = 1000000  # microsec (1 seconde)
    ) -> List[Dict]:
        """
        Analyse les requêtes lentes et propose des optimisations
        
        Args:
            data_dir: Répertoire des données Oracle
            top_n: Nombre de requêtes à analyser
            threshold_elapsed: Seuil de temps (en microsec)
        
        Returns:
            Liste des analyses d'optimisation
        """
        logger.info("="*60)
        logger.info("⚡ ANALYSE D'OPTIMISATION DES REQUÊTES")
        logger.info("="*60)
        
        # Charger les stats SQL
        sql_stats_file = f"{data_dir}/sql_stats.csv"
        if not os.path.exists(sql_stats_file):
            logger.error(f"❌ Fichier {sql_stats_file} non trouvé")
            return []
        
        sql_df = pd.read_csv(sql_stats_file)
        logger.info(f"📊 {len(sql_df)} requêtes chargées")
        
        # Filtrer les requêtes lentes
        slow_queries = sql_df[
            sql_df['ELAPSED_TIME'] > threshold_elapsed
        ].sort_values('ELAPSED_TIME', ascending=False).head(top_n)
        
        logger.info(f"🐌 {len(slow_queries)} requêtes lentes détectées (> {threshold_elapsed/1000000:.1f}s)")
        
        if len(slow_queries) == 0:
            logger.warning("⚠️  Aucune requête lente à analyser")
            return []
        
        # Analyser chaque requête
        results = []
        for idx, (_, row) in enumerate(slow_queries.iterrows(), 1):
            logger.info(f"\n🔍 Analyse {idx}/{len(slow_queries)}: {row['SQL_ID']}")
            
            analysis = self._analyze_single_query(row)
            results.append(analysis)
            
            # Afficher un résumé rapide
            if 'error' not in analysis:
                logger.success(f"   ✅ {len(analysis.get('optimisations', []))} optimisations proposées")
        
        self.optimization_results = results
        
        # Sauvegarder les résultats
        self._save_results(results, data_dir)
        
        return results
    
    def _analyze_single_query(self, query_row: pd.Series) -> Dict:
        """Analyse une requête individuelle"""
        
        sql_id = query_row['SQL_ID']
        sql_text = query_row['SQL_TEXT']
        
        # Récupérer le plan d'exécution
        exec_plan = self.extractor.get_execution_plan(sql_id)
        plan_text = self._format_execution_plan(exec_plan)
        
        # Préparer les métriques
        metrics = {
            'EXECUTIONS': query_row['EXECUTIONS'],
            'ELAPSED_TIME': query_row['ELAPSED_TIME'],
            'CPU_TIME': query_row['CPU_TIME'],
            'BUFFER_GETS': query_row['BUFFER_GETS'],
            'DISK_READS': query_row['DISK_READS'],
            'ROWS_PROCESSED': query_row['ROWS_PROCESSED']
        }
        
        # Calculer des métriques dérivées
        if metrics['EXECUTIONS'] > 0:
            metrics['AVG_ELAPSED'] = metrics['ELAPSED_TIME'] / metrics['EXECUTIONS']
            metrics['AVG_BUFFER_GETS'] = metrics['BUFFER_GETS'] / metrics['EXECUTIONS']
        
        if metrics['ROWS_PROCESSED'] > 0:
            metrics['BUFFER_PER_ROW'] = metrics['BUFFER_GETS'] / metrics['ROWS_PROCESSED']
        
        # Récupérer le context RAG pertinent
        search_query = f"optimisation requête lente {self._extract_operations(exec_plan)} index scan join"
        context_docs = self.rag.retrieve_context(search_query, top_k=4)
        context = "\n\n".join([doc['document'] for doc in context_docs])
        
        logger.info(f"   📝 SQL : {sql_text[:60]}...")
        logger.info(f"   ⏱️  Temps moyen : {metrics.get('AVG_ELAPSED', 0)/1000:.1f}ms")
        logger.info(f"   💾 Buffer gets/row : {metrics.get('BUFFER_PER_ROW', 0):.1f}")
        
        # Analyse par l'IA
        logger.info(f"   🤖 Analyse IA en cours...")
        try:
            analysis = self.llm.analyze_query(
                sql_text=sql_text,
                plan=plan_text,
                metrics=metrics,
                context=context
            )
            
            # Ajouter les métadonnées
            analysis['sql_id'] = sql_id
            analysis['sql_text'] = sql_text
            analysis['metrics'] = metrics
            analysis['execution_plan'] = plan_text
            
            return analysis
            
        except Exception as e:
            logger.error(f"   ❌ Erreur analyse : {e}")
            return {
                'sql_id': sql_id,
                'error': str(e),
                'sql_text': sql_text
            }
    
    def _format_execution_plan(self, plan_df: pd.DataFrame) -> str:
        """Formate un plan d'exécution en texte lisible"""
        if plan_df.empty:
            return "Plan d'exécution non disponible"
        
        plan_text = "Plan d'exécution :\n"
        for _, row in plan_df.iterrows():
            operation = row['OPERATION']
            options = row.get('OPTIONS', '')
            object_name = row.get('OBJECT_NAME', '')
            cost = row.get('COST', '')
            
            line = f"  - {operation}"
            if options and options != 'None':
                line += f" ({options})"
            if object_name and object_name != 'None':
                line += f" on {object_name}"
            if cost and cost != 'None':
                line += f" [Cost: {cost}]"
            
            plan_text += line + "\n"
        
        return plan_text
    
    def _extract_operations(self, plan_df: pd.DataFrame) -> str:
        """Extrait les opérations principales du plan"""
        if plan_df.empty:
            return ""
        
        operations = plan_df['OPERATION'].unique()
        return ' '.join(operations[:3])  # Top 3 opérations
    
    def _save_results(self, results: List[Dict], output_dir: str):
        """Sauvegarde les résultats d'optimisation"""
        os.makedirs(f"{output_dir}/reports", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/reports/optimization_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.success(f"💾 Résultats sauvegardés : {filename}")
    
    def print_summary(self):
        """Affiche un résumé des optimisations"""
        if not self.optimization_results:
            logger.warning("Aucune analyse disponible")
            return
        
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DES OPTIMISATIONS")
        print("="*60)
        
        valid_results = [r for r in self.optimization_results if 'error' not in r]
        
        print(f"\n✅ {len(valid_results)}/{len(self.optimization_results)} requêtes analysées avec succès")
        
        # Statistiques globales
        total_optimizations = sum(
            len(r.get('optimisations', [])) 
            for r in valid_results
        )
        print(f"💡 {total_optimizations} optimisations totales proposées")
        
        # Top 3 requêtes les plus problématiques
        print(f"\n🔥 TOP 3 des requêtes à optimiser en priorité :\n")
        
        for i, result in enumerate(valid_results[:3], 1):
            print(f"{i}. SQL_ID: {result.get('sql_id', 'N/A')}")
            print(f"   SQL: {result.get('sql_text', 'N/A')[:70]}...")
            print(f"   Résumé: {result.get('resume', 'N/A')}")
            
            optimizations = result.get('optimisations', [])
            if optimizations:
                print(f"   Optimisations ({len(optimizations)}) :")
                for opt in optimizations[:2]:  # Top 2
                    priority_emoji = {
                        'haute': '🔴',
                        'moyenne': '🟡',
                        'faible': '🟢'
                    }
                    emoji = priority_emoji.get(opt.get('priorite', 'faible'), '⚪')
                    print(f"      {emoji} {opt.get('titre', 'N/A')}")
                    print(f"         Gain estimé: {opt.get('gain_estime', 'N/A')}")
            print()
        
        print("="*60)
    
    def get_optimization_by_sql_id(self, sql_id: str) -> Dict:
        """Récupère l'analyse d'optimisation pour un SQL_ID spécifique"""
        for result in self.optimization_results:
            if result.get('sql_id') == sql_id:
                return result
        return None
    
    def export_recommendations_csv(self, output_file: str):
        """Exporte les recommandations dans un CSV"""
        recommendations = []
        
        for result in self.optimization_results:
            if 'error' in result:
                continue
            
            sql_id = result.get('sql_id', '')
            sql_text = result.get('sql_text', '')[:100]
            
            for opt in result.get('optimisations', []):
                recommendations.append({
                    'SQL_ID': sql_id,
                    'SQL_TEXT': sql_text,
                    'OPTIMIZATION_TITLE': opt.get('titre', ''),
                    'PRIORITY': opt.get('priorite', ''),
                    'DESCRIPTION': opt.get('description', ''),
                    'IMPLEMENTATION': opt.get('implementation', ''),
                    'ESTIMATED_GAIN': opt.get('gain_estime', '')
                })
        
        df = pd.DataFrame(recommendations)
        df.to_csv(output_file, index=False)
        logger.success(f"📄 Recommandations exportées : {output_file}")
        
        return df


def main():
    """Fonction principale"""
    logger.info("="*60)
    logger.info("MODULE 5 : ANALYSE D'OPTIMISATION DE REQUÊTES")
    logger.info("="*60)
    
    # Initialiser l'optimiseur
    optimizer = QueryOptimizer()
    
    # Connecter à la source de données
    optimizer.extractor.connect()
    
    # Analyser les requêtes lentes
    results = optimizer.analyze_slow_queries(
        data_dir='data/oracle_exports',
        top_n=5,
        threshold_elapsed=500000  # 0.5 seconde
    )
    
    # Afficher le résumé
    optimizer.print_summary()
    
    # Exporter les recommandations
    optimizer.export_recommendations_csv(
        'data/oracle_exports/optimization_recommendations.csv'
    )
    
    logger.info("\n✅ MODULE 5 TERMINÉ")
    logger.info("📂 Résultats disponibles dans data/oracle_exports/reports/")


if __name__ == "__main__":
    main()