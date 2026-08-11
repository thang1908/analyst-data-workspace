from __future__ import annotations

import asyncio
import logging

from packages.infrastructure.logging import setup_logging

setup_logging()
logger = logging.getLogger("apps.worker")


async def worker_loop() -> None:
    logger.info("Starting CX Background Worker Loop...")
    while True:
        # Background job processing loop placeholder
        await asyncio.sleep(10)


def main() -> None:
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("Worker process stopped cleanly.")


if __name__ == "__main__":
    main()
