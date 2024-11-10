document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    let currentTaskId = null;

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        eventClick: function(info) {
            showTaskPopup(info.event);
        },
        events: '/api/tasks',  // This loads the tasks from your backend
        eventDataTransform: function(task) {
            return {
                id: task.id,
                title: task.title,
                start: task.start,  // start time of the task
                end: task.end,      // end time of the task
                extendedProps: {
                    priority: task.extendedProps.priority,
                    duration: task.extendedProps.duration,
                    details: task.extendedProps.details || ''
                }
            };
        }
    });

    calendar.render();

    // Function to show the task popup for new tasks
    window.addTaskButton = function() {
        currentTaskId = null;
        document.querySelector('.task-popup h3').textContent = 'Add Task';
        document.querySelector('.remove-btn').style.display = 'none';
        document.getElementById('task-name').value = '';
        document.getElementById('task-deadline').value = '';
        document.getElementById('task-priority').value = '';
        document.getElementById('task-duration').value = '';
        document.getElementById('task-details').value = '';
        showPopup();
    };

    // Function to show the task popup for existing tasks
    function showTaskPopup(event) {
        currentTaskId = event.id;
        document.querySelector('.task-popup h3').textContent = 'Edit Task';
        document.querySelector('.remove-btn').style.display = 'block';
        document.getElementById('task-name').value = event.title;
        document.getElementById('task-deadline').value = moment(event.end).format('YYYY-MM-DDTHH:mm');
        document.getElementById('task-priority').value = event.extendedProps.priority;
        document.getElementById('task-duration').value = event.extendedProps.duration;
        document.getElementById('task-details').value = event.extendedProps.details || '';
        showPopup();
    }

    function showPopup() {
        document.querySelector('.popup-overlay').style.display = 'block';
        document.querySelector('.task-popup').style.display = 'block';
    }

    window.closeTaskPopup = function() {
        document.querySelector('.popup-overlay').style.display = 'none';
        document.querySelector('.task-popup').style.display = 'none';
    };

    window.saveTask = async function() {
        const taskData = {
            name: document.getElementById('task-name').value,
            deadline: document.getElementById('task-deadline').value,
            priority: parseInt(document.getElementById('task-priority').value),
            duration: parseFloat(document.getElementById('task-duration').value),
            details: document.getElementById('task-details').value
        };

        try {
            let url = '/api/tasks';
            let method = 'POST';

            if (currentTaskId) {
                url += `/${currentTaskId}`;
                method = 'PUT';
            }

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(taskData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to save task');
            }

            await response.json();
            calendar.refetchEvents(); // Refresh the calendar
            closeTaskPopup();
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        }
    };

    window.removeTask = async function() {
        if (!currentTaskId) return;

        try {
            const response = await fetch(`/api/tasks/${currentTaskId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to delete task');
            }

            calendar.refetchEvents(); // Refresh the calendar
            closeTaskPopup();
        } catch (error) {
            console.error('Error:', error);
            alert(error.message);
        }
    };

    // Close popup when clicking overlay
    document.querySelector('.popup-overlay').addEventListener('click', function(e) {
        if (e.target === this) {
            closeTaskPopup();
        }
    });
});
