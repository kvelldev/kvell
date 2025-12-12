
import asyncio
import json
from tests.integration.conftest import *

@pytest.mark.asyncio
async def test_debug(test_client, collection):
    from app.domain.model.spark import Spark
    
    # Create spark
    spark = Spark.create(
        spark_id="test-debug",
        content="Test",
        user_hash="author",
        decay_after_seconds=600,
        vanish_after_days=30,
    )
    await collection.insert_one({
        "id": spark.id,
        "content": spark.content,
        "user_hash": spark.user_hash,
        "fuel_count": 0,
        "created_at": spark.created_at,
        "decay_at": spark.decay_at,
        "vanish_at": spark.vanish_at,
    })
    
    # Test
    response = await test_client.post(
        "/api/sparks/test-debug/fuel",
        headers={"X-Forwarded-For": "192.168.1.100"},
    )
    
    print(f"Response status: {response.status_code}")
    if response.status_code \!= 200:
        print(f"Response body: {json.dumps(response.json(), indent=2)}")
