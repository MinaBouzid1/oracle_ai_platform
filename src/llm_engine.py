"""
Module 3 : LLM Engine
Interface centralisée pour tous les appels LLM du projet
Supporte Claude, OpenAI, Groq et Ollama
"""

import os
import yaml
import json
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from loguru import logger
import sys
import time
import re

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

load_dotenv()


class LLMEngine:
    """Moteur LLM unifié pour la plateforme Oracle"""
    
    def __init__(self, prompts_file='data/prompts.yaml'):
        """
        Args:
            prompts_file: Chemin vers le fichier YAML de prompts
        """
        self.provider = os.getenv('LLM_PROVIDER', 'groq').lower()
        self.prompts = self._load_prompts(prompts_file)
        self.client = None
        self.model = None
        self.max_retries = 3
        self.retry_delay = 2
        
        logger.info(f"🚀 Initialisation LLM Engine (provider: {self.provider})")
        self._init_client()
    
    def _load_prompts(self, prompts_file: str) -> Dict:
        """Charge le fichier de prompts YAML"""
        try:
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts = yaml.safe_load(f)
            logger.success(f"✅ Prompts chargés depuis {prompts_file}")
            return prompts
        except Exception as e:
            logger.error(f"❌ Erreur chargement prompts : {e}")
            return {}
    
    def _init_client(self):
        """Initialise le client LLM selon le provider"""
        try:
            if self.provider == 'claude':
                from anthropic import Anthropic
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY non définie dans .env")
                self.client = Anthropic(api_key=api_key)
                self.model = "claude-3-haiku-20240307"
                logger.success("✅ Client Claude initialisé")
                
            elif self.provider == 'openai':
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise ValueError("OPENAI_API_KEY non définie dans .env")
                self.client = OpenAI(api_key=api_key)
                self.model = "gpt-3.5-turbo"
                logger.success("✅ Client OpenAI initialisé")
                
            elif self.provider == 'groq':
                from groq import Groq
                api_key = os.getenv('GROQ_API_KEY')
                if not api_key:
                    raise ValueError("GROQ_API_KEY non définie dans .env")
                self.client = Groq(api_key=api_key)
                self.model = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
                logger.success(f"✅ Client Groq initialisé (modèle: {self.model})")
                
            elif self.provider == 'ollama':
                import requests
                # Vérifier si Ollama est accessible
                try:
                    requests.get('http://localhost:11434', timeout=2)
                    self.model = os.getenv('OLLAMA_MODEL', 'llama2')
                    logger.success(f"✅ Ollama accessible (modèle: {self.model})")
                except:
                    raise ConnectionError("Ollama non accessible sur localhost:11434")
            else:
                raise ValueError(f"Provider inconnu : {self.provider}")
                
        except Exception as e:
            logger.error(f"❌ Erreur initialisation client : {e}")
            raise
    
    def generate(
        self, 
        prompt_key: str, 
        variables: Optional[Dict] = None,
        context: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> str:
        """
        Génère une réponse LLM à partir d'un prompt template
        
        Args:
            prompt_key: Clé du prompt dans prompts.yaml (ex: "security.analyze_users")
            variables: Variables à injecter dans le template
            context: Context RAG additionnel
            temperature: Créativité (0=déterministe, 1=créatif)
            max_tokens: Longueur max de la réponse
        
        Returns:
            Réponse du LLM (str)
        """
        variables = variables or {}
        
        # Récupérer le prompt template
        prompt_config = self._get_prompt_config(prompt_key)
        if not prompt_config:
            raise ValueError(f"Prompt '{prompt_key}' non trouvé dans prompts.yaml")
        
        # Construire les messages
        system_prompt = prompt_config.get('system', '')
        user_prompt = prompt_config['user']
        
        # Injecter les variables
        if context:
            variables['context'] = context
        
        user_prompt = self._inject_variables(user_prompt, variables)
        
        logger.info(f"🤖 Génération avec prompt: {prompt_key}")
        logger.debug(f"   Variables: {list(variables.keys())}")
        
        # Appel avec retry
        for attempt in range(self.max_retries):
            try:
                response = self._call_llm(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                logger.success(f"✅ Réponse générée ({len(response)} chars)")
                return response
                
            except Exception as e:
                logger.warning(f"⚠️  Tentative {attempt + 1}/{self.max_retries} échouée: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"❌ Échec après {self.max_retries} tentatives")
                    raise
    
    def _call_llm(
        self, 
        system_prompt: str, 
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Appel réel au LLM selon le provider"""
        
        if self.provider == 'claude':
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.content[0].text
        
        elif self.provider == 'openai':
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        elif self.provider == 'groq':
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        elif self.provider == 'ollama':
            import requests
            
            # Construire le prompt combiné pour Ollama
            full_prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()['response']
    
    def _get_prompt_config(self, prompt_key: str) -> Optional[Dict]:
        """Récupère la config d'un prompt (ex: "security.analyze_users")"""
        parts = prompt_key.split('.')
        config = self.prompts
        
        for part in parts:
            if isinstance(config, dict) and part in config:
                config = config[part]
            else:
                return None
        
        return config if isinstance(config, dict) and 'user' in config else None
    
    def _inject_variables(self, template: str, variables: Dict) -> str:
        """Injecte les variables dans un template"""
        result = template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON avec gestion markdown et extraction regex"""
        # Étape 1 : Nettoyage de base
        response = response.strip()
        
        # Étape 2 : Supprimer le texte avant le JSON (très important pour Mistral)
        # Chercher le premier {
        json_start = response.find('{')
        if json_start > 0:
            # Il y a du texte avant, on le supprime
            response = response[json_start:]
        
        # Étape 3 : Supprimer markdown code fences
        if '```' in response:
            # Extraire tout ce qui est entre ```json et ```
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            else:
                # Supprimer juste les ```
                response = response.replace('```json', '').replace('```', '')
        
        response = response.strip()
        
        # Étape 4 : Tentative parsing direct
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.debug(f"Parsing direct échoué : {e}")
            logger.debug(f"JSON nettoyé : {response[:500]}...")
        
        # Étape 5 : Extraire avec regex (chercher {...})
        try:
            # Trouver le JSON entre accolades
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, response, re.DOTALL)
            
            if matches:
                # Prendre le plus long (probablement le JSON complet)
                longest = max(matches, key=len)
                return json.loads(longest)
        except json.JSONDecodeError:
            logger.debug("Extraction regex échouée")
        
        # Étape 6 : Nettoyage agressif
        try:
            # Supprimer virgules traînantes
            cleaned = re.sub(r',(\s*[}\]])', r'\1', response)
            
            # Supprimer commentaires
            cleaned = re.sub(r'//.*?\n', '\n', cleaned)
            cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
            
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Étape 7 : Extraction partielle par regex
        logger.warning("⚠️  Utilisation du mode dégradé (extraction champs individuels)")
        
        result = {}
        
        # Extraire les strings
        for match in re.finditer(r'"([^"]+)"\s*:\s*"([^"]*)"', response):
            key, value = match.groups()
            if key not in result:
                result[key] = value
        
        # Extraire les nombres
        for match in re.finditer(r'"([^"]+)"\s*:\s*(\d+(?:\.\d+)?)', response):
            key, value = match.groups()
            if key not in result:
                result[key] = float(value) if '.' in value else int(value)
        
        # Extraire objets simples
        for match in re.finditer(r'"([^"]+)"\s*:\s*\{([^{}]+)\}', response):
            key, obj = match.groups()
            if key not in result:
                # Parser l'objet imbriqué
                obj_dict = {}
                for inner_match in re.finditer(r'"([^"]+)"\s*:\s*"([^"]*)"', obj):
                    k, v = inner_match.groups()
                    obj_dict[k] = v
                result[key] = obj_dict if obj_dict else {"raw": obj}
        
        if result:
            logger.info(f"✅ Extraction partielle : {len(result)} champs")
            return result
        
        # Étape 8 : Échec total
        logger.error("❌ Échec complet parsing JSON")
        logger.debug(f"Réponse brute : {response[:1000]}")
        
        return {
            "error": "Échec parsing JSON",
            "raw_response": response[:1000]
        }
    
    def _extract_number(self, text: str, field: str) -> Optional[int]:
        """Extrait un nombre d'un champ JSON malformé"""
        pattern = rf'"{field}"\s*:\s*(\d+)'
        match = re.search(pattern, text)
        return int(match.group(1)) if match else None

    def _extract_string(self, text: str, field: str) -> Optional[str]:
        """Extrait une string d'un champ JSON malformé"""
        pattern = rf'"{field}"\s*:\s*"([^"]+)"'
        match = re.search(pattern, text)
        return match.group(1) if match else None
    
    # ========================================================================
    # MÉTHODES SPÉCIALISÉES PAR MODULE
    # ========================================================================
    
    def analyze_query(self, sql_text: str, plan: str, metrics: Dict, context: str = "") -> Dict:
        """
        MODULE 5 : Analyse une requête SQL et propose des optimisations
        
        Returns:
            Dict avec structure JSON de optimization.explain_slow_query
        """
        variables = {
            'sql_text': sql_text,
            'execution_plan': plan,
            'executions': metrics.get('EXECUTIONS', 'N/A'),
            'elapsed_time': metrics.get('ELAPSED_TIME', 'N/A'),
            'cpu_time': metrics.get('CPU_TIME', 'N/A'),
            'buffer_gets': metrics.get('BUFFER_GETS', 'N/A'),
            'disk_reads': metrics.get('DISK_READS', 'N/A'),
            'rows_processed': metrics.get('ROWS_PROCESSED', 'N/A')
        }
        
        response = self.generate(
            'optimization.explain_slow_query',
            variables=variables,
            context=context,
            temperature=0.2
        )
        
        return self._parse_json_response(response)
    
    def assess_security(self, config_data: Dict, config_type: str, context: str = "") -> Dict:
        """
        MODULE 4 : Évalue la sécurité d'une configuration Oracle
        
        Args:
            config_data: Données de config (users, privileges, profiles)
            config_type: Type ("users", "privileges", "profiles")
            context: Context RAG additionnel
        
        Returns:
            Dict avec structure JSON de security.analyze_*
        """
        prompt_key = f"security.analyze_{config_type}"
        
        # Formatter les données pour le prompt
        if isinstance(config_data, dict):
            data_str = json.dumps(config_data, indent=2)
        else:
            data_str = str(config_data)
        
        variables = {
            f'{config_type}_data': data_str
        }
        
        response = self.generate(
            prompt_key,
            variables=variables,
            context=context,
            temperature=0.1  # Très déterministe pour la sécurité
        )
        
        return self._parse_json_response(response)
    
    def detect_anomaly(self, log_entry: Dict, historical_context: str = "", rag_context: str = "") -> Dict:
        """
        MODULE 6 : Détecte si un log d'audit est anormal
        
        Returns:
            Dict avec structure JSON de anomaly.classify_log
        """
        variables = {
            'timestamp': log_entry.get('TIMESTAMP', ''),
            'username': log_entry.get('USERNAME', ''),
            'action': log_entry.get('ACTION', ''),
            'object_name': log_entry.get('OBJECT_NAME', ''),
            'returncode': log_entry.get('RETURNCODE', ''),
            'client_id': log_entry.get('CLIENT_ID', ''),
            'os_username': log_entry.get('OS_USERNAME', ''),
            'terminal': log_entry.get('TERMINAL', ''),
            'context': historical_context or "Aucun historique disponible"
        }
        
        response = self.generate(
            'anomaly.classify_log',
            variables=variables,
            context=rag_context,
            temperature=0.1
        )
        
        return self._parse_json_response(response)
    
    def recommend_backup(self, requirements: Dict, context: str = "") -> Dict:
        """
        MODULE 7 : Recommande une stratégie de sauvegarde
        
        Args:
            requirements: Dict avec rpo, rto, db_size, criticality, budget
        
        Returns:
            Dict avec structure JSON de backup.recommend_strategy
        """
        response = self.generate(
            'backup.recommend_strategy',
            variables=requirements,
            context=context,
            temperature=0.2
        )
        
        return self._parse_json_response(response)
    
    def guide_recovery(self, scenario: str, details: Dict, context: str = "") -> str:
        """
        MODULE 8 : Guide une procédure de récupération
        
        Args:
            scenario: "complete_restore", "point_in_time", "table_recovery"
            details: Détails du scénario
        
        Returns:
            Playbook de récupération (str)
        """
        prompt_key = f"recovery.{scenario}"
        
        response = self.generate(
            prompt_key,
            variables=details,
            context=context,
            temperature=0.1
        )
        
        return response
    
    def chat(self, user_question: str, chat_history: List[Dict], context: str = "") -> str:
        """
        MODULE 9 : Chatbot conversationnel
        
        Args:
            user_question: Question de l'utilisateur
            chat_history: Historique [{role: user/assistant, content: ...}]
            context: Context RAG pertinent
        
        Returns:
            Réponse du chatbot
        """
        # Formatter l'historique
        history_str = ""
        for msg in chat_history[-5:]:  # Garder seulement les 5 derniers messages
            role = "Utilisateur" if msg['role'] == 'user' else "Assistant"
            history_str += f"{role}: {msg['content']}\n\n"
        
        variables = {
            'chat_history': history_str or "Nouvelle conversation",
            'user_question': user_question
        }
        
        response = self.generate(
            'chatbot.general',
            variables=variables,
            context=context,
            temperature=0.5  # Plus créatif pour le chat
        )
        
        return response


def main():
    """Test du LLM Engine"""
    logger.info("="*60)
    logger.info("MODULE 3 : LLM ENGINE & PROMPT ENGINEERING")
    logger.info("="*60)
    
    # Initialiser le moteur
    engine = LLMEngine()
    
    # Test 1 : Test simple
    logger.info("\n🧪 TEST 1 : Génération simple")
    try:
        response = engine.generate('llm.test')
        logger.info(f"✅ Réponse : {response}")
    except Exception as e:
        logger.error(f"❌ Erreur : {e}")
    
    # Test 2 : Analyse de sécurité
    logger.info("\n🧪 TEST 2 : Analyse de sécurité")
    test_users = {
        'users': [
            {
                'USERNAME': 'ADMIN_TEST',
                'ACCOUNT_STATUS': 'OPEN',
                'PROFILE': 'DEFAULT',
                'CREATED': '2020-01-15'
            }
        ]
    }
    
    try:
        result = engine.assess_security(test_users, 'users')
        logger.info(f"✅ Score sécurité : {result.get('score_securite', 'N/A')}")
        logger.info(f"   Niveau risque : {result.get('niveau_risque', 'N/A')}")
        if 'risques' in result:
            logger.info(f"   Risques détectés : {len(result['risques'])}")
    except Exception as e:
        logger.error(f"❌ Erreur : {e}")
    
    # Test 3 : Détection d'anomalie
    logger.info("\n🧪 TEST 3 : Détection d'anomalie")
    test_log = {
        'TIMESTAMP': '2024-01-15 03:45:22',
        'USERNAME': 'APP_USER',
        'ACTION': 'SELECT',
        'OBJECT_NAME': "EMPLOYEES WHERE 1=1 OR '1'='1",
        'RETURNCODE': 0,
        'CLIENT_ID': '192.168.1.50',
        'OS_USERNAME': 'hacker',
        'TERMINAL': 'UNKNOWN'
    }
    
    try:
        result = engine.detect_anomaly(test_log)
        logger.info(f"✅ Classification : {result.get('classification', 'N/A')}")
        logger.info(f"   Type anomalie : {result.get('type_anomalie', 'N/A')}")
        logger.info(f"   Confiance : {result.get('confiance', 'N/A')}%")
    except Exception as e:
        logger.error(f"❌ Erreur : {e}")
    
    logger.info("\n✅ MODULE 3 TERMINÉ")
    logger.info("💡 Le LLM Engine est prêt à être utilisé par les autres modules")


if __name__ == "__main__":
    main()