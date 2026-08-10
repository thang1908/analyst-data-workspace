import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cx-worker")


from apps.worker.src.modules.imports import process_queued_import_jobs

async def run_worker() -> None:
    logger.info("Starting CX Import Worker loop...")
    while True:
        try:
            await process_queued_import_jobs()
        except Exception as e:
            logger.error(f"Error in worker loop iteration: {e}")
        await asyncio.sleep(5)



if __name__ == "__main__":
    asyncio.run(run_worker())
