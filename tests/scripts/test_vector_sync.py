import sys
import os
import asyncio
import logging
from unittest.mock import patch, AsyncMock

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.services.vector_service import VectorService
from app.core import redis
from app.core import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_test():
    logger.info("🚀 Starting Vector Sync Test Script...")

    # Mock Data
    dataset_id = 99999
    fake_dataset = {
        "id": dataset_id,
        "name": "test_ds",
        "display_name": "Test Dataset",
        "data_source": "api_data",
        "updated_at": "2023-01-01 12:00:00",
        "tables": [
            {"id": 101, "physical_name": "tbl_user", "term": "用户表", "description": "User info", "columns": []},
            {"id": 102, "physical_name": "tbl_order", "term": "订单表", "description": "Order info", "columns": []}
        ],
        "metrics": [
            {"id": 201, "name": "gmv", "display_name": "GMV", "calculation_logic": "sum(amount)", "description": "Gross Merchandise Value"}
        ]
    }
    
    # Mock Yaml Fragments
    fake_yaml_table = "entity:\n  name: tbl_user\n"
    fake_yaml_metric = "metric:\n  name: gmv\n"

    # 1024 dimensions float32 (matching bge-m3 / updated VectorService)
    fake_vector = [0.1] * 1024

    # Patch Dependencies
    # We patch the class methods directly
    with patch("app.services.metadata_v2_service.MetadataV2Service.get_dataset_by_id", new_callable=AsyncMock) as mock_get_ds, \
         patch("app.services.metadata_yaml_service.MetadataYamlService.generate_table_yaml", return_value=fake_yaml_table) as mock_yaml_table, \
         patch("app.services.metadata_yaml_service.MetadataYamlService.generate_metric_yaml", return_value=fake_yaml_metric) as mock_yaml_metric, \
         patch("app.services.ai_service.AIService.create_embedding", new_callable=AsyncMock) as mock_embed, \
         patch("app.services.metadata_v2_service.MetadataV2Service.update_dataset", new_callable=AsyncMock) as mock_update:

        # Setup Mocks
        mock_get_ds.return_value = fake_dataset
        mock_embed.return_value = fake_vector
        mock_update.return_value = None

        # Initialize Real Redis
        # Ensure we use a test DB if possible, or just be careful with keys
        # The app uses settings.REDIS_DB, usually 0. 
        # VectorService uses a specific key pattern, so collision risk is low if we use a unique ID.
        try:
            await redis.init_redis()
            # Use binary client for verification
            import redis.asyncio as aioredis
            binary_r = aioredis.Redis(
                host=config.settings.REDIS_HOST,
                port=config.settings.REDIS_PORT,
                db=config.settings.REDIS_DB,
                password=config.settings.REDIS_PASSWORD if config.settings.REDIS_PASSWORD and config.settings.REDIS_PASSWORD.strip() not in ["", "None", "null"] else None,
                decode_responses=False
            )
            
            # Clean previous test keys (Granular)
            # We can't easily scan without keys pattern, but we know the IDs
            await binary_r.delete(f"metadata:vec:table:101")
            await binary_r.delete(f"metadata:vec:table:102")
            await binary_r.delete(f"metadata:vec:metric:201")
            
            # Drop index to ensure schema update
            try:
                await binary_r.execute_command("FT.DROPINDEX", VectorService.INDEX_NAME)
                logger.info(f"🗑️ Dropped index {VectorService.INDEX_NAME} for schema refresh")
            except:
                pass

            # Run Sync
            logger.info(f"🧪 Testing sync_dataset({dataset_id})...")
            await VectorService.sync_dataset(dataset_id)

            # Verify Redis Data
            logger.info("🔍 Verifying Redis data...")
            
            # Check Table Key
            table_key = "metadata:vec:table:101"
            if await binary_r.exists(table_key):
                data = await binary_r.hgetall(table_key)
                logger.info(f"✅ Table Key found! Type: {data.get(b'type')}")
            else:
                logger.error(f"❌ Table Key {table_key} not found!")

            # Check Metric Key
            metric_key = "metadata:vec:metric:201"
            if await binary_r.exists(metric_key):
                data = await binary_r.hgetall(metric_key)
                logger.info(f"✅ Metric Key found! Type: {data.get(b'type')}")
            else:
                logger.error(f"❌ Metric Key {metric_key} not found!")

            # Verify DB Update Call
            mock_update.assert_called()
            args = mock_update.call_args[0] # (dataset_id, data)
            update_data = args[1]
            logger.info(f"✅ Database update called with: {update_data}")
            
            if update_data.get('vector_status') == 1:
                logger.info("🎉 Test PASSED: Status updated to 1 (Synced)")
            else:
                logger.error(f"❌ Test FAILED: Status updated to {update_data.get('vector_status')}")

            # Run Semantic Search Test
            logger.info("🧪 Testing semantic_search()...")
            # We need to wait a bit for indexing? usually instant for small data
            import time
            await asyncio.sleep(0.5)
            
            search_results = await VectorService.semantic_search("api_data", "test query")
            if search_results:
                logger.info(f"✅ Semantic search returned {len(search_results)} results")
                logger.info(f"✅ Match: {search_results[0]}")
            else:
                logger.error("❌ Semantic search returned 0 results!")

        except Exception as e:
            logger.error(f"❌ Test Exception: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await redis.close_redis()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_test())
