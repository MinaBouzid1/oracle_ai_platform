"""
Module 9 : Dashboard & Chatbot
Interface web complète pour la plateforme Oracle AI
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Imports des modules
import sys
sys.path.append('src')

from llm_engine import LLMEngine
from rag_setup import OracleRAGSystem
from security_audit import SecurityAuditor
from query_optimizer import QueryOptimizer
from anomaly_detector import AnomalyDetector
from backup_recommender import BackupRecommender
from recovery_guide import RecoveryGuide
from data_extractor import OracleDataExtractor

# Configuration de la page
st.set_page_config(
    page_title="Oracle AI Platform",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .critical-alert {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f44336;
    }
    .success-alert {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des composants (avec cache)
@st.cache_resource
def init_components():
    """Initialise tous les composants de la plateforme"""
    return {
        'llm': LLMEngine(),
        'rag': OracleRAGSystem(),
        'extractor': OracleDataExtractor(use_mock=True)
    }

# Initialisation de la session
if 'components' not in st.session_state:
    st.session_state.components = init_components()
    st.session_state.chat_history = []
    st.session_state.current_page = "Accueil"

components = st.session_state.components

# ============================================================================
# SIDEBAR - Navigation
# ============================================================================

with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=Oracle+AI", use_column_width=True)
    
    st.markdown("---")
    
    page = st.radio(
        "📍 Navigation",
        ["🏠 Accueil", "🔒 Sécurité", "⚡ Performance", "💾 Sauvegardes", "💬 Chatbot"],
        key="navigation"
    )
    
    st.session_state.current_page = page
    
    st.markdown("---")
    
    # Status de la connexion
    st.markdown("### 🔌 Status Système")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("LLM", "✅ Actif", delta="OK")
    with col2:
        st.metric("RAG", "✅ Actif", delta=f"{components['rag'].collection.count()} docs")
    
    st.markdown("---")
    
    # Actions rapides
    st.markdown("### ⚡ Actions Rapides")
    
    if st.button("🔄 Rafraîchir les données"):
        with st.spinner("Extraction en cours..."):
            components['extractor'].connect()
            components['extractor'].extract_all()
        st.success("✅ Données mises à jour")
    
    if st.button("📊 Nouveau scan sécurité"):
        st.session_state.run_security_scan = True
        st.rerun()

# ============================================================================
# PAGE 1 : ACCUEIL
# ============================================================================

if "Accueil" in page:
    st.markdown('<h1 class="main-header">🗄️ Plateforme Intelligente de Gestion Oracle</h1>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="🔒 Score Sécurité",
            value="72/100",
            delta="-8 points",
            delta_color="inverse"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="⚡ Requêtes Lentes",
            value="15",
            delta="+3 depuis hier",
            delta_color="inverse"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="🚨 Anomalies",
            value="3",
            delta="2 critiques",
            delta_color="inverse"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="💾 Dernier Backup",
            value="Il y a 6h",
            delta="OK",
            delta_color="normal"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Alertes critiques
    st.markdown("### 🚨 Alertes Critiques")
    
    alerts_data = [
        {"severity": "🔴", "type": "Sécurité", "message": "Profil DEFAULT sans restrictions détecté", "time": "Il y a 2h"},
        {"severity": "🟠", "type": "Performance", "message": "Requête SELECT * FROM EMPLOYEES très lente (5.2s)", "time": "Il y a 4h"},
        {"severity": "🔴", "type": "Anomalie", "message": "Tentative d'injection SQL détectée (user: APP_USER)", "time": "Il y a 1h"}
    ]
    
    for alert in alerts_data:
        cols = st.columns([0.5, 1, 5, 1.5])
        with cols[0]:
            st.markdown(f"## {alert['severity']}")
        with cols[1]:
            st.markdown(f"**{alert['type']}**")
        with cols[2]:
            st.markdown(alert['message'])
        with cols[3]:
            st.markdown(f"*{alert['time']}*")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Tendance Performance (7 jours)")
        
        # Données simulées
        dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
        perf_data = pd.DataFrame({
            'Date': dates,
            'Temps moyen (ms)': [450, 520, 480, 650, 580, 720, 690]
        })
        
        fig = px.line(perf_data, x='Date', y='Temps moyen (ms)', 
                     title='Temps de réponse moyen',
                     markers=True)
        fig.update_traces(line_color='#1f77b4', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🔒 Répartition des Risques Sécurité")
        
        risk_data = pd.DataFrame({
            'Niveau': ['Critique', 'Haut', 'Moyen', 'Faible'],
            'Nombre': [2, 5, 8, 12]
        })
        
        fig = px.pie(risk_data, values='Nombre', names='Niveau',
                    title='Distribution des risques',
                    color='Niveau',
                    color_discrete_map={
                        'Critique': '#f44336',
                        'Haut': '#ff9800',
                        'Moyen': '#ffc107',
                        'Faible': '#4caf50'
                    })
        st.plotly_chart(fig, use_container_width=True)
    
    # Activité récente
    st.markdown("---")
    st.markdown("### 📋 Activité Récente")
    
    activity_data = pd.DataFrame({
        'Timestamp': ['2024-01-15 14:30', '2024-01-15 14:15', '2024-01-15 14:00', '2024-01-15 13:45'],
        'Module': ['Sécurité', 'Performance', 'Anomalies', 'Backup'],
        'Action': ['Audit complet exécuté', 'Analyse de 10 requêtes', 'Scan de 50 logs', 'Stratégie générée'],
        'Résultat': ['✅ Terminé', '✅ Terminé', '⚠️ 3 alertes', '✅ Terminé']
    })
    
    st.dataframe(activity_data, use_container_width=True, hide_index=True)

# ============================================================================
# PAGE 2 : SÉCURITÉ
# ============================================================================

elif "Sécurité" in page:
    st.markdown("# 🔒 Audit de Sécurité Oracle")
    
    st.markdown("---")
    
    # Bouton pour lancer un audit
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔍 Lancer un Audit Complet", type="primary"):
            st.session_state.run_security_scan = True
    
    with col2:
        if st.button("📥 Charger le Dernier Rapport"):
            st.session_state.load_last_report = True
    
    # Exécution de l'audit
    if st.session_state.get('run_security_scan', False):
        with st.spinner("🔍 Audit de sécurité en cours..."):
            auditor = SecurityAuditor()
            results = auditor.audit_full('data/oracle_exports')
            st.session_state.security_results = results
            st.session_state.run_security_scan = False
        st.success("✅ Audit terminé!")
    
    # Affichage des résultats
    if 'security_results' in st.session_state:
        results = st.session_state.security_results
        
        # Score global
        st.markdown("## 🎯 Score Global de Sécurité")
        
        score = results.get('score_global', 0)
        niveau = results.get('niveau_risque_global', 'inconnu')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Jauge de score
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Score de Sécurité"},
                delta={'reference': 80},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 40], 'color': "#ffcdd2"},
                        {'range': [40, 60], 'color': "#fff9c4"},
                        {'range': [60, 80], 'color': "#c8e6c9"},
                        {'range': [80, 100], 'color': "#a5d6a7"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 80
                    }
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Statistiques")
            resume = results.get('resume', {})
            st.metric("Total Risques", resume.get('total_risques', 0))
            st.metric("🔴 Critiques", resume.get('risques_critiques', 0))
            st.metric("🟠 Hauts", resume.get('risques_hauts', 0))
            st.metric("🟡 Moyens", resume.get('risques_moyens', 0))
        
        st.markdown("---")
        
        # Top risques
        st.markdown("## ⚠️ Principaux Risques Détectés")
        
        top_risks = resume.get('top_3_risques', [])
        
        for i, risk in enumerate(top_risks, 1):
            severity = risk.get('severite', 'faible')
            severity_color = {
                'critique': '🔴',
                'haute': '🟠',
                'moyenne': '🟡',
                'faible': '🟢'
            }
            
            with st.expander(f"{severity_color.get(severity, '⚪')} Risque #{i}: {risk.get('titre', 'N/A')}", expanded=(i==1)):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Description:**")
                    st.write(risk.get('description', 'N/A'))
                    
                    st.markdown(f"**Impact:**")
                    st.write(risk.get('impact', 'N/A'))
                    
                    st.markdown(f"**Recommandation:**")
                    st.info(risk.get('recommandation', 'N/A'))
                
                with col2:
                    st.markdown(f"**Sévérité:**")
                    st.markdown(f"## {severity_color.get(severity, '⚪')} {severity.upper()}")
                    st.markdown(f"**Source:**")
                    st.write(risk.get('source', 'N/A'))
        
        # Détails par catégorie
        st.markdown("---")
        st.markdown("## 📑 Détails par Catégorie")
        
        tabs = st.tabs(["👥 Utilisateurs", "🔑 Privilèges", "🔐 Profils"])
        
        with tabs[0]:
            users_audit = results['audits'].get('users', {})
            if 'risques' in users_audit:
                st.markdown(f"**Score:** {users_audit.get('score_securite', 'N/A')}/100")
                st.markdown(f"**Niveau:** {users_audit.get('niveau_risque', 'N/A')}")
                
                for risk in users_audit['risques']:
                    st.warning(f"⚠️ {risk.get('titre', 'N/A')}")
                    st.write(risk.get('description', 'N/A'))
        
        with tabs[1]:
            privs_audit = results['audits'].get('privileges', {})
            if 'risques' in privs_audit:
                st.markdown(f"**Score:** {privs_audit.get('score_securite', 'N/A')}/100")
                for risk in privs_audit['risques']:
                    st.warning(f"⚠️ {risk.get('titre', 'N/A')}")
        
        with tabs[2]:
            profiles_audit = results['audits'].get('profiles', {})
            if 'risques' in profiles_audit:
                st.markdown(f"**Score:** {profiles_audit.get('score_securite', 'N/A')}/100")
                for risk in profiles_audit['risques']:
                    st.warning(f"⚠️ {risk.get('titre', 'N/A')}")
    
    else:
        st.info("👆 Cliquez sur 'Lancer un Audit Complet' pour démarrer l'analyse de sécurité")

# ============================================================================
# PAGE 3 : PERFORMANCE
# ============================================================================

elif "Performance" in page:
    st.markdown("# ⚡ Optimisation des Performances")
    
    st.markdown("---")
    
    # Bouton pour analyser
    if st.button("🔍 Analyser les Requêtes Lentes", type="primary"):
        with st.spinner("⚡ Analyse en cours..."):
            optimizer = QueryOptimizer()
            optimizer.extractor.connect()
            results = optimizer.analyze_slow_queries(
                data_dir='data/oracle_exports',
                top_n=5,
                threshold_elapsed=500000
            )
            st.session_state.optimization_results = results
        st.success("✅ Analyse terminée!")
    
    # Affichage des résultats
    if 'optimization_results' in st.session_state:
        results = st.session_state.optimization_results
        
        valid_results = [r for r in results if 'error' not in r]
        
        st.markdown(f"## 📊 {len(valid_results)} Requêtes Analysées")
        
        st.markdown("---")
        
        # Afficher chaque requête
        for i, result in enumerate(valid_results, 1):
            sql_id = result.get('sql_id', 'N/A')
            sql_text = result.get('sql_text', 'N/A')
            resume = result.get('resume', 'N/A')
            
            with st.expander(f"🔍 Requête #{i}: {sql_id}", expanded=(i==1)):
                # SQL
                st.markdown("### 📝 Requête SQL")
                st.code(sql_text, language='sql')
                
                # Résumé
                st.markdown("### 💡 Analyse")
                st.info(resume)
                
                # Métriques
                st.markdown("### 📊 Métriques")
                metrics = result.get('metrics', {})
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Exécutions", metrics.get('EXECUTIONS', 'N/A'))
                with col2:
                    avg_time = metrics.get('AVG_ELAPSED', 0) / 1000
                    st.metric("Temps moyen", f"{avg_time:.1f}ms")
                with col3:
                    st.metric("Buffer Gets", f"{metrics.get('BUFFER_GETS', 0):,}")
                with col4:
                    st.metric("Disk Reads", f"{metrics.get('DISK_READS', 0):,}")
                
                # Optimisations
                st.markdown("### 🚀 Optimisations Proposées")
                
                optimizations = result.get('optimisations', [])
                
                for j, opt in enumerate(optimizations, 1):
                    priority = opt.get('priorite', 'faible')
                    priority_color = {
                        'haute': '🔴',
                        'moyenne': '🟡',
                        'faible': '🟢'
                    }
                    
                    st.markdown(f"#### {priority_color.get(priority, '⚪')} Optimisation #{j}: {opt.get('titre', 'N/A')}")
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(opt.get('description', 'N/A'))
                        
                        st.markdown("**Implémentation:**")
                        st.code(opt.get('implementation', 'N/A'), language='sql')
                    
                    with col2:
                        st.markdown(f"**Priorité:** {priority}")
                        st.markdown(f"**Gain estimé:** {opt.get('gain_estime', 'N/A')}")
                
                st.markdown("---")
    
    else:
        st.info("👆 Cliquez sur 'Analyser les Requêtes Lentes' pour démarrer")

# ============================================================================
# PAGE 4 : SAUVEGARDES
# ============================================================================

elif "Sauvegardes" in page:
    st.markdown("# 💾 Gestion des Sauvegardes")
    
    tabs = st.tabs(["📋 Stratégie de Sauvegarde", "🔧 Guide de Restauration"])
    
    with tabs[0]:
        st.markdown("## 💾 Recommandation de Stratégie")
        
        with st.form("backup_form"):
            st.markdown("### 📝 Exigences")
            
            col1, col2 = st.columns(2)
            
            with col1:
                rpo = st.selectbox(
                    "RPO (Recovery Point Objective)",
                    ["15 minutes", "1 heure", "4 heures", "1 jour"]
                )
                
                rto = st.selectbox(
                    "RTO (Recovery Time Objective)",
                    ["1 heure", "4 heures", "8 heures", "1 jour"]
                )
                
                db_size = st.text_input("Taille de la base", "100GB")
            
            with col2:
                criticality = st.selectbox(
                    "Criticité",
                    ["critique", "haute", "moyenne", "faible"]
                )
                
                budget = st.selectbox(
                    "Budget",
                    ["illimité", "élevé", "moyen", "limité"]
                )
                
                transaction_volume = st.selectbox(
                    "Volume de transactions",
                    ["très élevé", "élevé", "moyen", "faible"]
                )
            
            submit = st.form_submit_button("🚀 Générer la Stratégie", type="primary")
            
            if submit:
                with st.spinner("💾 Génération de la stratégie..."):
                    recommender = BackupRecommender()
                    strategy = recommender.recommend_strategy(
                        rpo=rpo,
                        rto=rto,
                        db_size=db_size,
                        criticality=criticality,
                        budget=budget,
                        transaction_volume=transaction_volume
                    )
                    st.session_state.backup_strategy = strategy
                st.success("✅ Stratégie générée!")
        
        # Affichage de la stratégie
        if 'backup_strategy' in st.session_state:
            strategy = st.session_state.backup_strategy
            
            st.markdown("---")
            st.markdown("## 📊 Stratégie Recommandée")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### {strategy.get('strategie_recommandee', 'N/A')}")
                st.write(strategy.get('justification', 'N/A'))
            
            with col2:
                st.metric("Type", strategy.get('type_backup', 'N/A'))
                st.metric("Rétention", strategy.get('retention', 'N/A'))
                st.metric("Coût estimé", strategy.get('cout_estime', 'N/A'))
            
            st.markdown("### ⏰ Fréquences")
            frequence = strategy.get('frequence', {})
            for backup_type, freq in frequence.items():
                st.write(f"• **{backup_type.title()}:** {freq}")
            
            st.markdown("### 📜 Scripts RMAN")
            
            scripts = strategy.get('scripts', {})
            for script_name, script_content in scripts.items():
                with st.expander(f"📄 {script_name.replace('_', ' ').title()}"):
                    st.code(script_content, language='sql')
    
    with tabs[1]:
        st.markdown("## 🔧 Guide de Restauration")
        
        st.markdown("### 📋 Choisissez votre scénario")
        
        scenario = st.selectbox(
            "Scénario de récupération",
            [
                "Restauration complète après crash",
                "Récupération point-in-time (PITR)",
                "Récupération de table",
                "Récupération de tablespace"
            ]
        )
        
        if st.button("📖 Générer le Playbook", type="primary"):
            with st.spinner("📖 Génération du playbook..."):
                guide = RecoveryGuide()
                
                scenario_map = {
                    "Restauration complète après crash": ('complete_restore', {
                        'has_rman_backups': True,
                        'has_archive_logs': True,
                        'last_backup_date': '2024-01-15',
                        'target': 'latest'
                    }),
                    "Récupération point-in-time (PITR)": ('point_in_time', {
                        'target_time': '2024-01-15 14:30:00',
                        'tablespaces': ['USERS'],
                        'has_archive_logs': True
                    }),
                    "Récupération de table": ('table_recovery', {
                        'table_name': 'EMPLOYEES',
                        'action': 'DROP',
                        'incident_time': '2024-01-15 10:00:00',
                        'flashback_enabled': True
                    }),
                    "Récupération de tablespace": ('tablespace_recovery', {
                        'tablespace_name': 'USERS',
                        'reason': 'corruption',
                        'has_backup': True
                    })
                }
                
                scenario_key, details = scenario_map[scenario]
                playbook = guide.generate_playbook(scenario_key, details)
                st.session_state.recovery_playbook = playbook
            
            st.success("✅ Playbook généré!")
        
        # Affichage du playbook
        if 'recovery_playbook' in st.session_state:
            playbook = st.session_state.recovery_playbook
            
            st.markdown("---")
            
            metadata = playbook.get('metadata', {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⏱️ Durée estimée", metadata.get('estimated_duration', 'N/A'))
            with col2:
                st.metric("⚠️ Niveau de risque", metadata.get('risk_level', 'N/A'))
            with col3:
                st.metric("📋 Prérequis", len(metadata.get('prerequisites', [])))
            
            st.markdown("### ✅ Prérequis")
            for prereq in metadata.get('prerequisites', []):
                st.write(f"• {prereq}")
            
            st.markdown("### 📝 Procédure Détaillée")
            st.text_area(
                "Playbook",
                playbook.get('content', 'N/A'),
                height=400
            )

# ============================================================================
# PAGE 5 : CHATBOT
# ============================================================================

elif "Chatbot" in page:
    st.markdown("# 💬 Assistant Oracle AI")
    
    st.markdown("---")
    
    # Suggestions de questions
    st.markdown("### 💡 Suggestions de questions")
    
    suggestions = [
        "Pourquoi ma requête SELECT * FROM EMPLOYEES est-elle lente ?",
        "Y a-t-il des risques de sécurité dans ma configuration ?",
        "Comment récupérer une table supprimée par erreur ?",
        "Quelle stratégie de sauvegarde recommandez-vous ?",
        "Qu'est-ce qu'une injection SQL et comment la détecter ?"
    ]
    
    cols = st.columns(len(suggestions))
    for i, (col, suggestion) in enumerate(zip(cols, suggestions)):
        with col:
            if st.button(f"❓ {i+1}", key=f"suggestion_{i}"):
                st.session_state.selected_question = suggestion
    
    # Zone de saisie
    user_input = st.text_input(
        "Votre question:",
        value=st.session_state.get('selected_question', ''),
        placeholder="Posez votre question ici...",
        key="chat_input"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button("📤 Envoyer", type="primary")
    with col2:
        if st.button("🗑️ Effacer l'historique"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Traitement de la question
    if send_button and user_input:
        with st.spinner("🤖 Réflexion en cours..."):
            # Récupérer le context RAG
            context_docs = components['rag'].retrieve_context(user_input, top_k=3)
            context = "\n\n".join([doc['document'] for doc in context_docs])
            
            # Générer la réponse
            response = components['llm'].chat(
                user_question=user_input,
                chat_history=st.session_state.chat_history,
                context=context
            )
            
            # Ajouter à l'historique
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            
            # Effacer la question sélectionnée
            if 'selected_question' in st.session_state:
                del st.session_state.selected_question
    
    # Affichage de l'historique
    st.markdown("---")
    st.markdown("### 💬 Conversation")
    
    if st.session_state.chat_history:
        for i, message in enumerate(reversed(st.session_state.chat_history)):
            if message['role'] == 'user':
                st.markdown(f"""
                <div style='background-color: #e3f2fd; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;'>
                    <strong>👤 Vous:</strong><br/>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background-color: #f5f5f5; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;'>
                    <strong>🤖 Assistant:</strong><br/>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💬 Posez votre première question pour commencer la conversation!")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🗄️ <strong>Plateforme Oracle AI</strong> | Développé avec ❤️ | Version 1.0</p>
    <p>Propulsé par Claude AI + RAG + Oracle Database</p>
</div>
""", unsafe_allow_html=True)