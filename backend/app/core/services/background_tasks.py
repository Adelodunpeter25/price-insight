"""Background task queue for non-blocking operations."""

import asyncio
import logging
from typing import Callable, Any
from collections import deque

logger = logging.getLogger(__name__)


class BackgroundTaskQueue:
    """Simple background task queue using asyncio."""

    def __init__(self, max_concurrent: int = 5):
        """Initialize background task queue."""
        self.max_concurrent = max_concurrent
        self.queue = deque()
        self.running_tasks = set()
        self.is_processing = False

    def add_task(self, coro: Callable, *args, **kwargs):
        """Add task to queue without blocking."""
        self.queue.append((coro, args, kwargs))
        
        # Start processing if not already running
        if not self.is_processing:
            asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        """Process tasks from queue with concurrency limit."""
        if self.is_processing:
            return
        
        self.is_processing = True
        
        try:
            while self.queue or self.running_tasks:
                # Start new tasks up to max_concurrent
                while len(self.running_tasks) < self.max_concurrent and self.queue:
                    coro, args, kwargs = self.queue.popleft()
                    task = asyncio.create_task(self._run_task(coro, args, kwargs))
                    self.running_tasks.add(task)
                
                # Wait for at least one task to complete
                if self.running_tasks:
                    done, pending = await asyncio.wait(
                        self.running_tasks,
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    self.running_tasks = pending
                
                # Small delay to prevent tight loop
                await asyncio.sleep(0.1)
        
        finally:
            self.is_processing = False

    async def _run_task(self, coro: Callable, args: tuple, kwargs: dict):
        """Run a single task with error handling."""
        try:
            await coro(*args, **kwargs)
        except Exception as e:
            logger.error(f"Background task failed: {e}")


# Global task queue instance
background_tasks = BackgroundTaskQueue(max_concurrent=5)
