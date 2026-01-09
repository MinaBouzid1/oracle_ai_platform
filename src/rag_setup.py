"""
Module 2 : RAG (Retrieval-Augmented Generation)
Gestion de la base de connaissances vectorielle avec ChromaDB
"""

import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from loguru import logger
import sys
from typing import List, Dict
import glob

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

class OracleRAGSystem:
    """Système RAG pour la plateforme Oracle"""
    
    def __init__(self, persist_directory='data/chroma_db'):
        """
        Args:
            persist_directory: Répertoire de persistance ChromaDB
        """
        self.persist_directory = persist_directory
        self.collection_name = "oracle_knowledge"
        self.client = None
        self.collection = None
        self.embedding_model = None
        
        logger.info("🚀 Initialisation du système RAG")
        self._init_chromadb()
        self._init_embedding_model()
    
    def _init_chromadb(self):
        """Initialise ChromaDB"""
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Créer ou récupérer la collection
            try:
                self.collection = self.client.get_collection(self.collection_name)
                logger.info(f"✅ Collection '{self.collection_name}' chargée")
                logger.info(f"   📊 {self.collection.count()} documents existants")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Oracle knowledge base"}
                )
                logger.info(f"✅ Collection '{self.collection_name}' créée")
                
        except Exception as e:
            logger.error(f"❌ Erreur ChromaDB : {e}")
            raise
    
    def _init_embedding_model(self):
        """Initialise le modèle d'embedding"""
        try:
            logger.info("📥 Chargement du modèle d'embedding...")
            # Modèle léger et performant
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.success("✅ Modèle d'embedding chargé")
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle : {e}")
            raise
    
    def load_documents(self, docs_directory='data/documents'):
        """
        Charge tous les documents du répertoire dans ChromaDB
        
        Args:
            docs_directory: Répertoire contenant les documents texte
        """
        logger.info(f"📚 Chargement des documents depuis {docs_directory}/")
        
        if not os.path.exists(docs_directory):
            logger.warning(f"⚠️  Répertoire {docs_directory} non trouvé")
            return 0
        
        # Trouver tous les fichiers .txt
        doc_files = glob.glob(f"{docs_directory}/*.txt")
        
        if not doc_files:
            logger.warning("⚠️  Aucun fichier .txt trouvé")
            return 0
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, filepath in enumerate(doc_files):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Découper en chunks si le document est long
                chunks = self._split_into_chunks(content, max_length=1000)
                
                for chunk_idx, chunk in enumerate(chunks):
                    doc_id = f"doc_{idx}_chunk_{chunk_idx}"
                    documents.append(chunk)
                    metadatas.append({
                        'source': os.path.basename(filepath),
                        'chunk': chunk_idx,
                        'total_chunks': len(chunks)
                    })
                    ids.append(doc_id)
                
                logger.info(f"  ✅ {os.path.basename(filepath)} ({len(chunks)} chunks)")
                
            except Exception as e:
                logger.error(f"  ❌ Erreur lecture {filepath}: {e}")
        
        # Ajouter à ChromaDB
        if documents:
            logger.info(f"💾 Vectorisation de {len(documents)} chunks...")
            embeddings = self.embedding_model.encode(documents).tolist()
            
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.success(f"✅ {len(documents)} chunks ajoutés à ChromaDB")
        
        return len(documents)
    
    def _split_into_chunks(self, text: str, max_length: int = 1000) -> List[str]:
        """
        Découpe un texte en chunks de taille maximale
        
        Args:
            text: Texte à découper
            max_length: Taille maximale d'un chunk en caractères
        
        Returns:
            Liste de chunks
        """
        # Découpage par paragraphes d'abord
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < max_length:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]
    
    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Récupère les documents les plus pertinents pour une requête
        
        Args:
            query: Question ou requête de l'utilisateur
            top_k: Nombre de documents à retourner
        
        Returns:
            Liste de dictionnaires {document, metadata, distance}
        """
        if self.collection.count() == 0:
            logger.warning("⚠️  Aucun document dans la base")
            return []
        
        # Vectoriser la requête
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Rechercher dans ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count())
        )
        
        # Formater les résultats
        context_docs = []
        for i in range(len(results['documents'][0])):
            context_docs.append({
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        logger.info(f"🔍 Trouvé {len(context_docs)} documents pertinents")
        return context_docs
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques de la base de connaissances"""
        return {
            'total_documents': self.collection.count(),
            'collection_name': self.collection_name,
            'persist_directory': self.persist_directory
        }
    
    def reset(self):
        """Réinitialise la collection (⚠️  supprime toutes les données)"""
        logger.warning("⚠️  Réinitialisation de la base de connaissances...")
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Oracle knowledge base"}
        )
        logger.info("✅ Collection réinitialisée")


def main():
    """Test du système RAG"""
    logger.info("="*60)
    logger.info("MODULE 2 : RAG & VECTOR DATABASE")
    logger.info("="*60)
    
    # Initialiser le système
    rag = OracleRAGSystem()
    
    # Charger les documents
    num_docs = rag.load_documents('data/documents')
    
    if num_docs == 0:
        logger.error("❌ Aucun document chargé")
        logger.info("📝 Créez des fichiers .txt dans data/documents/")
        return
    
    # Test de recherche
    logger.info("\n" + "="*60)
    logger.info("🧪 TEST DE RECHERCHE")
    logger.info("="*60)
    
    test_queries = [
        "Comment optimiser une requête lente avec des index ?",
        "Quels sont les risques de sécurité dans Oracle ?",
        "Comment détecter une injection SQL ?"
    ]
    
    for query in test_queries:
        logger.info(f"\n❓ Requête : {query}")
        results = rag.retrieve_context(query, top_k=3)
        
        for i, doc in enumerate(results, 1):
            logger.info(f"\n  📄 Résultat {i} (distance: {doc['distance']:.3f})")
            logger.info(f"     Source : {doc['metadata']['source']}")
            logger.info(f"     Extrait : {doc['document'][:150]}...")
    
    # Statistiques
    logger.info("\n" + "="*60)
    logger.info("📊 STATISTIQUES")
    logger.info("="*60)
    stats = rag.get_stats()
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("\n✅ MODULE 2 TERMINÉ")


if __name__ == "__main__":
    main()