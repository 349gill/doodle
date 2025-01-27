import heapq

class SchedulerTask:
    def __init__(self, id, name, priority, burst_time, deadline):
        self.id = id
        self.name = name
        self.deadline = deadline  # Enumerated into an integer
        self.priority = priority  # 0 = Highest priority
        self.burst_time = burst_time  # Hours required

class MultiLevelQueueScheduler:
    def __init__(self, num_queues):
        self.queues = [[] for _ in range(num_queues)]

    def add_task(self, task):
        if 0 <= task.priority < len(self.queues):
            heapq.heappush(self.queues[task.priority], (task.deadline, task.id, task))
        else:
            raise ValueError(f"Invalid task priority: {task.priority}")


    def empty_queues(self):
        return all(len(queue) == 0 for queue in self.queues)

    def execute(self):
        schedule = []
        while not self.empty_queues():
            closest = None
            closest_queue_index = None

            for i, queue in enumerate(self.queues):
                if queue:
                    top_item = queue[0]
                    if closest is None or top_item[0] < closest[0]:
                        closest = top_item
                        closest_queue_index = i

            if closest_queue_index is not None:
                task = heapq.heappop(self.queues[closest_queue_index])
                schedule.append(task[2])
            else:
                print("Error: No valid queue to pop from.")
                break

        return schedule
