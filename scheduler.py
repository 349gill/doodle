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
        return (self.due_date - current_time).total_seconds() / 3600
    
    def can_complete_before_due(self, current_time: datetime) -> bool:
        return self.time_until_due(current_time) >= self.duration
    
    def is_overdue(self, current_time: datetime) -> bool:
        return self.time_until_due(current_time) < 0


class MultilevelQueue:
    def __init__(
        self,
        priority_weight: float = 0.4,
        urgency_weight: float = 0.4,
        duration_weight: float = 0.2,
        start_time: Optional[datetime] = None):

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
        task_found = False

        for priority in range(1, 11):
            if not self.queues[priority]:
                continue

            remaining_tasks = []
            while self.queues[priority]:
                score, tid, task = heapq.heappop(self.queues[priority])

                if tid == task_id: task_found = True
                else: remaining_tasks.append((score, tid, task))

            for task_tuple in remaining_tasks:
                heapq.heappush(self.queues[priority], task_tuple)

        return task_found

    def calculate_score(self, task: Task) -> float:
        time_until_due = task.time_until_due(self.current_time)
        
        if task.is_overdue(self.current_time):
            return float('inf')

        priority_score = task.priority / 10.0
        urgency_ratio = task.duration / max(time_until_due, task.duration)
        urgency_score = min(1.0, urgency_ratio)

        duration_score = 1.0 - min(1.0, task.duration / 24.0)
        return (
            self.priority_weight * priority_score +
            self.urgency_weight * urgency_score +
            self.duration_weight * duration_score
        )

    def add_task(self, name: str, priority: int, due_date: datetime, duration: float) -> None:
        if not 1 <= priority <= 10: raise ValueError("Priority must be between 1 and 10")
        if duration <= 0: raise ValueError("Duration must be positive")
        if due_date < self.current_time: raise ValueError("Due date cannot be in the past")

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
        batch_tasks = []
        best_task = None
        best_score = float('-inf')
        best_priority = None

        for priority in range(10, 0, -1):
            if not self.queues[priority]:
                continue

            score, task_id, task = self.queues[priority][0]
            current_score = -self.calculate_score(task)
            
            if current_score > best_score:
                best_score = current_score
                best_task = task
                best_priority = priority
        
        if best_task:
            due_time = best_task.due_date
            for priority in range(10, 0, -1):
                while self.queues[priority] and self.queues[priority][0][2].due_date <= due_time:
                    _, _, task = heapq.heappop(self.queues[priority])
                    batch_tasks.append(task)
        
        return batch_tasks

    def execute_tasks(self) -> Tuple[List[Task], List[Task]]:
        while True:
            batch_tasks = self.get_next_task_batch()
            if not batch_tasks: break

            batch_tasks.sort(key=lambda task: (-task.priority, task.due_date))

            task_completed = False
            for task in batch_tasks:
                if task.can_complete_before_due(self.current_time):
                    task.arrival_time = self.current_time
                    task.due_date = self.current_time + timedelta(hours=task.duration)

                    self.completed_tasks.append(task)

                    self.current_time += timedelta(hours=task.duration)
                    task_completed = True
                    break
                else:
                    self.failed_tasks.append(task)

            if not task_completed: break
            self._update_queue_scores()

        return self.completed_tasks, self.failed_tasks

    def _update_queue_scores(self) -> None:
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