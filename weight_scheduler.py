from datetime import datetime, timedelta

# Define a Task class to store priority, due date, and duration for each task
class Task:
    def __init__(self, name, priority, due_date, duration):
        self.name = name
        self.priority = priority
        self.due_date = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
        self.duration = duration  # Duration in hours

    def __repr__(self):
        return f"{self.name} (Priority: {self.priority}, Due: {self.due_date}, Duration: {self.duration} hours)"

# Function to calculate a score for each task based on priority, due date, and duration
def calculate_score(task, current_time):
    hours_until_due = (task.due_date - current_time).total_seconds() / 3600  # Convert to hours
    # If the task can't be completed on time, return a very low score
    if hours_until_due < task.duration:
        return -float('inf')
    # Score formula balancing priority, hours left until due, and duration
    return task.priority / (hours_until_due * task.duration)

# Function to schedule tasks based on priority, due date, and duration
def schedule_tasks(tasks, start_time):
    # Sort tasks initially by due date
    tasks.sort(key=lambda x: x.due_date)
    schedule = []
    current_time = start_time

    while tasks:
        # Filter tasks that can still be completed by their due date
        available_tasks = [task for task in tasks if (task.due_date - current_time).total_seconds() / 3600 >= task.duration]
        if not available_tasks:
            break  # No more tasks can be completed on time

        # Calculate scores and choose the task with the highest score
        task_scores = [(task, calculate_score(task, current_time)) for task in available_tasks]
        best_task = max(task_scores, key=lambda x: x[1])[0]

        # Schedule the task and update current time
        schedule.append(best_task)
        current_time += timedelta(hours=best_task.duration)

        # Remove the scheduled task from the list
        tasks.remove(best_task)

    return schedule

def test_schedule_tasks():
    # Test Case 1: Standard Test Case
    tasks_1 = [
        Task("Assignment - Math 101", 7, "2024-11-18 10:00:00", 4),  # Duration: 4 hours
        Task("Project - Computer Science", 7, "2024-11-19 15:30:00", 10),  # Duration: 10 hours
        Task("Essay - Sociology", 7, "2024-11-20 09:00:00", 6),  # Duration: 6 hours
    ]
    start_time_1 = datetime(2024, 11, 10, 8, 30, 0)
    print("Test Case 1: Standard Test Case")
    scheduled_tasks_1 = schedule_tasks(tasks_1, start_time_1)
    for task in scheduled_tasks_1:
        print(f"{task}\n")

    # Test Case 2: Not Enough Time Test Case (with hours)
    tasks_2 = [
        Task("Assignment - Math 101", 7, "2024-11-10 10:00:00", 12),  # Duration: 12 hours
        Task("Project - Computer Science", 7, "2024-11-10 15:30:00", 12),  # Duration: 12 hours
        Task("Essay - Sociology", 7, "2024-11-18 18:00:00", 10),  # Duration: 10 hours
    ]
    start_time_2 = datetime(2024, 11, 10, 8, 30, 0)  # 8 days from start time
    print("\nTest Case 2: Not Enough Time Test Case")
    scheduled_tasks_2 = schedule_tasks(tasks_2, start_time_2)
    if not scheduled_tasks_2:
        print("Not enough time to complete all tasks.\n")
    else:
        for task in scheduled_tasks_2:
            print(f"{task}\n")

    # Test Case 3: Tasks with Same Due Date
    tasks_3 = [
        Task("Assignment - Math 101", 7, "2024-11-18 10:00:00", 4),  # Duration: 4 hours
        Task("Project - Computer Science", 7, "2024-11-18 10:00:00", 2),  # Duration: 2 hours
        Task("Essay - Sociology", 7, "2024-11-18 10:00:00", 6),  # Duration: 6 hours
    ]
    start_time_3 = datetime(2024, 11, 10, 8, 30, 0)
    print("\nTest Case 3: Tasks with Same Due Date")
    scheduled_tasks_3 = schedule_tasks(tasks_3, start_time_3)
    for task in scheduled_tasks_3:
        print(f"{task}\n")

    # Test Case 4: Tasks that Can Be Completed in the Available Time
    tasks_4 = [
        Task("Assignment - Math 101", 7, "2024-11-18 10:00:00", 4),  # Duration: 4 hours
        Task("Project - Computer Science", 7, "2024-11-18 18:00:00", 4),  # Duration: 4 hours
        Task("Essay - Sociology", 7, "2024-11-19 09:00:00", 4),  # Duration: 4 hours
    ]
    start_time_4 = datetime(2024, 11, 10, 8, 30, 0)  # 8 days from start time
    print("\nTest Case 4: Tasks that Can Be Completed in the Available Time")
    scheduled_tasks_4 = schedule_tasks(tasks_4, start_time_4)
    for task in scheduled_tasks_4:
        print(f"{task}\n")

if __name__ == '__main__':
    test_schedule_tasks()


'''
if __name__ == '__main__':
    # Accept exact timestamps as inputs for the tasks (duration in hours)
    tasks = [
        Task("Assignment - Math 101", 7, "2024-11-18 10:00:00", 4),  # Duration in hours
        Task("Project - Computer Science", 7, "2024-11-19 15:30:00", 10),  # Duration in hours
        Task("Essay - Sociology", 7, "2024-11-20 09:00:00", 6),  # Duration in hours
    ]

    # Define the starting time with exact timestamp for scheduling
    start_time = datetime(2024, 11, 10, 8, 30, 0)  # Exact timestamp for the start time

    # Get the scheduled order of tasks
    scheduled_tasks = schedule_tasks(tasks, start_time)

    # Display the scheduled tasks
    print("Scheduled Task Order:")
    for task in scheduled_tasks:
        print(f"{task}\n")
'''