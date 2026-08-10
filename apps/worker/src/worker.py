import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cx-worker")


async def run_worker() -> None:
    logger.info("Starting CX Import Worker loop...")
    while True:
        # Worker polling loop harness
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_worker())
