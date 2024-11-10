from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import heapq


@dataclass
class Task:
    id: int
    name: str
    priority: int  # 10 (highest) to 1 (lowest)
    due_date: datetime
    duration: float  # in hours
    arrival_time: datetime
    
    def time_until_due(self, current_time: datetime) -> float:
        """Return time until due in hours."""
        return (self.due_date - current_time).total_seconds() / 3600
    
    def can_complete_before_due(self, current_time: datetime) -> bool:
        """Check if task can be completed before its due date."""
        return self.time_until_due(current_time) >= self.duration
    
    def is_overdue(self, current_time: datetime) -> bool:
        """Check if task is already overdue."""
        return self.time_until_due(current_time) < 0


class MultilevelQueue:
    def __init__(
        self,
        priority_weight: float = 0.4,
        urgency_weight: float = 0.4,
        duration_weight: float = 0.2,
        start_time: Optional[datetime] = None
    ):
        if not abs(priority_weight + urgency_weight + duration_weight - 1.0) < 1e-6:
            raise ValueError("Weights must sum to 1.0")
            
        self.queues: Dict[int, list] = {i: [] for i in range(1, 11)}
        self.current_time = start_time or datetime.now()
        self.task_counter = 0
        self.priority_weight = priority_weight
        self.urgency_weight = urgency_weight
        self.duration_weight = duration_weight
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []

    def remove_task(self, task_id: int) -> bool:
        """Remove a task from the queue by task_id."""
        task_found = False

        # Iterate through priority queues to find the task
        for priority in range(1, 11):
            if not self.queues[priority]:
                continue

            # Temporarily store tasks to rebuild the heap
            remaining_tasks = []

            # Remove the specified task from the heap
            while self.queues[priority]:
                score, tid, task = heapq.heappop(self.queues[priority])

                if tid == task_id:
                    task_found = True  # Task found and removed
                else:
                    remaining_tasks.append((score, tid, task))

            # Rebuild the priority queue without the removed task
            for task_tuple in remaining_tasks:
                heapq.heappush(self.queues[priority], task_tuple)

        return task_found

    def calculate_score(self, task: Task) -> float:
        """Calculate comprehensive score for task scheduling."""
        time_until_due = task.time_until_due(self.current_time)
        
        if task.is_overdue(self.current_time):
            return float('inf')  # Overdue tasks get immediate attention
            
        # Normalize priority (higher priority = higher score)
        priority_score = task.priority / 10.0
        
        # Urgency score increases as deadline approaches
        urgency_ratio = task.duration / max(time_until_due, task.duration)
        urgency_score = min(1.0, urgency_ratio)
        
        # Duration score (shorter tasks get higher score)
        duration_score = 1.0 - min(1.0, task.duration / 24.0)
        
        # Weighted combination
        return (
            self.priority_weight * priority_score +
            self.urgency_weight * urgency_score +
            self.duration_weight * duration_score
        )

    def add_task(self, name: str, priority: int, due_date: datetime, duration: float) -> None:
        """Add a new task to the queue."""
        if not 1 <= priority <= 10:
            raise ValueError("Priority must be between 1 and 10")
        if duration <= 0:
            raise ValueError("Duration must be positive")
        if due_date < self.current_time:
            raise ValueError("Due date cannot be in the past")

        self.task_counter += 1
        task = Task(
            id=self.task_counter,
            name=name,
            priority=priority,
            due_date=due_date,
            duration=duration,
            arrival_time=self.current_time
        )
        
        score = self.calculate_score(task)
        heapq.heappush(self.queues[priority], (-score, task.id, task))  # Negative score for max-heap

    def get_next_task_batch(self) -> List[Task]:
        """Get a batch of tasks that have similar or same due times."""
        batch_tasks = []
        best_task = None
        best_score = float('-inf')
        best_priority = None
        
        # Find the task with the highest score across all priority levels
        for priority in range(10, 0, -1):
            if not self.queues[priority]:
                continue
                
            # Recalculate score for the top task in this priority level
            score, task_id, task = self.queues[priority][0]
            current_score = -self.calculate_score(task)  # Negative because we store as min-heap
            
            if current_score > best_score:
                best_score = current_score
                best_task = task
                best_priority = priority
        
        if best_task:
            due_time = best_task.due_date
            # Collect tasks with the same or close due time
            for priority in range(10, 0, -1):
                while self.queues[priority] and self.queues[priority][0][2].due_date <= due_time:
                    _, _, task = heapq.heappop(self.queues[priority])
                    batch_tasks.append(task)
        
        return batch_tasks

    def execute_tasks(self) -> Tuple[List[Task], List[Task]]:
        """Execute all tasks and return a tuple of (completed_tasks, failed_tasks)."""
        while True:
            batch_tasks = self.get_next_task_batch()
            if not batch_tasks:
                break

            # Sort tasks by priority (highest priority first) and then by due date
            batch_tasks.sort(key=lambda task: (-task.priority, task.due_date))

            task_completed = False
            for task in batch_tasks:
                # Check if the task can be completed before the due date based on current_time
                if task.can_complete_before_due(self.current_time):
                    # Update the start and end times based on the current time and duration
                    task.arrival_time = self.current_time
                    task.due_date = self.current_time + timedelta(hours=task.duration)

                    # Mark task as completed
                    self.completed_tasks.append(task)

                    # Move `current_time` forward by task's duration
                    self.current_time += timedelta(hours=task.duration)
                    task_completed = True
                    break
                else:
                    # If task cannot be completed on time, mark it as failed
                    self.failed_tasks.append(task)

            if not task_completed:
                # If no task in the batch can be completed on time, stop execution
                break

            # Recalculate scores to reprioritize remaining tasks based on updated current_time
            self._update_queue_scores()

        return self.completed_tasks, self.failed_tasks

    def _update_queue_scores(self) -> None:
        """Update scores for all tasks in all queues."""
        for priority in range(1, 11):
            if not self.queues[priority]:
                continue
                
            tasks = []
            while self.queues[priority]:
                _, _, task = heapq.heappop(self.queues[priority])
                score = self.calculate_score(task)
                tasks.append((-score, task.id, task))
                
            for task_tuple in tasks:
                heapq.heappush(self.queues[priority], task_tuple)


# Example usage
if __name__ == "__main__":
    scheduler = MultilevelQueue()
    now = datetime.now()

    # Example tasks
    test_tasks = [
        {
            "name": "High Priority, Later Due Date",
            "priority": 10,
            "due_date": now + timedelta(hours=48),
            "duration": 8
        },
        {
            "name": "Medium Priority, Urgent",
            "priority": 5,
            "due_date": now + timedelta(hours=4),
            "duration": 2
        },
        {
            "name": "Low Priority, Very Urgent",
            "priority": 2,
            "due_date": now + timedelta(hours=2),
            "duration": 1
        },
        {
            "name": "High Priority, Urgent",
            "priority": 9,
            "due_date": now + timedelta(hours=6),
            "duration": 3
        }
    ]
