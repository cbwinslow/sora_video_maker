"""
Batch Processing Manager

This tool manages batch processing of videos with queue management and scheduling.
"""

import asyncio
import logging
import json
import os
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchTask:
    """Represents a single task in the batch"""
    id: str
    task_type: str
    data: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    result: Optional[Dict] = None
    retry_count: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        d = asdict(self)
        d['status'] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'BatchTask':
        """Create from dictionary"""
        data['status'] = TaskStatus(data['status'])
        return cls(**data)


class BatchProcessor:
    """Manage batch processing of tasks"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.queue: List[BatchTask] = []
        self.running_tasks: Dict[str, BatchTask] = {}
        self.completed_tasks: List[BatchTask] = []
        self.failed_tasks: List[BatchTask] = []

        # Configuration
        self.max_concurrent = self.config.get('max_concurrent', 3)
        self.max_retries = self.config.get('max_retries', 2)
        self.retry_delay = self.config.get('retry_delay', 5.0)
        self.save_state = self.config.get('save_state', True)
        self.state_file = self.config.get('state_file', 'batch_state.json')

        # Task handlers
        self.task_handlers: Dict[str, Callable] = {}

        # Load saved state if available
        if self.save_state and os.path.exists(self.state_file):
            self.load_state()

    def register_handler(self, task_type: str, handler: Callable):
        """
        Register a handler for a task type

        Args:
            task_type: Type of task
            handler: Async function to handle the task
        """
        self.task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")

    def add_task(self, task_type: str, data: Dict, priority: int = 0) -> str:
        """
        Add a task to the queue

        Args:
            task_type: Type of task
            data: Task data
            priority: Task priority (higher = more important)

        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task = BatchTask(
            id=task_id,
            task_type=task_type,
            data=data,
            priority=priority
        )

        self.queue.append(task)
        self._sort_queue()

        logger.info(f"Added task {task_id} of type {task_type} (priority: {priority})")

        if self.save_state:
            self._save_state()

        return task_id

    def add_tasks_bulk(self, tasks: List[Dict]) -> List[str]:
        """
        Add multiple tasks at once

        Args:
            tasks: List of task dictionaries with 'task_type', 'data', and optional 'priority'

        Returns:
            List of task IDs
        """
        task_ids = []

        for task_spec in tasks:
            task_id = self.add_task(
                task_spec['task_type'],
                task_spec['data'],
                task_spec.get('priority', 0)
            )
            task_ids.append(task_id)

        logger.info(f"Added {len(task_ids)} tasks in bulk")
        return task_ids

    def _sort_queue(self):
        """Sort queue by priority (higher first)"""
        self.queue.sort(key=lambda t: t.priority, reverse=True)

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """
        Get status of a specific task

        Args:
            task_id: Task ID

        Returns:
            Task status dictionary or None
        """
        # Check all lists
        for task_list in [self.queue, list(self.running_tasks.values()),
                         self.completed_tasks, self.failed_tasks]:
            for task in task_list:
                if task.id == task_id:
                    return task.to_dict()

        return None

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending task

        Args:
            task_id: Task ID

        Returns:
            True if cancelled, False otherwise
        """
        for i, task in enumerate(self.queue):
            if task.id == task_id:
                task.status = TaskStatus.CANCELLED
                self.queue.pop(i)
                self.failed_tasks.append(task)
                logger.info(f"Cancelled task {task_id}")
                return True

        logger.warning(f"Cannot cancel task {task_id} - not in queue")
        return False

    async def _execute_task(self, task: BatchTask) -> bool:
        """
        Execute a single task

        Args:
            task: Task to execute

        Returns:
            True if successful, False otherwise
        """
        if task.task_type not in self.task_handlers:
            logger.error(f"No handler for task type: {task.task_type}")
            task.error = f"No handler for task type: {task.task_type}"
            return False

        handler = self.task_handlers[task.task_type]

        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now().isoformat()

            logger.info(f"Executing task {task.id} ({task.task_type})")

            # Execute handler
            result = await handler(task.data)

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()

            logger.info(f"Task {task.id} completed successfully")
            return True

        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            task.error = str(e)
            task.status = TaskStatus.FAILED
            return False

    async def _process_task(self, task: BatchTask):
        """
        Process a task with retry logic

        Args:
            task: Task to process
        """
        self.running_tasks[task.id] = task

        try:
            success = await self._execute_task(task)

            # Retry logic
            while not success and task.retry_count < self.max_retries:
                task.retry_count += 1
                logger.info(f"Retrying task {task.id} (attempt {task.retry_count}/{self.max_retries})")

                await asyncio.sleep(self.retry_delay)
                success = await self._execute_task(task)

            # Move to appropriate list
            if success:
                self.completed_tasks.append(task)
            else:
                self.failed_tasks.append(task)

        finally:
            # Remove from running
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]

            if self.save_state:
                self._save_state()

    async def process_queue(self):
        """Process all tasks in the queue"""
        logger.info(f"Starting batch processing ({len(self.queue)} tasks in queue)")

        while self.queue or self.running_tasks:
            # Start new tasks up to max concurrent
            while len(self.running_tasks) < self.max_concurrent and self.queue:
                task = self.queue.pop(0)
                asyncio.create_task(self._process_task(task))

            # Wait a bit before checking again
            await asyncio.sleep(0.5)

        logger.info("Batch processing complete")
        self._print_summary()

    def get_queue_status(self) -> Dict:
        """
        Get overall queue status

        Returns:
            Dictionary with queue statistics
        """
        return {
            'pending': len(self.queue),
            'running': len(self.running_tasks),
            'completed': len(self.completed_tasks),
            'failed': len(self.failed_tasks),
            'total': len(self.queue) + len(self.running_tasks) +
                    len(self.completed_tasks) + len(self.failed_tasks)
        }

    def _print_summary(self):
        """Print processing summary"""
        status = self.get_queue_status()

        print("\n" + "=" * 50)
        print("BATCH PROCESSING SUMMARY")
        print("=" * 50)
        print(f"Total Tasks: {status['total']}")
        print(f"Completed: {status['completed']}")
        print(f"Failed: {status['failed']}")
        print(f"Success Rate: {status['completed'] / status['total'] * 100:.1f}%" if status['total'] > 0 else "N/A")
        print("=" * 50)

    def _save_state(self):
        """Save current state to file"""
        try:
            state = {
                'queue': [task.to_dict() for task in self.queue],
                'running': [task.to_dict() for task in self.running_tasks.values()],
                'completed': [task.to_dict() for task in self.completed_tasks],
                'failed': [task.to_dict() for task in self.failed_tasks],
                'saved_at': datetime.now().isoformat()
            }

            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def load_state(self):
        """Load state from file"""
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            self.queue = [BatchTask.from_dict(t) for t in state.get('queue', [])]
            self.completed_tasks = [BatchTask.from_dict(t) for t in state.get('completed', [])]
            self.failed_tasks = [BatchTask.from_dict(t) for t in state.get('failed', [])]

            logger.info(f"Loaded state from {self.state_file}")
            logger.info(f"Restored {len(self.queue)} pending tasks")

        except Exception as e:
            logger.error(f"Error loading state: {e}")

    def clear_completed(self):
        """Clear completed tasks from memory"""
        count = len(self.completed_tasks)
        self.completed_tasks.clear()
        logger.info(f"Cleared {count} completed tasks")

        if self.save_state:
            self._save_state()

    def export_results(self, output_file: str):
        """
        Export results to JSON file

        Args:
            output_file: Output file path
        """
        try:
            results = {
                'completed': [task.to_dict() for task in self.completed_tasks],
                'failed': [task.to_dict() for task in self.failed_tasks],
                'statistics': self.get_queue_status(),
                'exported_at': datetime.now().isoformat()
            }

            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

            logger.info(f"Results exported to {output_file}")

        except Exception as e:
            logger.error(f"Error exporting results: {e}")


async def main():
    """Example usage"""

    # Create batch processor
    processor = BatchProcessor({
        'max_concurrent': 2,
        'max_retries': 2,
        'save_state': False
    })

    # Define task handlers
    async def generate_video_handler(data: Dict) -> Dict:
        """Simulate video generation"""
        await asyncio.sleep(1)  # Simulate work
        return {
            'video_path': f"/output/video_{data['topic_id']}.mp4",
            'duration': 60
        }

    async def upload_video_handler(data: Dict) -> Dict:
        """Simulate video upload"""
        await asyncio.sleep(0.5)
        return {
            'url': f"https://platform.com/{data['video_id']}",
            'views': 0
        }

    # Register handlers
    processor.register_handler('generate_video', generate_video_handler)
    processor.register_handler('upload_video', upload_video_handler)

    # Add tasks
    print("Adding tasks to queue...")

    for i in range(5):
        processor.add_task('generate_video', {
            'topic_id': i,
            'title': f'Video {i}'
        }, priority=i)

    for i in range(3):
        processor.add_task('upload_video', {
            'video_id': i,
            'platform': 'youtube'
        })

    # Process queue
    await processor.process_queue()

    # Export results
    processor.export_results('batch_results.json')


if __name__ == '__main__':
    asyncio.run(main())
