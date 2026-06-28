import logging
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.core import redis
from app.services.ai_service import AIService
from app.services.metadata_yaml_service import MetadataYamlService
from app.services.metadata_v2_service import MetadataV2Service

logger = logging.getLogger(__name__)

class VectorService:
    """Service for managing vector embeddings and Redis Stack search index"""

    INDEX_NAME = "idx:metadata"
    VECTOR_DIM = 1024  # Updated to match actual model output (e.g. BGE-M3)

    @staticmethod
    async def ensure_index():
        """Ensure Redis Search index exists"""
        r = await redis.get_redis()
        if not r:
            logger.warning("Redis not available, skipping index creation")
            return

        try:
            # Check if index exists
            await r.execute_command("FT.INFO", VectorService.INDEX_NAME)
        except Exception:
            # Index likely doesn't exist, create it
            logger.info(f"Creating Redis Search index: {VectorService.INDEX_NAME}")
            try:
                # Schema: 
                # dataset_id: TAG
                # data_source: TAG
                # type: TAG (table | metric)
                # content: TEXT
                
                await r.execute_command(
                    "FT.CREATE", VectorService.INDEX_NAME,
                    "ON", "HASH",
                    "PREFIX", "1", "metadata:vec:",
                    "SCHEMA",
                    "dataset_id", "TAG", "SORTABLE",
                    "data_source", "TAG", "SORTABLE",
                    "type", "TAG", "SORTABLE",
                    "name", "TEXT", "SORTABLE",
                    "term", "TEXT", "SORTABLE",
                    "content", "TEXT", "WEIGHT", "1.0",
                    "vector", "VECTOR", "HNSW", "6",
                        "TYPE", "FLOAT32",
                        "DIM", str(VectorService.VECTOR_DIM),
                        "DISTANCE_METRIC", "COSINE"
                )
            except Exception as e:
                logger.error(f"Failed to create Redis index: {e}")

    @staticmethod
    async def purge_dataset(dataset_id: int):
        """Physical delete all vector keys associated with a dataset from Redis"""
        r = await redis.get_redis()
        if not r:
            return

        # Use binary client to avoid decoding issues during key retrieval
        binary_r = await redis.get_binary_redis()
        try:
            # Search for all keys belonging to this dataset
            # Note: FT.SEARCH defaults to LIMIT 0 10. We need to fetch more.
            clean_query = f"@dataset_id:{{{dataset_id}}}"
            
            # Use a loop to delete in batches if there are many items
            while True:
                search_res = await binary_r.execute_command(
                    "FT.SEARCH", VectorService.INDEX_NAME, 
                    clean_query, 
                    "NOCONTENT", # Only need keys
                    "RETURN", "1", "__key",
                    "LIMIT", "0", "500" # Batch size
                )
                
                if not search_res or search_res[0] == 0:
                    break
                    
                keys_to_delete = []
                # Extract keys (format: [count, key1, [fields], key2, [fields]])
                # Start from index 1, step 2 (key, fields)
                for i in range(1, len(search_res), 2):
                    key = search_res[i]
                    keys_to_delete.append(key)
                
                if not keys_to_delete:
                    break
                    
                logger.info(f"Cleaning up {len(keys_to_delete)} keys for dataset {dataset_id}")
                await r.delete(*keys_to_delete)
                
                if len(keys_to_delete) < 500: 
                    break
        except Exception as e:
            logger.warning(f"Purge warning (index might be empty): {e}")
        finally:
            await binary_r.close()

    @staticmethod
    async def sync_dataset(dataset_id: int):
        """Full sync of a dataset to vector store (Granular: Tables & Metrics)"""
        logger.info(f"Starting granular vector sync for dataset_id={dataset_id}")
        
        try:
            # 1. Fetch Dataset & Components
            dataset = await MetadataV2Service.get_dataset_by_id(dataset_id)
            if not dataset:
                raise ValueError("Dataset not found")
            
            data_source = dataset.get('data_source', 'default')
            updated_at = str(dataset.get('updated_at', ''))
            
            r = await redis.get_redis()
            if not r:
                raise ValueError("Redis connection failed")
            
            await VectorService.ensure_index()
            
            # 1.5 Clean existing keys for this dataset to avoid stale data (Fix: Purge before Sync)
            await VectorService.purge_dataset(dataset_id)

            # 2. Sync Tables
            tables = dataset.get('tables', [])
            logger.info(f"Syncing {len(tables)} tables...")
            for table in tables:
                try:
                    yaml_content = MetadataYamlService.generate_table_yaml(table)
                    vector = await AIService.create_embedding(yaml_content)
                    
                    if not vector:
                        logger.warning(f"Empty vector for table {table['physical_name']}")
                        continue

                    import numpy as np
                    vector_bytes = np.array(vector, dtype=np.float32).tobytes()
                    
                    key = f"metadata:vec:table:{table['id']}"
                    mapping = {
                        "dataset_id": str(dataset_id),
                        "data_source": data_source,
                        "type": "table",
                        "content": yaml_content,
                        "vector": vector_bytes,
                        "updated_at": updated_at,
                        "name": table['physical_name'],
                        "term": table['term']
                    }
                    await r.hset(key, mapping=mapping)
                except Exception as e:
                    logger.error(f"Failed to sync table {table['id']}: {e}")

            # 3. Sync Metrics
            metrics = dataset.get('metrics', [])
            logger.info(f"Syncing {len(metrics)} metrics...")
            for metric in metrics:
                try:
                    yaml_content = MetadataYamlService.generate_metric_yaml(metric)
                    vector = await AIService.create_embedding(yaml_content)
                    
                    if not vector:
                        continue

                    import numpy as np
                    vector_bytes = np.array(vector, dtype=np.float32).tobytes()
                    
                    key = f"metadata:vec:metric:{metric['id']}"
                    mapping = {
                        "dataset_id": str(dataset_id),
                        "data_source": data_source,
                        "type": "metric",
                        "content": yaml_content,
                        "vector": vector_bytes,
                        "updated_at": updated_at,
                        "name": metric['name'],
                        "display_name": metric['display_name']
                    }
                    await r.hset(key, mapping=mapping)
                except Exception as e:
                    logger.error(f"Failed to sync metric {metric['id']}: {e}")

            # 4. Update Database Status -> Synced (1)
            await MetadataV2Service.update_dataset(dataset_id, {
                "vector_status": 1, 
                "last_vectorized_at": datetime.now() 
            }, mark_stale=False)
            
            logger.info(f"Vector sync completed for dataset_id={dataset_id}")
            
        except Exception as e:
            logger.error(f"Vector sync failed for dataset_id={dataset_id}: {e}")
            # Update Database Status -> Failed (3)
            await MetadataV2Service.update_dataset(dataset_id, {"vector_status": 3}, mark_stale=False)

    @staticmethod
    async def semantic_search(data_source: str, query: str, top_k: int = 8, enable_rerank: bool = False) -> List[Dict[str, Any]]:
        """Perform semantic search using Redis Stack Vector Search (Granular)"""
        # Ensure index exists before searching
        await VectorService.ensure_index()
        
        # Use binary client to avoid UnicodeDecodeError with vector/score data
        r = await redis.get_binary_redis()
        if not r:
            logger.warning("Redis not available for semantic search")
            return []

        try:
            # 1. Generate query embedding
            query_vector = await AIService.create_embedding(query)
            import numpy as np
            query_vector_bytes = np.array(query_vector, dtype=np.float32).tobytes()

            # 2. Construct FT.SEARCH command
            # If rerank is enabled, fetch more candidates (Recall phase)
            search_k = top_k * 3 if enable_rerank else top_k
            
            # Search syntax: (@data_source:{source_name})=>[KNN {search_k} @vector $vec AS score]
            search_query = f"(@data_source:{{{data_source}}})=>[KNN {search_k} @vector $vec AS score]"
            
            # Execute search
            logger.info(f"Executing Redis Search: {search_query}")
            res = await r.execute_command(
                "FT.SEARCH", VectorService.INDEX_NAME,
                search_query,
                "PARAMS", "2", "vec", query_vector_bytes,
                "SORTBY", "score", "ASC",
                "DIALECT", "2"
            )
            
            logger.info(f"Redis Search Result Raw: {res}")

            # Result format: [count, key1, [f1, v1, f2, v2...], key2, ...]
            initial_results = []
            if not res or res[0] == 0:
                return []

            # Parse results
            for i in range(1, len(res), 2):
                key = res[i]
                fields = res[i+1]
                
                # Convert list of fields to dict
                data = {}
                for j in range(0, len(fields), 2):
                    key_name = fields[j].decode() if isinstance(fields[j], bytes) else fields[j]
                    val = fields[j+1]
                    if isinstance(val, bytes) and key_name != 'vector':
                        try:
                            val = val.decode()
                        except:
                            pass
                    data[key_name] = val
                
                initial_results.append({
                    "data": data,
                    "key": key
                })

            # 3. Rerank Phase (Optional)
            final_results = []
            
            if enable_rerank and initial_results:
                try:
                    documents = [item["data"].get("content", "") for item in initial_results]
                    rerank_scores = await AIService.rerank(query, documents, top_n=top_k)
                    
                    # Map scores back to results
                    # rerank_scores is list of {"index": int, "relevance_score": float}
                    for score_obj in rerank_scores:
                        idx = score_obj.get("index")
                        new_score = score_obj.get("relevance_score")
                        if idx is not None and idx < len(initial_results):
                            item = initial_results[idx]
                            data = item["data"]
                            key = item["key"]
                            
                            ds_id = int(data.get('dataset_id', 0))
                            obj_type = data.get('type', 'unknown')
                            obj_name = data.get('name', 'unknown')
                            
                            final_results.append({
                                "dataset_id": ds_id,
                                "reasons": f"Rerank命中{obj_type}: {obj_name} (Score: {new_score:.4f})",
                                "score": new_score, 
                                "item_type": obj_type,
                                "name": obj_name,
                                "item_id": int(key.decode().split(':')[-1]) if isinstance(key, bytes) else int(key.split(':')[-1]),
                                "yaml_content": data.get('content')
                            })
                    
                    # Since rerank API already returns top_n sorted, final_results is sorted.
                except Exception as e:
                    logger.error(f"Rerank failed, falling back to vector search: {e}")
                    # Fallback to initial results (slice to top_k)
                    final_results = [] # clear and refill
                    for item in initial_results[:top_k]:
                        data = item["data"]
                        key = item["key"]
                        score = float(data.get('score', 1.0))
                        # ... construct obj (same as below) ...
                        # To avoid code duplication, we let the "else" block handle the standard construction logic via a helper?
                        # Or just duplicate slightly for now.
                        ds_id = int(data.get('dataset_id', 0))
                        obj_type = data.get('type', 'unknown')
                        obj_name = data.get('name', 'unknown')
                        final_results.append({
                            "dataset_id": ds_id,
                            "reasons": f"命中{obj_type}: {obj_name} (Distance: {score:.4f})",
                            "score": score,
                            "item_type": obj_type,
                            "name": obj_name,
                            "item_id": int(key.decode().split(':')[-1]) if isinstance(key, bytes) else int(key.split(':')[-1]),
                            "yaml_content": data.get('content')
                        })
            
            else:
                # Standard Vector Search (No Rerank)
                for item in initial_results[:top_k]:
                    data = item["data"]
                    key = item["key"]
                    
                    ds_id = int(data.get('dataset_id', 0))
                    score = float(data.get('score', 1.0))
                    obj_type = data.get('type', 'unknown')
                    obj_name = data.get('name', 'unknown')
                    
                    final_results.append({
                        "dataset_id": ds_id,
                        "reasons": f"命中{obj_type}: {obj_name} (Distance: {score:.4f})",
                        "score": score,
                        "item_type": obj_type,
                        "name": obj_name,
                        "item_id": int(key.decode().split(':')[-1]) if isinstance(key, bytes) else int(key.split(':')[-1]),
                        "yaml_content": data.get('content')
                    })

            return final_results

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
        finally:
            await r.close()

    @staticmethod
    async def check_capability() -> Dict[str, Any]:
        """Check if Redis supports Vector Search (RediSearch module)"""
        r = await redis.get_redis()
        if not r:
            return {"supported": False, "error": "Redis not connected"}
            
        try:
            # Check DB Number (Critical for RediSearch)
            from app.core.config import settings
            db_num = settings.REDIS_DB
            db_warning = None
            if db_num != 0:
                db_warning = f"⚠️ 当前 Redis 使用的是 DB {db_num}。注意：RediSearch 模块在许多环境下仅支持 DB 0，在非 0 库下执行 FT.CREATE 可能会报错或无法索引数据。"

            # Check modules list
            modules = await r.module_list()
            
            has_search = False
            module_names = []
            
            for mod in modules:
                name = mod.get('name')
                if isinstance(name, bytes):
                    name = name.decode()
                module_names.append(name)
                
                if name == 'search' or name == 'ft' or name == 'RediSearch':
                    has_search = True
            
            if has_search:
                return {
                    "supported": True, 
                    "modules": module_names,
                    "db_warning": db_warning,
                    "message": "✅ Redis Stack (RediSearch) detected"
                }
            else:
                return {
                    "supported": False, 
                    "modules": module_names,
                    "db_warning": db_warning,
                    "message": "❌ RediSearch module not found. Please use redis/redis-stack image."
                }
                
        except Exception as e:
            return {"supported": False, "error": f"Failed to check modules: {e}"}

    @staticmethod
    async def list_vectors(
        data_source: Optional[str] = None, 
        dataset_id: Optional[int] = None, 
        page: int = 1, 
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List vector data for browsing/debugging"""
        await VectorService.ensure_index()
        
        r = await redis.get_binary_redis()
        if not r:
            return {"total": 0, "items": []}

        try:
            # Build query
            query_parts = []
            if data_source:
                query_parts.append(f"@data_source:{{{data_source}}}")
            if dataset_id:
                query_parts.append(f"@dataset_id:{{{dataset_id}}}")
            
            query = " ".join(query_parts) if query_parts else "*"
            
            offset = (page - 1) * page_size
            
            # Execute search
            # FT.SEARCH index query LIMIT offset num RETURN num field1 ...
            # We want: dataset_id, data_source, type, name, term, updated_at
            # Note: updated_at is in Hash but not in Schema (so not sortable via FT.SEARCH unless updated), but can be returned.
            cmd_args = [
                "FT.SEARCH", VectorService.INDEX_NAME,
                query,
                "LIMIT", str(offset), str(page_size),
                "RETURN", "6", "dataset_id", "data_source", "type", "name", "term", "updated_at"
            ]
            
            # Simple Sort by dataset_id if possible, else default
            # cmd_args.extend(["SORTBY", "dataset_id", "ASC"]) 
            
            res = await r.execute_command(*cmd_args)
            
            if not res or res[0] == 0:
                return {"total": 0, "items": []}
                
            total_count = res[0]
            items = []
            
            for i in range(1, len(res), 2):
                key = res[i]
                fields = res[i+1]
                
                data = {}
                for j in range(0, len(fields), 2):
                    key_name = fields[j].decode() if isinstance(fields[j], bytes) else fields[j]
                    val = fields[j+1]
                    if isinstance(val, bytes):
                        try:
                            val = val.decode()
                        except:
                            pass
                    data[key_name] = val
                    
                items.append({
                    "key": key.decode() if isinstance(key, bytes) else key,
                    **data
                })
                
            return {
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "items": items
            }
            
        except Exception as e:
            logger.error(f"List vectors failed: {e}")
            return {"total": 0, "items": [], "error": str(e)}
        finally:
            await r.close()

    @staticmethod
    async def get_vector_details(key: str) -> Dict[str, Any]:
        """Get full details of a specific vector key"""
        r = await redis.get_binary_redis()
        if not r:
            return {}
        try:
            # Check if key exists
            if not await r.exists(key):
                return {}
                
            data = await r.hgetall(key)
            decoded_data = {}
            for k, v in data.items():
                k_str = k.decode() if isinstance(k, bytes) else k
                if k_str == 'vector':
                    decoded_data[k_str] = "(Binary Vector Data Hidden)"
                else:
                    try:
                        decoded_data[k_str] = v.decode() if isinstance(v, bytes) else v
                    except:
                        decoded_data[k_str] = str(v)
            
            return decoded_data
        except Exception as e:
            logger.error(f"Get vector details failed: {e}")
            return {"error": str(e)}
        finally:
            await r.close()

