"""
Task Queue for Psi4 MCP Server.

Manages queued calculations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from queue import Queue, PriorityQueue
import threading
import uuid


class TaskStatus(str, Enum):
    """Status of a task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """A queued task."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    priority: int = 5
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other: "Task") -> bool:
        return self.priority < other.priority


class TaskQueue:
    """Queue for managing calculation tasks."""
    
    def __init__(self, max_concurrent: int = 1):
        self._queue: PriorityQueue[Task] = PriorityQueue()
        self._tasks: Dict[str, Task] = {}
        self._max_concurrent = max_concurrent
        self._running = 0
        self._lock = threading.Lock()
    
    def submit(self, name: str = "", priority: int = 5, **metadata: Any) -> Task:
        """Submit a new task."""
        task = Task(name=name, priority=priority, metadata=metadata)
        with self._lock:
            self._queue.put(task)
            self._tasks[task.id] = task
        return task
    
    def get_next(self) -> Optional[Task]:
        """Get next task to execute."""
        with self._lock:
            if self._running >= self._max_concurrent:
                return None
            if self._queue.empty():
                return None
            task = self._queue.get_nowait()
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            self._running += 1
            return task
    
    def complete(self, task_id: str, result: Any = None) -> None:
        """Mark task as completed."""
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = result
                self._running = max(0, self._running - 1)
    
    def fail(self, task_id: str, error: str) -> None:
        """Mark task as failed."""
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                task.error = error
                self._running = max(0, self._running - 1)
    
    def cancel(self, task_id: str) -> bool:
        """Cancel a pending task."""
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.CANCELLED
                    return True
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self._tasks.get(task_id)
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """List tasks, optionally filtered by status."""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)
    
    def clear_completed(self) -> int:
        """Remove completed tasks."""
        with self._lock:
            to_remove = [tid for tid, t in self._tasks.items() 
                        if t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)]
            for tid in to_remove:
                del self._tasks[tid]
            return len(to_remove)
    
    @property
    def pending_count(self) -> int:
        return sum(1 for t in self._tasks.values() if t.status == TaskStatus.PENDING)
    
    @property
    def running_count(self) -> int:
        return self._running
