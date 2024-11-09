from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Tuple
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
        """Return time until due in hours"""
        return (self.due_date - current_time).total_seconds() / 3600  # Convert to hours

    def can_complete_before_due(self, current_time: datetime) -> bool:
        """Check if task can be completed before its due date"""
        return self.time_until_due(current_time) >= self.duration


class MultilevelQueue:
    def __init__(self,
                 priority_weight: float = 0.4,
                 urgency_weight: float = 0.4,
                 duration_weight: float = 0.2):
        self.queues: Dict[int, list] = {i: [] for i in range(1, 11)}
        self.current_time = datetime.now()
        self.task_counter = 0
        self.priority_weight = priority_weight
        self.urgency_weight = urgency_weight
        self.duration_weight = duration_weight

    def calculate_urgency_score(self, task: Task) -> Tuple[float, bool]:
        """
        Calculate urgency score considering multiple factors.
        Returns tuple of (score, is_critical)
        """
        time_until_due = task.time_until_due(self.current_time)

        # Critical flag for tasks that must be started now to meet deadline
        is_critical = time_until_due <= task.duration * 1.1  # 10% buffer

        if time_until_due <= 0:
            return (-1000 - task.priority, True)

        # Normalize each factor to 0-1 range
        priority_factor = (11 - task.priority) / 10

        # Urgency factor based on due date vs duration
        urgency_factor = min(1.0, task.duration / time_until_due)

        # Duration factor (shorter tasks get priority)
        duration_factor = min(1.0, task.duration / 24)  # Normalize against 24 hours

        score = (
                self.priority_weight * (1 - priority_factor) +
                self.urgency_weight * (1 - urgency_factor) +
                self.duration_weight * duration_factor
        )

        return (score, is_critical)

    def add_task(self, name: str, priority: int, due_date: datetime, duration: float) -> None:
        """Add a new task with priority (10 highest, 1 lowest) and duration in hours"""
        if not 1 <= priority <= 10:
            raise ValueError("Priority must be between 1 and 10")

        self.task_counter += 1
        task = Task(
            id=self.task_counter,
            name=name,
            priority=priority,
            due_date=due_date,
            duration=duration,
            arrival_time=self.current_time
        )

        urgency_score, is_critical = self.calculate_urgency_score(task)
        heapq.heappush(self.queues[priority], (urgency_score, is_critical, task))

    def get_next_task(self) -> Task:
        """Get next task based on dynamic priority and urgency"""
        critical_task = self._find_critical_task()
        if critical_task:
            return critical_task

        for priority in range(10, 0, -1):
            if self.queues[priority]:
                return heapq.heappop(self.queues[priority])[2]
        return None

    def _find_critical_task(self) -> Task:
        """Find the most urgent critical task across all priority levels"""
        critical_tasks = []

        for priority in range(10, 0, -1):
            while self.queues[priority] and self.queues[priority][0][1]:
                score, _, task = heapq.heappop(self.queues[priority])
                critical_tasks.append((score, task))

        if not critical_tasks:
            return None

        most_urgent = min(critical_tasks, key=lambda x: x[0])

        for score, task in critical_tasks:
            if task != most_urgent[1]:
                new_score, is_critical = self.calculate_urgency_score(task)
                heapq.heappush(self.queues[task.priority], (new_score, is_critical, task))

        return most_urgent[1]

    def execute_tasks(self) -> List[Task]:
        """Execute all tasks and return execution sequence"""
        execution_sequence = []

        while True:
            task = self.get_next_task()
            if not task:
                break

            execution_sequence.append(task)
            self.current_time += timedelta(hours=task.duration)
            self._recalculate_urgency()

        return execution_sequence

    def _recalculate_urgency(self):
        """Recalculate urgency scores for all remaining tasks"""
        for priority in range(1, 11):
            if not self.queues[priority]:
                continue

            tasks = []
            while self.queues[priority]:
                _, _, task = heapq.heappop(self.queues[priority])
                score, is_critical = self.calculate_urgency_score(task)
                tasks.append((score, is_critical, task))

            for task_tuple in tasks:
                heapq.heappush(self.queues[priority], task_tuple)


# Example usage with hours
if __name__ == "__main__":
    scheduler = MultilevelQueue()
    now = datetime.now()

    # Example tasks with different priorities and time constraints
    test_tasks = [
        {
            "name": "High Priority, Later Due Date",
            "priority": 10,
            "due_date": now + timedelta(hours=48),  # Due in 48 hours
            "duration": 8  # 8 hours task
        },
        {
            "name": "Medium Priority, Urgent",
            "priority": 5,
            "due_date": now + timedelta(hours=4),  # Due in 4 hours
            "duration": 2  # 2 hours task
        },
        {
            "name": "Low Priority, Very Urgent",
            "priority": 2,
            "due_date": now + timedelta(hours=2),  # Due in 2 hours
            "duration": 1  # 1 hour task
        },
        {
            "name": "High Priority, Urgent",
            "priority": 9,
            "due_date": now + timedelta(hours=6),  # Due in 6 hours
            "duration": 3  # 3 hours task
        }
    ]

    # Add all test tasks
    for task in test_tasks:
        scheduler.add_task(
            name=task["name"],
            priority=task["priority"],
            due_date=task["due_date"],
            duration=task["duration"]
        )

    # Execute and display results
    print("\nTask Execution Sequence:")
    execution_sequence = scheduler.execute_tasks()

    for i, task in enumerate(execution_sequence, 1):
        time_until_due = task.time_until_due(task.arrival_time)
        print(f"\nTask {i}:")
        print(f"Name: {task.name}")
        print(
            f"Priority Level: {task.priority} {'(Highest)' if task.priority == 10 else '(Lowest)' if task.priority == 1 else ''}")
        print(f"Duration: {task.duration:.1f} hours")
        print(f"Time Until Due: {time_until_due:.1f} hours")
        print(f"Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"Can Complete Before Due: {'Yes' if task.can_complete_before_due(task.arrival_time) else 'No'}")
        print("-" * 50)