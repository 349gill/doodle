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
        heapq.heappush(self.queues[task.priority], (task.deadline, task.id, task))

    def empty_queues(self):
        return all(len(queue) == 0 for queue in self.queues)

    def execute(self):
        schedule = []
        while not self.empty_queues():
            closest = None
            closest_queue_index = None
            
            for i, queue in enumerate(self.queues):
                if len(queue) > 0:
                    if closest is None or queue[0].deadline < closest.deadline:
                        closest = queue[0]
                        closest_queue_index = i
            
            if closest_queue_index is not None:
                task = heapq.heappop(self.queues[closest_queue_index])
                schedule.append(task)

        return schedule