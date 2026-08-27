import os
import redis
from rq import Worker, Queue, Connection
from app.core.config import settings
from app.db.base import SessionLocal
from app.agents.langgraph_graph import app_graph
import asyncio
from app.api.v1 import schemas

listen = ['default']

def process_log_job(log_data):
    """
    Job to be executed by RQ worker.
    """
    print(f"Worker processing log: {log_data}")
    # Run the graph
    # Since graph is async, we need to run it in event loop
    inputs = {"log_entry": log_data, "next": "ops_monitor"}
    
    # Simple async wrapper
    async def run():
        await app_graph.ainvoke(inputs)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())
    loop.close()

if __name__ == '__main__':
    conn = redis.from_url(settings.REDIS_URL or 'redis://localhost:6379/0')
    with Connection(conn):
        print(f"Worker initiated. Settings: {settings.REDIS_URL}")
        worker = Worker(map(Queue, listen))
        worker.work()
