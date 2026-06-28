import logging
import httpx
import json
from typing import Optional, Dict, Any, List
from app.core.database import get_db_connection

logger = logging.getLogger(__name__)

class AIService:
    """Service for interacting with LLMs (OpenAI Compatible)"""

    @staticmethod
    async def get_config() -> Dict[str, str]:
        """Fetch AI configuration from database with defaults"""
        # Default fallback config
        config = {
            'enabled': 'false',
            'provider': 'openai',
            'base_url': 'https://api.openai.com/v1',
            'api_key': '',
            'model': 'gpt-3.5-turbo',
            'embed_model': 'text-embedding-3-small',
            'embed_base_url': 'https://api.openai.com/v1',
            'embed_api_key': '',
            'rerank_model': 'bge-reranker-v2-m3',
            'rerank_base_url': '',
            'rerank_api_key': ''
        }
        try:
            async with get_db_connection() as db:
                async with db.cursor() as cursor:
                    await cursor.execute(
                        "SELECT config_key, config_value FROM sys_config WHERE config_group = 'ai'"
                    )
                    rows = await cursor.fetchall()
                    for row in rows:
                        key = row[0].replace('ai.', '').strip()
                        val = str(row[1]).strip()
                        config[key] = val
        except Exception as e:
            logger.warning(f"Failed to fetch AI config from DB, using defaults: {e}")
            
        return config

    @staticmethod
    async def chat_completion(messages: List[Dict[str, str]], stream: bool = False) -> Optional[str]:
        """Send a chat completion request to the configured LLM"""
        config = await AIService.get_config()
        
        if config.get('enabled') != 'true':
            raise ValueError("AI feature is currently disabled in system settings.")

        base_url = config.get('base_url', '').rstrip('/')
        api_key = config.get('api_key')
        model = config.get('model')

        if not base_url or not api_key:
            raise ValueError("AI Base URL or API Key is missing in configuration.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.0, # Use 0.0 for maximum determinism in logic/SQL tasks
            "stream": stream
        }

        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"AI API Request failed: {e}")
                raise ValueError(f"AI Service Error: {str(e)}")

    @staticmethod
    async def chat_completion_stream(messages: List[Dict[str, str]]):
        """Send a streaming chat completion request to the configured LLM"""
        config = await AIService.get_config()
        
        if config.get('enabled') != 'true':
            raise ValueError("AI feature is currently disabled in system settings.")

        base_url = config.get('base_url', '').rstrip('/')
        api_key = config.get('api_key')
        model = config.get('model')

        if not base_url or not api_key:
            raise ValueError("AI Base URL or API Key is missing in configuration.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.0, 
            "stream": True
        }

        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                async with client.stream("POST", f"{base_url}/chat/completions", headers=headers, json=payload) as response:
                    if response.status_code != 200:
                         error_text = await response.aread()
                         logger.error(f"AI Stream API Error: {response.status_code} - {error_text}")
                         yield f"[AI Provider Error: {response.status_code}]"
                         return

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Handle standard SSE format
                        if line.startswith("data:"):
                            # Remove "data:" prefix and any leading space
                            content_json = line[5:].lstrip()
                            
                            if content_json == "[DONE]":
                                break
                                
                            try:
                                chunk = json.loads(content_json)
                                choices = chunk.get('choices', [])
                                if choices:
                                    delta = choices[0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        if content:
                                            yield content
                            except json.JSONDecodeError:
                                # Some providers might send non-JSON data or concatenated chunks
                                logger.warning(f"Failed to decode AI stream chunk: {line}")
                                continue
                            except Exception as e:
                                logger.error(f"Error processing stream chunk: {e}")
                                continue
            except Exception as e:
                logger.error(f"AI Stream Request failed: {e}")
                yield f"\n[System Error: {str(e)}]"

    @staticmethod
    async def test_connection(config_override: Dict[str, str] = None) -> bool:
        """Test the connection with the given or stored configuration"""
        # If no override, use stored config
        config = config_override or await AIService.get_config()
        
        base_url = config.get('base_url', '').rstrip('/')
        api_key = config.get('api_key')
        model = config.get('model')

        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 5
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            return True

    @staticmethod
    async def rerank(query: str, documents: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Rerank a list of documents based on relevance to the query.
        Returns a list of {"index": int, "relevance_score": float}.
        """
        config = await AIService.get_config()
        
        if config.get('enabled') != 'true':
            raise ValueError("AI feature is currently disabled.")

        base_url = config.get('rerank_base_url') or config.get('base_url', '').rstrip('/')
        api_key = config.get('rerank_api_key') or config.get('api_key')
        model = config.get('rerank_model')

        if not base_url or not api_key:
            # Fallback: If no dedicated rerank config, we can't perform rerank.
            # Or should we assume the embedding provider supports rerank? 
            # Most OpenAI-compatible APIs (like vLLM/Xinference) use /v1/rerank
            raise ValueError("Rerank Base URL or API Key is missing.")
            
        # Adjust endpoint
        # Standard convention for rerank in OpenAI-compatible world is often /v1/rerank
        # But if the user provided a full URL ending in /rerank, respect it.
        if base_url.endswith('/rerank'):
            url = base_url
        elif base_url.endswith('/v1'):
            url = f"{base_url}/rerank"
        else:
            url = f"{base_url}/v1/rerank"
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "query": query,
            "documents": documents,
            "top_n": top_n,
            "return_documents": False # We only need indices and scores
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Standard response format: {"results": [{"index": 0, "relevance_score": 0.9}, ...]}
                # Some providers (like Cohere) use slightly different format, but /v1/rerank usually follows this.
                if 'results' in data:
                    return data['results']
                elif 'data' in data: # Some might use 'data'
                    return data['data']
                else:
                    logger.warning(f"Unexpected Rerank response format: {data}")
                    return []
                    
            except Exception as e:
                logger.error(f"Rerank Request failed: {e}")
                # Fallback: return empty list or raise?
                # If rerank fails, we should probably fall back to original order, so log error and re-raise or return empty.
                raise ValueError(f"Rerank Error: {str(e)}")

    @staticmethod
    async def create_embedding(text: str) -> List[float]:
        """Generate vector embedding for the given text"""
        config = await AIService.get_config()
        
        if config.get('enabled') != 'true':
            raise ValueError("AI feature is currently disabled.")

        # Prefer specific embedding config, fallback to main config
        base_url = config.get('embed_base_url') or config.get('base_url', '').rstrip('/')
        api_key = config.get('embed_api_key') or config.get('api_key')
        model = config.get('embed_model')

        if not base_url or not api_key:
            raise ValueError("AI Embedding Base URL or API Key is missing.")

        # Adjust endpoint if base_url includes /v1
        if base_url.endswith('/v1'):
            url = f"{base_url}/embeddings"
        else:
            url = f"{base_url}/v1/embeddings"
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "input": text
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data['data'][0]['embedding']
            except Exception as e:
                logger.error(f"AI Embedding Request failed: {e}")
                raise ValueError(f"Embedding Error: {str(e)}")
