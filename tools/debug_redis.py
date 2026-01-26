
import asyncio
import os
import json
from redis.asyncio import Redis

async def main():
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    print(f"Connecting to Redis at {redis_host}:{redis_port}...")
    redis = Redis(host=redis_host, port=redis_port, decode_responses=True)

    pubsub = redis.pubsub()
    channels = ["sparks:posted", "sparks:updated", "sparks:events"]

    await pubsub.subscribe(*channels)
    print(f"Subscribed to: {channels}")
    print("Waiting for messages... (Ctrl+C to stop)")

    async for message in pubsub.listen():
        if message["type"] == "message":
            print("\n--- Message Received ---")
            print(f"Channel: {message['channel']}")
            try:
                data = json.loads(message["data"])
                print(json.dumps(data, indent=2))
            except:
                print(f"Raw Data: {message['data']}")
        elif message["type"] == "subscribe":
            print(f"Subscribed to {message['channel']}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
