
"""
Module 9 : Dashboard & Chatbot
Interface web complete pour la plateforme Oracle AI
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
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PROFESSIONAL CSS STYLING
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --primary-light: #818cf8;
        --secondary: #0ea5e9;
        --accent: #f59e0b;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --dark: #0f172a;
        --dark-secondary: #1e293b;
        --dark-tertiary: #334155;
        --light: #f8fafc;
        --border: rgba(255,255,255,0.1);
        --glass: rgba(15, 23, 42, 0.8);
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--dark); }
    ::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--primary-light); }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15,23,42,0.98) 0%, rgba(30,27,75,0.98) 100%);
        border-right: 1px solid rgba(99,102,241,0.2);
    }
    
    [data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
    }
    
    p, span, label, div { color: #cbd5e1; }
    
    .hero-header {
        background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(14,165,233,0.15) 100%);
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 24px;
        padding: 3rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #f8fafc 0%, #6366f1 50%, #0ea5e9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    .glass-card {
        background: linear-gradient(135deg, rgba(30,41,59,0.8) 0%, rgba(15,23,42,0.9) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 20px;
        padding: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card:hover {
        border-color: rgba(99,102,241,0.5);
        transform: translateY(-2px);
        box-shadow: 0 20px 40px rgba(99,102,241,0.15);
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99,102,241,0.5), transparent);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(30,41,59,0.6) 0%, rgba(15,23,42,0.8) 100%);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 16px;
        padding: 1.25rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: rgba(99,102,241,0.4);
        box-shadow: 0 10px 30px rgba(99,102,241,0.1);
    }
    
    .metric-card .icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .metric-card .icon.purple { background: rgba(99,102,241,0.2); }
    .metric-card .icon.blue { background: rgba(14,165,233,0.2); }
    .metric-card .icon.orange { background: rgba(245,158,11,0.2); }
    .metric-card .icon.green { background: rgba(16,185,129,0.2); }
    .metric-card .icon.red { background: rgba(239,68,68,0.2); }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
        margin-top: 0.25rem;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.5rem;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        border-radius: 6px;
    }
    
    .metric-delta.positive { background: rgba(16,185,129,0.15); color: #10b981; }
    .metric-delta.negative { background: rgba(239,68,68,0.15); color: #ef4444; }
    .metric-delta.neutral { background: rgba(99,102,241,0.15); color: #818cf8; }
    
    .alert-card {
        background: linear-gradient(135deg, rgba(30,41,59,0.6) 0%, rgba(15,23,42,0.8) 100%);
        border: 1px solid;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.3s ease;
    }
    
    .alert-card:hover { transform: translateX(4px); }
    
    .alert-card.critical {
        border-color: rgba(239,68,68,0.3);
        background: linear-gradient(135deg, rgba(239,68,68,0.1) 0%, rgba(15,23,42,0.8) 100%);
    }
    
    .alert-card.warning {
        border-color: rgba(245,158,11,0.3);
        background: linear-gradient(135deg, rgba(245,158,11,0.1) 0%, rgba(15,23,42,0.8) 100%);
    }
    
    .alert-card.info {
        border-color: rgba(14,165,233,0.3);
        background: linear-gradient(135deg, rgba(14,165,233,0.1) 0%, rgba(15,23,42,0.8) 100%);
    }
    
    .alert-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        flex-shrink: 0;
    }
    
    .alert-icon.critical { background: rgba(239,68,68,0.2); }
    .alert-icon.warning { background: rgba(245,158,11,0.2); }
    .alert-icon.info { background: rgba(14,165,233,0.2); }
    
    .alert-content { flex: 1; }
    
    .alert-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 2px;
    }
    
    .alert-message { font-size: 0.8rem; color: #94a3b8; }
    .alert-time { font-size: 0.75rem; color: #64748b; white-space: nowrap; }
    
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(99,102,241,0.2);
    }
    
    .section-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(14,165,233,0.2) 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #f8fafc;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important;
    }
    
    .secondary-btn > button {
        background: transparent !important;
        border: 1px solid rgba(99,102,241,0.4) !important;
        color: #818cf8 !important;
        box-shadow: none !important;
    }
    
    .secondary-btn > button:hover {
        background: rgba(99,102,241,0.1) !important;
        border-color: rgba(99,102,241,0.6) !important;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: rgba(30,41,59,0.8) !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(99,102,241,0.5) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
    }
    
    .streamlit-expanderHeader {
        background: rgba(30,41,59,0.6) !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(15,23,42,0.8) !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(30,41,59,0.6);
        border-radius: 12px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
        padding: 0.75rem 1.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(99,102,241,0.1) !important;
        color: #f8fafc !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.3) 0%, rgba(14,165,233,0.2) 100%) !important;
        color: #f8fafc !important;
    }
    
    .stDataFrame { border-radius: 12px !important; overflow: hidden; }
    
    [data-testid="stDataFrame"] > div {
        background: rgba(30,41,59,0.6) !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
        border-radius: 12px !important;
    }
    
    .stCodeBlock {
        background: rgba(15,23,42,0.9) !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
        border-radius: 12px !important;
    }
    
    code { font-family: 'JetBrains Mono', monospace !important; }
    
    [data-testid="stMetricValue"] {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
    }
    
    [data-testid="stMetricLabel"] { color: #64748b !important; }
    [data-testid="stMetricDelta"] { font-size: 0.85rem !important; }
    
    .chat-message {
        padding: 1.25rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        position: relative;
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(99,102,241,0.1) 100%);
        border: 1px solid rgba(99,102,241,0.3);
        margin-left: 2rem;
    }
    
    .chat-message.assistant {
        background: linear-gradient(135deg, rgba(30,41,59,0.8) 0%, rgba(15,23,42,0.9) 100%);
        border: 1px solid rgba(99,102,241,0.15);
        margin-right: 2rem;
    }
    
    .chat-avatar {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        margin-bottom: 0.75rem;
    }
    
    .chat-avatar.user { background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); }
    .chat-avatar.assistant { background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); }
    .chat-content { color: #e2e8f0; font-size: 0.95rem; line-height: 1.6; }
    
    .logo-container { text-align: center; padding: 1.5rem 1rem; margin-bottom: 1.5rem; }
    
    .logo-text {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #0ea5e9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .logo-subtitle {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 4px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent);
        margin: 1.5rem 0;
    }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-badge.online {
        background: rgba(16,185,129,0.15);
        color: #10b981;
        border: 1px solid rgba(16,185,129,0.3);
    }
    
    .status-badge.offline {
        background: rgba(239,68,68,0.15);
        color: #ef4444;
        border: 1px solid rgba(239,68,68,0.3);
    }
    
    [data-testid="stRadio"] > div { gap: 0.5rem; }
    
    [data-testid="stRadio"] label {
        background: rgba(30,41,59,0.6) !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
        border-radius: 12px !important;
        padding: 0.875rem 1rem !important;
        transition: all 0.3s ease !important;
        cursor: pointer;
    }
    
    [data-testid="stRadio"] label:hover {
        background: rgba(99,102,241,0.1) !important;
        border-color: rgba(99,102,241,0.4) !important;
    }
    
    [data-testid="stRadio"] label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(14,165,233,0.1) 100%) !important;
        border-color: rgba(99,102,241,0.5) !important;
    }
    
    [data-testid="stForm"] {
        background: rgba(30,41,59,0.4);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 16px;
        padding: 1.5rem;
    }
    
    .risk-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .risk-badge.critique { background: rgba(239,68,68,0.2); color: #ef4444; }
    .risk-badge.haute { background: rgba(245,158,11,0.2); color: #f59e0b; }
    .risk-badge.moyenne { background: rgba(99,102,241,0.2); color: #818cf8; }
    .risk-badge.faible { background: rgba(16,185,129,0.2); color: #10b981; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Initialisation des composants (avec cache)
# ============================================================================

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
    st.session_state.performance_metrics = None
    st.session_state.optimization_results = None
    st.session_state.security_results = None
    st.session_state.backup_strategy = None
    st.session_state.recovery_playbook = None
    st.session_state.run_security_scan = False
    st.session_state.load_last_report = False

components = st.session_state.components


# ============================================================================
# SIDEBAR - Navigation
# ============================================================================

with st.sidebar:
    # Logo
    st.markdown('''
    <div class="logo-container">
        <div class="logo-text">Oracle AI</div>
        <div class="logo-subtitle">Intelligence Platform</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Accueil", "Securite", "Performance", "Sauvegardes", "Chatbot"],
        key="navigation",
        label_visibility="collapsed",
        format_func=lambda x: {
            "Accueil": "🏠  Accueil",
            "Securite": "🛡️  Securite",
            "Performance": "⚡  Performance",
            "Sauvegardes": "💾  Sauvegardes",
            "Chatbot": "💬  Assistant IA"
        }[x]
    )
    
    st.session_state.current_page = page
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Status de la connexion
    st.markdown('''
    <div style="margin-bottom: 1rem;">
        <p style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: #64748b; margin-bottom: 0.75rem;">
            Statut Systeme
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'''
        <div class="metric-card" style="padding: 0.75rem;">
            <div style="font-size: 0.7rem; color: #64748b; margin-bottom: 4px;">LLM</div>
            <div class="status-badge online">
                <span style="width: 6px; height: 6px; background: #10b981; border-radius: 50%; display: inline-block;"></span>
                Actif
            </div>
        </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
        <div class="metric-card" style="padding: 0.75rem;">
            <div style="font-size: 0.7rem; color: #64748b; margin-bottom: 4px;">RAG</div>
            <div class="status-badge online">
                <span style="width: 6px; height: 6px; background: #10b981; border-radius: 50%; display: inline-block;"></span>
                {components['rag'].collection.count()} docs
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Actions rapides
    st.markdown('''
    <div style="margin-bottom: 1rem;">
        <p style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: #64748b; margin-bottom: 0.75rem;">
            Actions Rapides
        </p>
    </div>
    ''', unsafe_allow_html=True)

    if st.button("🔄 Rafraichir les donnees", use_container_width=True):
        with st.spinner("Extraction en cours..."):
        # Essayez d'abord de connecter l'extracteur si la méthode existe
            if hasattr(components['extractor'], 'connect'):
                components['extractor'].connect()
        # Puis exécuter l'extraction
            components['extractor'].extract_all()
        st.success("Donnees mises a jour")
    
    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.button("📊 Nouveau scan securite", use_container_width=True):
        st.session_state.run_security_scan = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# PAGE 1 : ACCUEIL
# ============================================================================

if "Accueil" in page:
    # Hero Header
    st.markdown('''
    <div class="hero-header">
        <div class="hero-title">Oracle AI Platform</div>
        <div class="hero-subtitle">Plateforme intelligente de gestion et d'optimisation de bases de donnees Oracle</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Calculer les métriques de performance pour l'accueil
    try:
        optimizer = QueryOptimizer()
        optimizer.oracle.connect()
        perf_metrics = optimizer.get_performance_metrics(
            data_dir='data/oracle_exports',
            timeframe_days=7
        )
    except Exception as e:
        perf_metrics = {
            'total_execution_time_seconds': 0,
            'slow_queries_count': 0,
            'avg_query_time_ms': 0,
            'total_queries': 0
        }
    
    # Metriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="icon purple">⏱️</div>
            <div class="metric-value">{perf_metrics.get('total_execution_time_seconds', 0):.0f}s</div>
            <div class="metric-label">Temps total exécution</div>
            <div class="metric-delta negative">+12%</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="icon orange">⚡</div>
            <div class="metric-value">{perf_metrics.get('slow_queries_count', 0)}</div>
            <div class="metric-label">Requetes Lentes</div>
            <div class="metric-delta negative">+3 depuis hier</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
        <div class="metric-card">
            <div class="icon red">🚨</div>
            <div class="metric-value">3</div>
            <div class="metric-label">Anomalies</div>
            <div class="metric-delta negative">2 critiques</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown('''
        <div class="metric-card">
            <div class="icon green">💾</div>
            <div class="metric-value">6h</div>
            <div class="metric-label">Dernier Backup</div>
            <div class="metric-delta positive">OK</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Alertes critiques
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('''
        <div class="section-header">
            <div class="section-icon">🚨</div>
            <div class="section-title">Alertes Critiques</div>
        </div>
        ''', unsafe_allow_html=True)
        
        alerts_data = [
            {"severity": "critical", "type": "Securite", "message": "Profil DEFAULT sans restrictions detecte", "time": "Il y a 2h"},
            {"severity": "warning", "type": "Performance", "message": "Requete SELECT * FROM EMPLOYEES tres lente (5.2s)", "time": "Il y a 4h"},
            {"severity": "critical", "type": "Anomalie", "message": "Tentative d'injection SQL detectee (user: APP_USER)", "time": "Il y a 1h"}
        ]
        
        severity_icons = {"critical": "🔴", "warning": "🟠", "info": "🔵"}
        
        for alert in alerts_data:
            st.markdown(f'''
            <div class="alert-card {alert['severity']}">
                <div class="alert-icon {alert['severity']}">{severity_icons[alert['severity']]}</div>
                <div class="alert-content">
                    <div class="alert-title">{alert['type']}</div>
                    <div class="alert-message">{alert['message']}</div>
                </div>
                <div class="alert-time">{alert['time']}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="section-header">
            <div class="section-icon">📊</div>
            <div class="section-title">Repartition Risques</div>
        </div>
        ''', unsafe_allow_html=True)
        
        risk_data = pd.DataFrame({
            'Niveau': ['Critique', 'Haut', 'Moyen', 'Faible'],
            'Nombre': [2, 5, 8, 12]
        })
        
        fig = px.pie(risk_data, values='Nombre', names='Niveau',
                    color='Niveau',
                    color_discrete_map={
                        'Critique': '#ef4444',
                        'Haut': '#f59e0b',
                        'Moyen': '#6366f1',
                        'Faible': '#10b981'
                    },
                    hole=0.6)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#94a3b8',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=20, b=60),
            height=280
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Graphique Performance
    st.markdown('''
    <div class="glass-card">
        <div class="section-header" style="border: none; padding: 0; margin-bottom: 1rem;">
            <div class="section-icon">📈</div>
            <div class="section-title">Tendance Performance (7 jours)</div>
        </div>
    ''', unsafe_allow_html=True)
    
    dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
    perf_data = pd.DataFrame({
        'Date': dates,
        'Temps moyen (ms)': [450, 520, 480, 650, 580, 720, 690]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=perf_data['Date'],
        y=perf_data['Temps moyen (ms)'],
        mode='lines+markers',
        name='Temps de reponse',
        line=dict(color='#6366f1', width=3),
        marker=dict(size=8, color='#6366f1'),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.1)'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#94a3b8',
        xaxis=dict(showgrid=True, gridcolor='rgba(99, 102, 241, 0.1)', tickformat='%d %b'),
        yaxis=dict(showgrid=True, gridcolor='rgba(99, 102, 241, 0.1)', title='ms'),
        margin=dict(l=40, r=40, t=20, b=40),
        height=300,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Activite recente
    st.markdown('''
    <div class="section-header">
        <div class="section-icon">📋</div>
        <div class="section-title">Activite Recente</div>
    </div>
    ''', unsafe_allow_html=True)
    
    activity_data = pd.DataFrame({
        'Timestamp': ['2024-01-15 14:30', '2024-01-15 14:15', '2024-01-15 14:00', '2024-01-15 13:45'],
        'Module': ['Securite', 'Performance', 'Anomalies', 'Backup'],
        'Action': ['Audit complet execute', 'Analyse de 10 requetes', 'Scan de 50 logs', 'Strategie generee'],
        'Resultat': ['Termine', 'Termine', '3 alertes', 'Termine']
    })
    
    st.dataframe(activity_data, use_container_width=True, hide_index=True)


# ============================================================================
# PAGE 2 : SECURITE
# ============================================================================

elif "Securite" in page:
    st.markdown('''
    <div class="hero-header" style="padding: 2rem;">
        <div class="hero-title" style="font-size: 2.5rem;">Audit de Securite Oracle</div>
        <div class="hero-subtitle">Analyse complete des vulnerabilites et recommandations</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Boutons d'action
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔍 Lancer un Audit Complet", type="primary", use_container_width=True):
            st.session_state.run_security_scan = True
    
    with col2:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("📥 Charger Dernier Rapport", use_container_width=True):
            st.session_state.load_last_report = True
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Execution de l'audit
    if st.session_state.get('run_security_scan', False):
        with st.spinner("Audit de securite en cours..."):
            auditor = SecurityAuditor()
            results = auditor.audit_full('data/oracle_exports')
            st.session_state.security_results = results
            st.session_state.run_security_scan = False
        st.success("Audit termine!")
    
    # Affichage des resultats
    if 'security_results' in st.session_state and st.session_state.security_results:
        results = st.session_state.security_results
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Score global
        st.markdown('''
        <div class="section-header">
            <div class="section-icon">🎯</div>
            <div class="section-title">Score Global de Securite</div>
        </div>
        ''', unsafe_allow_html=True)
        
        score = results.get('score_global', 0)
        niveau = results.get('niveau_risque_global', 'inconnu')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Jauge de score
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Score de Securite", 'font': {'color': '#f8fafc', 'size': 16}},
                delta={'reference': 80, 'increasing': {'color': '#10b981'}, 'decreasing': {'color': '#ef4444'}},
                gauge={
                    'axis': {'range': [None, 100], 'tickcolor': '#64748b'},
                    'bar': {'color': "#6366f1"},
                    'bgcolor': "rgba(30,41,59,0.6)",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 40], 'color': "rgba(239,68,68,0.3)"},
                        {'range': [40, 60], 'color': "rgba(245,158,11,0.3)"},
                        {'range': [60, 80], 'color': "rgba(99,102,241,0.3)"},
                        {'range': [80, 100], 'color': "rgba(16,185,129,0.3)"}
                    ],
                    'threshold': {
                        'line': {'color': "#10b981", 'width': 4},
                        'thickness': 0.75,
                        'value': 80
                    }
                }
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#f8fafc'},
                height=350,
                margin=dict(l=30, r=30, t=60, b=30)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            resume = results.get('resume', {})
            
            st.markdown(f'''
            <div class="metric-card" style="margin-bottom: 1rem;">
                <div class="metric-label">Total Risques</div>
                <div class="metric-value">{resume.get('total_risques', 0)}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
            <div class="metric-card" style="margin-bottom: 1rem; border-color: rgba(239,68,68,0.3);">
                <div class="metric-label">🔴 Critiques</div>
                <div class="metric-value" style="color: #ef4444;">{resume.get('risques_critiques', 0)}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
            <div class="metric-card" style="margin-bottom: 1rem; border-color: rgba(245,158,11,0.3);">
                <div class="metric-label">🟠 Hauts</div>
                <div class="metric-value" style="color: #f59e0b;">{resume.get('risques_hauts', 0)}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown(f'''
            <div class="metric-card" style="border-color: rgba(99,102,241,0.3);">
                <div class="metric-label">🟡 Moyens</div>
                <div class="metric-value" style="color: #818cf8;">{resume.get('risques_moyens', 0)}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Top risques
        st.markdown('''
        <div class="section-header">
            <div class="section-icon">⚠️</div>
            <div class="section-title">Principaux Risques Detectes</div>
        </div>
        ''', unsafe_allow_html=True)
        
        top_risks = resume.get('top_3_risques', [])
        severity_colors = {'critique': '🔴', 'haute': '🟠', 'moyenne': '🟡', 'faible': '🟢'}
        
        for i, risk in enumerate(top_risks, 1):
            severity = risk.get('severite', 'faible')
            
            with st.expander(f"{severity_colors.get(severity, '⚪')} Risque #{i}: {risk.get('titre', 'N/A')}", expanded=(i==1)):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Description:**")
                    st.write(risk.get('description', 'N/A'))
                    
                    st.markdown(f"**Impact:**")
                    st.write(risk.get('impact', 'N/A'))
                    
                    st.markdown(f"**Recommandation:**")
                    st.info(risk.get('recommandation', 'N/A'))
                
                with col2:
                    st.markdown(f'''
                    <div style="text-align: center;">
                        <div class="risk-badge {severity}">{severity.upper()}</div>
                        <p style="margin-top: 1rem; font-size: 0.8rem; color: #64748b;">Source</p>
                        <p style="color: #f8fafc; font-size: 0.9rem;">{risk.get('source', 'N/A')}</p>
                    </div>
                    ''', unsafe_allow_html=True)
        
        # Details par categorie
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('''
        <div class="section-header">
            <div class="section-icon">📑</div>
            <div class="section-title">Details par Categorie</div>
        </div>
        ''', unsafe_allow_html=True)
        
        tabs = st.tabs(["👥 Utilisateurs", "🔑 Privileges", "🔐 Profils"])
        
        with tabs[0]:
            users_audit = results['audits'].get('users', {})
            if 'risques' in users_audit:
                st.markdown(f"**Score:** {users_audit.get('score_securite', 'N/A')}/100 | **Niveau:** {users_audit.get('niveau_risque', 'N/A')}")
                for risk in users_audit['risques']:
                    st.warning(f"⚠️ {risk.get('titre', 'N/A')}: {risk.get('description', 'N/A')}")
        
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
        st.markdown('''
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
            <div style="color: #f8fafc; font-size: 1.1rem; margin-bottom: 0.5rem;">Aucun audit disponible</div>
            <div style="color: #64748b;">Cliquez sur "Lancer un Audit Complet" pour demarrer l'analyse de securite</div>
        </div>
        ''', unsafe_allow_html=True)


# ============================================================================
# PAGE 3 : PERFORMANCE
# ============================================================================

elif "Performance" in page:
    st.markdown('''
    <div class="hero-header" style="padding: 2rem;">
        <div class="hero-title" style="font-size: 2.5rem;">Optimisation des Performances</div>
        <div class="hero-subtitle">Analyse et optimisation des requetes lentes</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Nouveau bouton pour analyse détaillée
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔍 Analyser les Requêtes Lentes", type="primary", use_container_width=True):
            with st.spinner("Analyse en cours..."):
                optimizer = QueryOptimizer()
                optimizer.oracle.connect()
                results = optimizer.analyze_slow_queries_from_file(
                    data_dir='data/oracle_exports',
                    top_n=5,
                    threshold_elapsed=500000
         )
                st.session_state.optimization_results = results
            st.success("Analyse terminée!")
    
    with col2:
        if st.button("📊 Obtenir Métriques Globales", type="primary", use_container_width=True):
            with st.spinner("Calcul des métriques..."):
                optimizer = QueryOptimizer()
                optimizer.oracle.connect()
                
                # Nouvelle méthode pour obtenir les métriques globales
                metrics = optimizer.get_performance_metrics(
                    data_dir='data/oracle_exports',
                    timeframe_days=7
                )
                st.session_state.performance_metrics = metrics
            st.success("Métriques calculées!")
    
    # Section 1 : Métriques globales
    if 'performance_metrics' in st.session_state and st.session_state.performance_metrics:
        metrics = st.session_state.performance_metrics
        
        # Vérifier s'il y a une erreur
        if 'error' not in metrics:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('''
            <div class="section-header">
                <div class="section-icon">📈</div>
                <div class="section-title">Métriques de Performance Globales</div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Afficher les 4 métriques principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="icon purple">⏱️</div>
                    <div class="metric-value">{metrics.get('total_execution_time_seconds', 0):.1f}s</div>
                    <div class="metric-label">Temps total d'exécution</div>
                    <div class="metric-delta neutral">
                        {metrics.get('time_trend', '→')}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                avg_time = metrics.get('avg_query_time_ms', 0)
                st.markdown(f'''
                <div class="metric-card">
                    <div class="icon orange">⚡</div>
                    <div class="metric-value">{avg_time:.0f}ms</div>
                    <div class="metric-label">Temps moyen par requête</div>
                    <div class="metric-delta neutral">
                        {metrics.get('avg_time_trend', '→')}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3:
                total_queries = metrics.get('total_queries', 0)
                st.markdown(f'''
                <div class="metric-card">
                    <div class="icon green">📊</div>
                    <div class="metric-value">{total_queries:,}</div>
                    <div class="metric-label">Nombre total de requêtes</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col4:
                slow_queries = metrics.get('slow_queries_count', 0)
                slow_pct = metrics.get('slow_queries_percentage', 0)
                st.markdown(f'''
                <div class="metric-card">
                    <div class="icon red">🐌</div>
                    <div class="metric-value">{slow_queries}</div>
                    <div class="metric-label">Requêtes lentes</div>
                    <div class="metric-delta negative">
                        {slow_pct:.1f}%
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Graphique de distribution des temps d'exécution
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('''
            <div class="glass-card">
                <div class="section-header" style="border: none; padding: 0; margin-bottom: 1rem;">
                    <div class="section-icon">📊</div>
                    <div class="section-title">Distribution des Temps d'Exécution</div>
                </div>
            ''', unsafe_allow_html=True)
            
            if 'query_times_distribution' in metrics and metrics['query_times_distribution']:
                # Créer un DataFrame pour le graphique
                dist_data = pd.DataFrame({
                    'Temps (ms)': metrics['query_times_distribution']
                })
                
                fig = px.histogram(
                    dist_data,
                    x='Temps (ms)',
                    nbins=20,
                    labels={'x': 'Temps d\'exécution (ms)', 'y': 'Nombre de requêtes'},
                    color_discrete_sequence=['#6366f1']
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8',
                    xaxis=dict(showgrid=True, gridcolor='rgba(99, 102, 241, 0.1)'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(99, 102, 241, 0.1)'),
                    margin=dict(l=40, r=40, t=20, b=40),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée de distribution disponible")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Section 2 : Analyse détaillée des requêtes
    if 'optimization_results' in st.session_state and st.session_state.optimization_results:
        results = st.session_state.optimization_results
        valid_results = [r for r in results if 'error' not in r]
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'''
        <div class="section-header">
            <div class="section-icon">🔍</div>
            <div class="section-title">Analyse Détailée des Requêtes</div>
        </div>
        ''', unsafe_allow_html=True)
        
        for i, result in enumerate(valid_results, 1):
            sql_id = result.get('sql_id', 'N/A')
           # Nouveau code corrigé :
            original_sql_text = result.get('sql_text', 'N/A')
            if original_sql_text != 'N/A' and len(original_sql_text) > 200:
                sql_text = original_sql_text[:200] + "..."
            else:
                sql_text = original_sql_text
            resume = result.get('resume', 'N/A')
            
            with st.expander(f"🔍 Requete #{i}: {sql_id}", expanded=(i==1)):
                st.markdown("### 📝 Requete SQL")
                st.code(result.get('sql_text', 'N/A'), language='sql')
                
                st.markdown("### 💡 Analyse")
                st.info(resume)
                
                st.markdown("### 📊 Metriques")
                metrics = result.get('metrics', {})
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Executions", f"{metrics.get('EXECUTIONS', 'N/A'):,}")
                with col2:
                    avg_time = metrics.get('AVG_ELAPSED', 0) / 1000
                    st.metric("Temps moyen", f"{avg_time:.1f}ms")
                with col3:
                    st.metric("Buffer Gets", f"{metrics.get('BUFFER_GETS', 0):,}")
                with col4:
                    st.metric("Disk Reads", f"{metrics.get('DISK_READS', 0):,}")
                
                st.markdown("### 🚀 Optimisations Proposees")
                
                optimizations = result.get('optimisations', [])
                priority_colors = {'haute': '🔴', 'moyenne': '🟡', 'faible': '🟢'}
                
                for j, opt in enumerate(optimizations, 1):
                    priority = opt.get('priorite', 'faible')
                    
                    st.markdown(f"#### {priority_colors.get(priority, '⚪')} Optimisation #{j}: {opt.get('titre', 'N/A')}")
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(opt.get('description', 'N/A'))
                        st.markdown("**Implementation:**")
                        st.code(opt.get('implementation', 'N/A'), language='sql')
                    
                    with col2:
                        st.markdown(f"**Priorite:** {priority}")
                        st.markdown(f"**Gain estime:** {opt.get('gain_estime', 'N/A')}")
    
    elif not st.session_state.get('performance_metrics') and not st.session_state.get('optimization_results'):
        st.markdown('''
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚡</div>
            <div style="color: #f8fafc; font-size: 1.1rem; margin-bottom: 0.5rem;">Prêt pour l'analyse</div>
            <div style="color: #64748b;">Cliquez sur un bouton ci-dessus pour démarrer l'analyse</div>
        </div>
        ''', unsafe_allow_html=True)


# ============================================================================
# PAGE 4 : SAUVEGARDES
# ============================================================================

elif "Sauvegardes" in page:
    st.markdown('''
    <div class="hero-header" style="padding: 2rem;">
        <div class="hero-title" style="font-size: 2.5rem;">Gestion des Sauvegardes</div>
        <div class="hero-subtitle">Strategies de backup et guides de restauration</div>
    </div>
    ''', unsafe_allow_html=True)
    
    tabs = st.tabs(["📋 Strategie de Sauvegarde", "🔧 Guide de Restauration"])
    
    with tabs[0]:
        st.markdown('''
        <div class="section-header">
            <div class="section-icon">💾</div>
            <div class="section-title">Recommandation de Strategie</div>
        </div>
        ''', unsafe_allow_html=True)
        
        with st.form("backup_form"):
            st.markdown("### 📝 Exigences")
            
            col1, col2 = st.columns(2)
            
            with col1:
                rpo = st.selectbox("RPO (Recovery Point Objective)", ["15 minutes", "1 heure", "4 heures", "1 jour"])
                rto = st.selectbox("RTO (Recovery Time Objective)", ["1 heure", "4 heures", "8 heures", "1 jour"])
                db_size = st.text_input("Taille de la base", "100GB")
            
            with col2:
                criticality = st.selectbox("Criticite", ["critique", "haute", "moyenne", "faible"])
                budget = st.selectbox("Budget", ["illimite", "eleve", "moyen", "limite"])
                transaction_volume = st.selectbox("Volume de transactions", ["tres eleve", "eleve", "moyen", "faible"])
            
            submit = st.form_submit_button("🚀 Generer la Strategie", type="primary")
            
            if submit:
                with st.spinner("Generation de la strategie..."):
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
                st.success("Strategie generee!")
        
        if 'backup_strategy' in st.session_state and st.session_state.backup_strategy:
            strategy = st.session_state.backup_strategy
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### {strategy.get('strategie_recommandee', 'N/A')}")
                st.write(strategy.get('justification', 'N/A'))
            
            with col2:
                st.metric("Type", strategy.get('type_backup', 'N/A'))
                st.metric("Retention", strategy.get('retention', 'N/A'))
                st.metric("Cout estime", strategy.get('cout_estime', 'N/A'))
            
            st.markdown("### Frequences")
            frequence = strategy.get('frequence', {})
            for backup_type, freq in frequence.items():
                st.write(f"- **{backup_type.title()}:** {freq}")
            
            st.markdown("### 📜 Scripts RMAN")
            scripts = strategy.get('scripts', {})
            for script_name, script_content in scripts.items():
                with st.expander(f"📄 {script_name.replace('_', ' ').title()}"):
                    st.code(script_content, language='sql')
    
    with tabs[1]:
        st.markdown('''
        <div class="section-header">
            <div class="section-icon">🔧</div>
            <div class="section-title">Guide de Restauration</div>
        </div>
        ''', unsafe_allow_html=True)
        
        scenario = st.selectbox(
            "Scenario de recuperation",
            [
                "Restauration complete apres crash",
                "Recuperation point-in-time (PITR)",
                "Recuperation de table",
                "Recuperation de tablespace"
            ]
        )
        
        if st.button("📖 Generer le Playbook", type="primary"):
            with st.spinner("Generation du playbook..."):
                guide = RecoveryGuide()
                
                scenario_map = {
                    "Restauration complete apres crash": ('complete_restore', {
                        'has_rman_backups': True,
                        'has_archive_logs': True,
                        'last_backup_date': '2024-01-15',
                        'target': 'latest'
                    }),
                    "Recuperation point-in-time (PITR)": ('point_in_time', {
                        'target_time': '2024-01-15 14:30:00',
                        'tablespaces': ['USERS'],
                        'has_archive_logs': True
                    }),
                    "Recuperation de table": ('table_recovery', {
                        'table_name': 'EMPLOYEES',
                        'action': 'DROP',
                        'incident_time': '2024-01-15 10:00:00',
                        'flashback_enabled': True
                    }),
                    "Recuperation de tablespace": ('tablespace_recovery', {
                        'tablespace_name': 'USERS',
                        'reason': 'corruption',
                        'has_backup': True
                    })
                }
                
                scenario_key, details = scenario_map[scenario]
                playbook = guide.generate_playbook(scenario_key, details)
                st.session_state.recovery_playbook = playbook
            
            st.success("Playbook genere!")
        
        if 'recovery_playbook' in st.session_state and st.session_state.recovery_playbook:
            playbook = st.session_state.recovery_playbook
            metadata = playbook.get('metadata', {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Duree estimee", metadata.get('estimated_duration', 'N/A'))
            with col2:
                st.metric("Niveau de risque", metadata.get('risk_level', 'N/A'))
            with col3:
                st.metric("Prerequis", len(metadata.get('prerequisites', [])))
            
            st.markdown("### Prerequis")
            for prereq in metadata.get('prerequisites', []):
                st.write(f"- {prereq}")
            
            st.markdown("### 📝 Procedure Detaillee")
            st.text_area("Playbook", playbook.get('content', 'N/A'), height=400)


# ============================================================================
# PAGE 5 : CHATBOT
# ============================================================================

elif "Chatbot" in page:
    st.markdown('''
    <div class="hero-header" style="padding: 2rem;">
        <div class="hero-title" style="font-size: 2.5rem;">Assistant Oracle AI</div>
        <div class="hero-subtitle">Posez vos questions sur la gestion de votre base Oracle</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Suggestions de questions
    st.markdown('''
    <div class="section-header">
        <div class="section-icon">💡</div>
        <div class="section-title">Suggestions de questions</div>
    </div>
    ''', unsafe_allow_html=True)
    
    suggestions = [
        "Pourquoi ma requete SELECT * FROM EMPLOYEES est-elle lente ?",
        "Y a-t-il des risques de securite dans ma configuration ?",
        "Comment recuperer une table supprimee par erreur ?",
        "Quelle strategie de sauvegarde recommandez-vous ?",
        "Qu'est-ce qu'une injection SQL et comment la detecter ?"
    ]
    
    cols = st.columns(len(suggestions))
    for i, (col, suggestion) in enumerate(zip(cols, suggestions)):
        with col:
            if st.button(f"❓ {i+1}", key=f"suggestion_{i}", help=suggestion):
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
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Effacer l'historique"):
            st.session_state.chat_history = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Traitement de la question
    if send_button and user_input:
        with st.spinner("Reflexion en cours..."):
            # Recuperer le context RAG
            context_docs = components['rag'].retrieve_context(user_input, top_k=3)
            context = "\n\n".join([doc['document'] for doc in context_docs])
            
            # Generer la reponse
            response = components['llm'].chat(
                user_question=user_input,
                chat_history=st.session_state.chat_history,
                context=context
            )
            
            # Ajouter a l'historique
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            
            # Effacer la question selectionnee
            if 'selected_question' in st.session_state:
                del st.session_state.selected_question
    
    # Affichage de l'historique
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('''
    <div class="section-header">
        <div class="section-icon">💬</div>
        <div class="section-title">Conversation</div>
    </div>
    ''', unsafe_allow_html=True)
    
    if st.session_state.chat_history:
        for i, message in enumerate(reversed(st.session_state.chat_history)):
            if message['role'] == 'user':
                st.markdown(f'''
                <div class="chat-message user">
                    <div class="chat-avatar user">👤</div>
                    <div class="chat-content">{message['content']}</div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="chat-message assistant">
                    <div class="chat-avatar assistant">🤖</div>
                    <div class="chat-content">{message['content']}</div>
                </div>
                ''', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">💬</div>
            <div style="color: #f8fafc; font-size: 1.1rem; margin-bottom: 0.5rem;">Aucune conversation</div>
            <div style="color: #64748b;">Posez votre premiere question pour commencer!</div>
        </div>
        ''', unsafe_allow_html=True)


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('''
<div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(99,102,241,0.2);">
    <p style="color: #64748b; font-size: 0.85rem;">
        <span style="color: #6366f1; font-weight: 600;">Oracle AI Platform</span> | Version 1.0
    </p>
</div>
''', unsafe_allow_html=True)

