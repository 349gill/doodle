from collections import deque

class Task:
    def __init__(self, id, name, priority, burst_time, deadline):
        self.id = id
        self.name = name
        self.priority = priority  # 0 = highest priority
        self.burst_time = burst_time  # Hours required
        self.deadline = deadline

class MultiLevelQueueScheduler:
    def __init__(self, num_queues):
        self.queues = [deque() for _ in range(num_queues)]  # Create queues for each priority level

    def add_task(self, task):
        self.queues[task.priority].append(task)


    def empty_queues(self):
        for queue in self.queues:
            if len(queue) != 0:
                return False
            
        return True


    def execute(self):
        while not self.empty_queues():
            pass

        # for priority_level, queue in enumerate(self.queues):
        #     while queue:
        #         task = queue.popleft()
        #         print(f"Executing {task.name} from Priority {priority_level} queue.")
        #         print(f"Task {task.name} with Burst Time {task.burst_time} is completed.\n")

# Example Usage
if __name__ == "__main__":
    # Create a scheduler with 3 priority levels (0 = highest, 2 = lowest)
    scheduler = MultiLevelQueueScheduler(num_queues=3)

    # Add some tasks to the scheduler
    scheduler.add_task(Task(1, "Task A", 0, 5))  # High-priority task
    scheduler.add_task(Task(2, "Task B", 1, 3))  # Medium-priority task
    scheduler.add_task(Task(3, "Task C", 2, 8))  # Low-priority task
    scheduler.add_task(Task(4, "Task D", 0, 2))  # High-priority task

    # Execute tasks based on the multi-level queue scheduling algorithm
    scheduler.execute()
